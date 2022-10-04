# eStargz images

:information_source: Available images: https://github.com/orgs/stargz-containers/packages

A repository to convert an existing image to eStargz image.

At every commit on master, images are converted to eStargz and pushed to [`ghcr.io/stargz-containers`](https://github.com/orgs/stargz-containers/packages) namespace. 

You can then use those eStargz images like so

```bash
nerdctl --snapshotter=stargz run -it ghcr.io/stargz-containers/python:3.9-esgz
```

The original image is `python:3.9`
A copy of the original image (`ghcr.io/stargz-containers/python:3.9-org`) is also pushed for benchmarking purposes.

If you want to add an image to the list of images available for conversion, please make a pull request to add the public image to [`list_of_images_to_optimize.py`](./list_of_images_to_optimize.py).

## About project

This project started based on the discussion in https://github.com/containerd/stargz-snapshotter/issues/715 .
@gabrieldemarmiesse contributed the original version as https://github.com/gabrieldemarmiesse/estargz-images and this repository is based on it.
