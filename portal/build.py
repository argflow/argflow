#!/usr/bin/env python3

import argparse
import glob
import os
import shutil
import subprocess


def pip(args):
    subprocess.run(["pip"] + args.split())


def npm(args, cwd):
    subprocess.run(["npm"] + args.split(), cwd=cwd)


def flake8(args):
    subprocess.run(["flake8"] + args.split())


def pytest(args):
    subprocess.run(["pytest"] + args.split())


def python(args):
    subprocess.run(["python3"] + args.split())


def rm(file):
    files = glob.glob(file)

    for file in files:
        if os.path.isdir(file):
            shutil.rmtree(file)

        if os.path.isfile(file):
            os.remove(file)


def copytree(src, dest):
    shutil.copytree(src, dest, dirs_exist_ok=True)


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True, title="commands")

    subparsers.add_parser("clean")
    subparsers.add_parser("lint")
    subparsers.add_parser("test")

    bootstrap = subparsers.add_parser("bootstrap")
    bootstrap.add_argument("--python-only", action="store_true")

    build = subparsers.add_parser("build")
    build.add_argument("target", nargs="?", default="all")

    return parser.parse_args()


def bootstrap_server():
    # Install dependencies
    pip("install -r requirements.txt")
    pip("install -r requirements.dev.txt")

    # Install project in editable mode
    pip("install -e argflow")
    pip("install -e .")


def build_server():
    python("setup.py sdist bdist_wheel")


def build_client():
    # Install dependencies and build the app
    npm("install", "client")
    npm("run build", "client")

    # Copy build output into python package
    copytree("client/build", "argflow_ui/client")


def build_visualisers():
    npm("install", "visualisers")
    npm("run build", "visualisers")


def build(target):
    if target == "all":
        bootstrap_server()
        build_client()
        build_visualisers()
        build_server()

    elif target == "server":
        build_server()

    elif target == "client":
        build_client()

    elif target == "visualisers":
        build_visualisers()

    else:
        print(f"invalid target: {target}")
        exit(1)


def main():
    args = parse_args()

    if args.command == "clean":
        rm("build")
        rm("dist")
        rm("*.egg-info")

    if args.command == "bootstrap":
        bootstrap_server()

        if not args.python_only:
            build_client()
            build_visualisers()

    if args.command == "lint":
        flake8("argflow_ui tests")

    if args.command == "test":
        pytest("tests")

    if args.command == "build":
        build(args.target)


if __name__ == "__main__":
    main()
