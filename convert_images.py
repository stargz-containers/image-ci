import json
import platform
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from list_of_images_to_optimize import Image, images_to_optimize

CONVERTED_IMAGES_PREFIX = "ghcr.io/stargz-containers"
NUMBER_OF_THREADS = 1
PUSH = "--push" in sys.argv
MERGE = "--merge" in sys.argv
ARCH = "" if MERGE else f"-{platform.machine()}"
ARCHS = ["x86_64", "aarch64"]


def run(args: list):
    print("--> Executing: ", " ".join(args))
    subprocess.check_call(args)


def split_registry_domain(image_name: str) -> tuple:
    """We split an image name into (registry domain, remote name).

    This follows splitDockerDomain of github.com/distribution/reference.
    See also: https://github.com/distribution/reference/blob/0965666a6ade2e06035fe352e38344be1e68951a/normalize.go#L143-L191
    """
    first, sep, rest = image_name.partition("/")
    if not sep:
        return "docker.io", "library/" + image_name
    if first == "localhost":
        domain, remote_name = first, rest
    elif first == "index.docker.io":
        domain, remote_name = "docker.io", rest
    elif "." in first or ":" in first or first.lower() != first:
        domain, remote_name = first, rest
    else:
        domain, remote_name = "docker.io", image_name
    if domain == "docker.io" and "/" not in remote_name:
        remote_name = "library/" + remote_name
    return domain, remote_name


def get_normalized_image_name(docker_image_name: str) -> str:
    """We add docker.io/library/ if necessary.

    References that already include a registry domain (e.g. ghcr.io/foo/bar:tag)
    are kept as they are.
    """
    domain, remote_name = split_registry_domain(docker_image_name)
    return f"{domain}/{remote_name}"


def get_image_name_without_registry(image_name: str) -> str:
    """We remove the registry domain (e.g. ghcr.io/) if present.

    For docker.io images we also remove "library/", like Docker's familiar
    names, so "alpine:3" and "docker.io/library/alpine:3" give "alpine:3".
    """
    domain, remote_name = split_registry_domain(image_name)
    if domain == "docker.io" and remote_name.startswith("library/"):
        familiar_name = remote_name[len("library/"):]
        if "/" not in familiar_name:
            return familiar_name
    return remote_name


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
                "--period=30",
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
        src_image_name = get_normalized_image_name(self.src_image.name)
        run(["nerdctl", "pull", "-q", src_image_name])
        self.convert()

        if PUSH:
            # we might need to sleep a bit to make sure the image is available for push
            # I'm not sure if this is needed, but we had some flakyness in the
            # push step in the CI, so it's what I tried.
            time.sleep(5)
            run(["nerdctl", "push", self.converted_image_name])
            print(f"--> Pushed {self.converted_image_name} to registry")

        run(["nerdctl", "rmi", self.src_image.name, self.converted_image_name])

class OriginalConversionJob(ConversionJob):
    @property
    def converted_image_name(self) -> str:
        return f"{CONVERTED_IMAGES_PREFIX}/{get_image_name_without_registry(self.src_image.name)}-org"

    def source_is_index(self) -> bool:
        src_image_name = get_normalized_image_name(self.src_image.name)
        manifest = json.loads(subprocess.check_output(["crane", "manifest", src_image_name]))
        return "manifests" in manifest

    def pull_convert_and_push(self):
        src_image_name = get_normalized_image_name(self.src_image.name)
        if self.source_is_index():
            run(
                [
                    "crane",
                    "index",
                    "filter",
                    src_image_name,
                    "--platform",
                    "linux/amd64",
                    "--platform",
                    "linux/arm64",
                    "-t",
                    self.converted_image_name,
                ]
            )
        else:
            # crane index filter fails on single-platform images
            run(["crane", "copy", src_image_name, self.converted_image_name])
        print(f"--> Pushed {self.converted_image_name} to registry")


class StargzConversionJob(ConversionJob):
    @property
    def converted_image_name(self) -> str:
        return f"{CONVERTED_IMAGES_PREFIX}/{get_image_name_without_registry(self.src_image.name)}-esgz-noopt{ARCH}"

    def convert(self):
        self.ctr_remote_image_optimize(optimize=False)


class EStargzConversionJob(ConversionJob):
    @property
    def converted_image_name(self) -> str:
        return f"{CONVERTED_IMAGES_PREFIX}/{get_image_name_without_registry(self.src_image.name)}-esgz{ARCH}"

    def convert(self):
        self.ctr_remote_image_optimize()


class EStargzZstdchunkedConversionJob(ConversionJob):
    @property
    def converted_image_name(self) -> str:
        return f"{CONVERTED_IMAGES_PREFIX}/{get_image_name_without_registry(self.src_image.name)}-zstdchunked{ARCH}"

    def convert(self):
        self.ctr_remote_image_optimize(zstdchunked=True)


def check_converted_image_name_collisions(images: list):
    """We fail if two images from different registries would get the same converted name"""
    sources_by_name = {}
    for image in images:
        name = get_image_name_without_registry(image.name)
        source = get_normalized_image_name(image.name)
        if name in sources_by_name and sources_by_name[name] != source:
            raise ValueError(
                f"Images {sources_by_name[name]} and {source} would both be "
                f"converted to {CONVERTED_IMAGES_PREFIX}/{name}"
            )
        sources_by_name[name] = source


def main():
    check_converted_image_name_collisions(images_to_optimize)

    conversion_jobs = []

    for image_and_args in images_to_optimize:
        if PUSH:
            # this is just transferring layers. If we don't have permission to push,
            # we can't do it.
            if platform.machine() == "x86_64":
                conversion_jobs.append(OriginalConversionJob(image_and_args))
        if image_and_args.copy_only:
            # Without --push nothing is copied, so we only check the source exists.
            if not PUSH and not MERGE:
                run(["crane", "digest", get_normalized_image_name(image_and_args.name)])
            continue
        conversion_jobs += [
            StargzConversionJob(image_and_args),
            EStargzConversionJob(image_and_args),
            EStargzZstdchunkedConversionJob(image_and_args),
        ]

    if MERGE:
        for job in conversion_jobs:
            arch_args = []
            for arch in ARCHS:
                arch_args += ["-m", f"{job.converted_image_name}-{arch}"]
            run(["crane", "index", "append", "-t", job.converted_image_name] + arch_args)
    elif NUMBER_OF_THREADS == 1:
        for job in conversion_jobs:
            job.pull_convert_and_push_if_necessary()
    else:
        with ThreadPoolExecutor(max_workers=NUMBER_OF_THREADS) as pool:
            pool.map(ConversionJob.pull_convert_and_push_if_necessary, conversion_jobs)
    print("--> All done!")


if __name__ == "__main__":
    main()
