"""
The first element is the docker image name
the second element is optional and is the workload to optimize for.

If the workload is not specified, the default entrypoint and arguments
of the image are used.

If the docker image needs some environment variables or mounts to boot,
you can set those as the argument of the Image() class.
You can take postgres as an example for the env and
elasticsearch as example for the mount.
"""

from image_class import Image

images_to_optimize = [
    Image("alpine:3.24.3", ["sh", "-c", "echo hello world"]),
    Image("nixos/nix:2.35.4", ["sh", "-c", "echo hello world"]),
    Image("fedora:45", ["sh", "-c", "echo hello world"]),
    Image("ubuntu:26.04", ["sh", "-c", "echo hello world"]),
    Image("rethinkdb:2.4.3"),
    # doesn't work:
    # Error: failed to copy image: PUT https://index.docker.io/v2/.../glassfish/manifests/4.1-jdk8-org:
    # DENIED: unknown manifest class for application/octet-stream
    # Image("glassfish:4.1-jdk8"),
    Image("drupal:11.3.20"),
    Image("jenkins/jenkins:2.587"),
    Image("redis:8.10.2"),
    Image("tomcat:11.0.27-jdk25-temurin-noble"),
    Image("postgres:18.6", env={"POSTGRES_PASSWORD": "abc"}),
    Image("mariadb:13.0.2", env={"MYSQL_ROOT_PASSWORD": "abc"}),
    Image("wordpress:7.1.3"),
    Image("fluent/fluentd:v1.19-debian-2"),
    Image("php:8.3.36-apache-trixie"),
    # FIXME: Device or resource busy
    # Image(
    #     "elasticsearch:8.1.1",
    #     mount=[
    #         (
    #             "mounts/elasticsearch/elasticsearch.yml",
    #             "/usr/share/elasticsearch/config/elasticsearch.yml",
    #         )
    #     ],
    # ),
    Image("php:8.3.36", ["php", "-r", 'echo "hello world\\n";']),
    Image(
        "gcc:16.2.0",
        ["sh", "-c", "cd /src; gcc -o /a.out main.c; /a.out; exit\n"],
        mount=[("mounts/gcc", "/src")],
    ),
    Image('golang:1.27', ["sh", "-c", 'cd /go/src; go run main.go; exit\n'], mount=[('mounts/go', '/go/src')]),
    Image("jruby:10.1.2", ["jruby", "-e", "puts 'hello'; exit\n"]),
    Image("r-base:4.6.1", ["R", "--no-save", "-e", 'sprintf("hello")']),
    Image("perl:5.44.0", ['perl',  "-e", 'print("hello")']),
    # python images
    Image("python:3.15-slim", ["python", "-c", "print('hello world')"]),
    Image("python:3.15", ["python", "-c", "print('hello world')"]),
    Image("pypy:3.12", ["pypy3", "-c", "print('hello world')"]),
    Image("node:26.12.1", ["node", "-e", 'console.log("hello")'])
]
