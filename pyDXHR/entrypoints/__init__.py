import argparse
import sys


def bigfile():
    parser = argparse.ArgumentParser(
        prog="pyDXHR Bigfile utilities",
    )

    parser.add_argument(
        "command",
        metavar="command",
        type=str,
        help="Command to run. Valid values: [unpack, repack, extract]",
    )

    args = parser.parse_args()

    if args.command not in ("unpack", "repack", "extract"):
        print("Invalid command. Valid values: [unpack, repack, extract]. Exiting...")
        sys.exit(1)


def drm():
    parser = argparse.ArgumentParser(
        prog="pyDXHR DRM utilities",
    )

    parser.add_argument(
        "command",
        metavar="command",
        type=str,
        description="Command to run. Valid values: [unpack, repack]",
    )

    args = parser.parse_args()

    print(args)


def export():
    parser = argparse.ArgumentParser(
        prog="pyDXHR exporters",
    )

    parser.add_argument(
        "command",
        metavar="command",
        type=str,
        description="Command to run. Valid values: [gltf, material, texture, usm, cfx]",
    )

    args = parser.parse_args()

    print(args)
