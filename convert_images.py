import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from list_of_images_to_optimize import Image, images_to_optimize

CONVERTED_IMAGES_PREFIX = "ghcr.io/gabrieldemarmiesse/estargz-images"
NUMBER_OF_THREADS = 1
PUSH = "--push" in sys.argv


def run(args: list):
    print("--> Executing: ", " ".join(args))
    subprocess.check_call(args)


def get_normalized_image_name(docker_image_name: str) -> str:
    """We add docker.io/library/ if necessary"""
    if "/" not in docker_image_name:
        return "docker.io/library/" + docker_image_name
    else:
        return "docker.io/" + docker_image_name


class ConversionJob:
    def __init__(self, src_image: Image):
        self.src_image = src_image

    def ctr_remote_image_optimize(
        self, optimize: bool = True, zstdchunked: bool = False
    ):
        src_image_name = get_normalized_image_name(self.src_image.name)

        additional_options = []
        if self.src_image.entrypoint is not None:
            additional_options += [
                "--entrypoint",
                json.dumps(self.src_image.entrypoint),
            ]

        for mount_src, mount_dst in self.src_image.mount:
            mount_src = (Path(__file__).parent / mount_src).absolute()
            additional_options += [
                "--mount",
                f"type=bind,src={mount_src},dst={mount_dst},options=rbind",
            ]

        for env_name, env_value in self.src_image.env.items():
            additional_options += ["--env", f"{env_name}={env_value}"]

        if not optimize:
            additional_options.append("--no-optimize")
        if zstdchunked:
            additional_options.append("--zstdchunked")

        run(
            [
                "ctr-remote",
                "image",
                "optimize",
                "--oci",
            ]
            + additional_options
            + [
                src_image_name,
                self.converted_image_name,
            ]
        )

    @property
    def converted_image_name(self) -> str:
        raise NotImplementedError("You need to subclass and implement this method")

    def convert(self):
        raise NotImplementedError("You need to subclass and implement this method")

    def job_was_already_done(self) -> bool:
        """We check if the docker image already exists"""
        try:
            run(["crane", "digest", self.converted_image_name])
            return True
        except subprocess.CalledProcessError:
            return False

    def pull_convert_and_push_if_necessary(self):
        if self.job_was_already_done():
            print(f"--> Image {self.converted_image_name} is already in the registry")
            return
        print(f"--> Image {self.converted_image_name} not in registry, converting...")
        self.pull_convert_and_push()

    def pull_convert_and_push(self):
        run(["nerdctl", "pull", "-q", self.src_image.name])
        self.convert()

        if PUSH:
            # we might need to sleep a bit to make sure the image is available for push
            # I'm not sure if this is needed, but we had some flakyness in the
            # push step in the CI, so it's what I tried.
            time.sleep(5)
            run(["nerdctl", "push", self.converted_image_name])
            print(f"--> Pushed {self.converted_image_name} to registry")


class OriginalConversionJob(ConversionJob):
    @property
    def converted_image_name(self) -> str:
        return f"{CONVERTED_IMAGES_PREFIX}/{self.src_image.name}-org"

    def pull_convert_and_push(self):
        run(
            [
                "crane",
                "copy",
                "--platform",
                "linux/amd64",
                self.src_image.name,
                self.converted_image_name,
            ]
        )
        print(f"--> Pushed {self.converted_image_name} to registry")


class StargzConversionJob(ConversionJob):
    @property
    def converted_image_name(self) -> str:
        return f"{CONVERTED_IMAGES_PREFIX}/{self.src_image.name}-esgz-noopt"

    def convert(self):
        self.ctr_remote_image_optimize(optimize=False)


class EStargzConversionJob(ConversionJob):
    @property
    def converted_image_name(self) -> str:
        return f"{CONVERTED_IMAGES_PREFIX}/{self.src_image.name}-esgz"

    def convert(self):
        self.ctr_remote_image_optimize()


class EStargzZstdchunkedConversionJob(ConversionJob):
    @property
    def converted_image_name(self) -> str:
        return f"{CONVERTED_IMAGES_PREFIX}/{self.src_image.name}-zstdchunked"

    def convert(self):
        self.ctr_remote_image_optimize(zstdchunked=True)


def main():
    conversion_jobs = []

    for image_and_args in images_to_optimize:
        if PUSH:
            # this is just transferring layers. If we don't have permission to push,
            # we can't do it.
            conversion_jobs.append(OriginalConversionJob(image_and_args))
        conversion_jobs += [
            StargzConversionJob(image_and_args),
            EStargzConversionJob(image_and_args),
            EStargzZstdchunkedConversionJob(image_and_args),
        ]

    if NUMBER_OF_THREADS == 1:
        for job in conversion_jobs:
            job.pull_convert_and_push_if_necessary()
    else:
        with ThreadPoolExecutor(max_workers=NUMBER_OF_THREADS) as pool:
            pool.map(ConversionJob.pull_convert_and_push_if_necessary, conversion_jobs)
    print("--> All done!")


if __name__ == "__main__":
    main()
