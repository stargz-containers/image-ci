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
    Image("alpine:3.15.3", ["sh", "-c", "echo hello world"]),
    Image("nixos/nix:2.3.12", ["sh", "-c", "echo hello world"]),
    Image("fedora:35", ["sh", "-c", "echo hello world"]),
    Image("rethinkdb:2.4.1"),
    # doesn't work:
    # Error: failed to copy image: PUT https://index.docker.io/v2/.../glassfish/manifests/4.1-jdk8-org:
    # DENIED: unknown manifest class for application/octet-stream
    # Image("glassfish:4.1-jdk8"),
    Image("drupal:9.3.9"),
    Image("jenkins:2.60.3"),
    Image("redis:6.2.6"),
    Image("tomcat:10.1.0-jdk17-openjdk-bullseye"),
    Image("postgres:14.2", env={"POSTGRES_PASSWORD": "abc"}),
    Image("mariadb:10.7.3", env={"MYSQL_ROOT_PASSWORD": "abc"}),
    Image("wordpress:5.9.2"),
    Image("php:8.1.4-apache-bullseye"),
    Image("rabbitmq:3.9.14"),
    Image(
        "elasticsearch:8.1.1",
        mount=[
            (
                "mounts/elasticsearch/elasticsearch.yml",
                "/usr/share/elasticsearch/config/elasticsearch.yml",
            )
        ],
    ),
    Image("php:8.1.4", ["php", "-r", 'echo "hello world\\n";']),
    Image(
        "gcc:11.2.0",
        ["sh", "-c", "cd /src; gcc main.c; ./a.out; exit\n"],
        mount=[("mounts/gcc", "/src")],
    ),
    Image('golang:1.18', ["sh", "-c", 'cd /go/src; go run main.go; exit\n'], mount=[('mounts/go', '/go/src')]),
    Image("jruby:9.3.4", ["jruby", "-e", "puts 'hello'; exit\n"]),
    Image("r-base:4.1.3", ["R", "--no-save", "-e", 'sprintf("hello")']),
    Image("perl:5.34.1", ['perl',  "-e", 'print("hello")']),
    # python images
    Image("python:3.7-slim", ["python", "-c", "print('hello world')"]),
    Image("python:3.7", ["python", "-c", "print('hello world')"]),
    Image("python:3.8", ["python", "-c", "print('hello world')"]),
    Image("python:3.9", ["python", "-c", "print('hello world')"]),
    Image("python:3.10", ["python", "-c", "print('hello world')"]),
    Image("python:3.10-slim", ["python", "-c", "print('hello world')"]),
    Image("python:3.11.0rc2", ["python", "-c", "print('hello world')"]),
    Image("pypy:3.9", ["pypy3", "-c", "print('hello world')"]),
    Image("node:17.8.0", ["node", "-e", 'console.log("hello")'])
]
