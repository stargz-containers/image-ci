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
    Image("alpine:3.21.2", ["sh", "-c", "echo hello world"]),
    Image("nixos/nix:2.26.1", ["sh", "-c", "echo hello world"]),
    Image("fedora:41", ["sh", "-c", "echo hello world"]),
    Image("rethinkdb:2.4.3"),
    # doesn't work:
    # Error: failed to copy image: PUT https://index.docker.io/v2/.../glassfish/manifests/4.1-jdk8-org:
    # DENIED: unknown manifest class for application/octet-stream
    # Image("glassfish:4.1-jdk8"),
    Image("drupal:11.1.1"),
    Image("jenkins/jenkins:2.492"),
    Image("redis:7.4.2"),
    Image("tomcat:11.0.2-jdk21-temurin-noble"),
    Image("postgres:17.2", env={"POSTGRES_PASSWORD": "abc"}),
    Image("mariadb:11.6.2", env={"MYSQL_ROOT_PASSWORD": "abc"}),
    Image("wordpress:6.7.1"),
    Image("fluent/fluentd:v1.18-1"),
    Image("fluent/fluentd:v1.18-debian-arm64-1"),
    Image("php:8.2.27-apache-bookworm"),
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
    Image("php:8.2.27", ["php", "-r", 'echo "hello world\\n";']),
    Image(
        "gcc:14.2.0",
        ["sh", "-c", "cd /src; gcc -o /a.out main.c; /a.out; exit\n"],
        mount=[("mounts/gcc", "/src")],
    ),
    Image('golang:1.23', ["sh", "-c", 'cd /go/src; go run main.go; exit\n'], mount=[('mounts/go', '/go/src')]),
    Image("jruby:9.4.11", ["jruby", "-e", "puts 'hello'; exit\n"]),
    Image("r-base:4.4.2", ["R", "--no-save", "-e", 'sprintf("hello")']),
    Image("perl:5.40.1", ['perl',  "-e", 'print("hello")']),
    # python images
    Image("python:3.13-slim", ["python", "-c", "print('hello world')"]),
    Image("python:3.13", ["python", "-c", "print('hello world')"]),
    Image("pypy:3.10", ["pypy3", "-c", "print('hello world')"]),
    Image("node:23.7.0", ["node", "-e", 'console.log("hello")'])
]
