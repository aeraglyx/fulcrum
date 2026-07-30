import re
import math
import sys
import subprocess
import os
import tomllib

import bpy


def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.Popen([opener, filename])


def get_addon_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_manifest():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, "blender_manifest.toml")
    with open(filepath, "rb") as f:
        manifest = tomllib.load(f)
    return manifest


def get_addon_version():
    return get_manifest()["version"]


def oklab_2_srgb(l, a, b):
    # https://bottosson.github.io/posts/oklab/

    x = l + 0.3963377774 * a + 0.2158037573 * b
    y = l - 0.1055613458 * a - 0.0638541728 * b
    z = l - 0.0894841775 * a - 1.2914855480 * b

    x = x * x * x
    y = y * y * y
    z = z * z * z

    return [
        +4.0767416621 * x - 3.3077115913 * y + 0.2309699292 * z,
        -1.2684380046 * x + 2.6097574011 * y - 0.3413193965 * z,
        -0.0041960863 * x - 0.7034186147 * y + 1.7076147010 * z,
    ]


def oklab_hsl_2_srgb(h, s, l):
    """HSL but based on Oklab, so better :)"""
    # https://bottosson.github.io/posts/oklab/

    a = s * math.cos(h * math.tau)
    b = s * math.sin(h * math.tau)

    return oklab_2_srgb(l, a, b)


def version_up(name, i=1):
    # if it doesn't have a version, add it
    if not name[-1].isdigit():
        return name + "_v02"  # v001 or v002 ?
    # otherwise increment by 1
    old_name = re.sub(r"(?<=v|V)\d+$", "", name)
    old_v = re.search(r"(?<=v|V)\d+$", name).group()
    new_v = str(int(old_v) + i).zfill(len(old_v))
    return old_name + new_v
    # TODO test it
