"""Build a 3x3 cube MJCF."""

import itertools
from typing import Sequence
from dm_control import mjcf
from mujoco import viewer
from pathlib import Path
from lxml import etree
import re


SAVE_DIR = Path(__file__).parent
NAME = "Cube 3x3x3"
XML_NAME = "cube_3x3x3.xml"
PRECISION = 6
ZERO_THRESHOLD = 1e-6
ADD_ACTUATORS = True


def build() -> mjcf.RootElement:
    root = mjcf.RootElement()
    root.model = NAME

    # ================================ #
    # Constants.
    # ================================ #
    cube_mass = 0.0685  # Total mass of the cube in kg.
    cubelet_dimension = 0.019  # Dimension of a cubelet in m.
    # Vertices obtained via `process_mesh.py`.
    cubelet_vertices = """
        0.008075 0.0095 -0.008075
        -0.008075 0.0095 -0.008075
        0.008075 0.0095 0.008075
        -0.008075 0.0095 0.008075
        -0.0095 0.008075 -0.008075
        -0.0095 -0.008075 -0.008075
        -0.0095 0.008075 0.008075
        -0.0095 -0.008075 0.008075
        0.008075 -0.0095 -0.008075
        0.008075 -0.0095 0.008075
        -0.008075 -0.0095 -0.008075
        -0.008075 -0.0095 0.008075
        0.0095 0.008075 0.008075
        0.0095 -0.008075 0.008075
        0.0095 0.008075 -0.008075
        0.0095 -0.008075 -0.008075
        0.008075 0.008075 0.0095
        -0.008075 0.008075 0.0095
        0.008075 -0.008075 0.0095
        -0.008075 -0.008075 0.0095
        0.008075 -0.008075 -0.0095
        -0.008075 -0.008075 -0.0095
        0.008075 0.008075 -0.0095
        -0.008075 0.008075 -0.0095
    """
    axes = ("pX", "nX", "pY", "nY", "pZ", "nZ")  # +/- axis directions.
    # ================================ #

    # ================================ #
    # Compiler settings.
    # ================================ #
    root.compiler.autolimits = True
    root.compiler.angle = "radian"
    root.compiler.texturedir = "assets"
    # ================================ #

    # ================================ #
    # Memory settings.
    # ================================ #
    root.size.memory = "600K"
    # ================================ #

    # ================================ #
    # Option settings.
    # ================================ #
    root.option.timestep = 0.01
    root.option.integrator = "implicitfast"
    # ================================ #

    # ================================ #
    # Rendering settings.
    # ================================ #
    root.visual.headlight.diffuse = (0.6, 0.6, 0.6)
    root.visual.headlight.ambient = (0.3, 0.3, 0.3)
    root.visual.headlight.specular = (0, 0, 0)
    getattr(root.visual, "global").azimuth = 180
    getattr(root.visual, "global").elevation = -20
    root.statistic.extent = 0.1
    root.statistic.meansize = 0.0087
    # ================================ #

    # ================================ #
    # Defaults.
    # ================================ #
    root.default.geom.mass = cube_mass / 27
    cubelet_default = root.default.add("default", dclass="cubelet")
    cubelet_default.geom.type = "mesh"
    cubelet_default.geom.mesh = "cubelet"
    cubelet_default.geom.condim = 1
    cubelet_default.joint.type = "ball"
    cubelet_default.joint.armature = 1e-4
    cubelet_default.joint.damping = 5e-4
    cubelet_default.joint.frictionloss = 1e-3
    if ADD_ACTUATORS:
        root.default.motor.ctrlrange = (-0.05, 0.05)
    core_default = root.default.add("default", dclass="core")
    core_default.geom.type = "sphere"
    core_default.geom.size = (0.01,)
    core_default.geom.contype = 0
    core_default.geom.conaffinity = 0
    core_default.geom.group = "4"
    # ================================ #

    # ================================ #
    # Assets.
    # ================================ #
    root.asset.add("mesh", name="cubelet", vertex=cubelet_vertices)
    root.asset.add("texture", type="skybox", builtin="gradient", height=512, width=512)

    color2dir = {
        "white": "pZ",
        "yellow": "nZ",
        "red": "pX",
        "orange": "nX",
        "blue": "pY",
        "green": "nY",
    }
    dir2color = {v: k for k, v in color2dir.items()}
    dir2face = {
        "pX": "D",
        "nX": "U",
        "pY": "R",
        "nY": "L",
        "pZ": "F",
        "nZ": "B",
    }

    for color in color2dir:
        root.asset.add(
            "texture",
            file=f"{color}.png",
            gridsize="3 4",
            gridlayout=f".....{dir2face[color2dir[color]]}......",
            rgb1=(0, 0, 0),
        )
        root.asset.add("material", name=color, texture=color)

    for color1, color2 in itertools.combinations(color2dir.keys(), 2):
        color1, color2 = sorted([color1, color2])
        if color1 == "white" and color2 == "yellow":
            continue
        if color1 == "red" and color2 == "orange":
            continue
        if color1 == "blue" and color2 == "green":
            continue
        root.asset.add(
            "texture",
            file=f"{color1}_{color2}.png",
            gridsize="3 4",
            gridlayout=f".....{dir2face[color2dir[color1]]}{dir2face[color2dir[color2]]}.....",
            rgb1=(0, 0, 0),
        )
        root.asset.add(
            "material", name=f"{color1}_{color2}", texture=f"{color1}_{color2}"
        )

    for comb in itertools.combinations(color2dir.keys(), 3):
        if "white" in comb and "yellow" in comb:
            continue
        if "red" in comb and "orange" in comb:
            continue
        if "blue" in comb and "green" in comb:
            continue
        color1, color2, color3 = sorted(comb)
        root.asset.add(
            "texture",
            file=f"{color1}_{color2}_{color3}.png",
            gridsize="3 4",
            gridlayout=f".....{dir2face[color2dir[color1]]}{dir2face[color2dir[color2]]}{dir2face[color2dir[color3]]}....",
            rgb1=(0, 0, 0),
        )
        root.asset.add(
            "material",
            name=f"{color1}_{color2}_{color3}",
            texture=f"{color1}_{color2}_{color3}",
        )
    # ================================ #

    def dir2axis(d: str) -> Sequence[float]:
        s = -1 if d[0] == "n" else 1
        if d[1] == "X":
            return (s, 0, 0)
        elif d[1] == "Y":
            return (0, s, 0)
        elif d[1] == "Z":
            return (0, 0, s)
        else:
            raise ValueError(f"Invalid direction: {d}")

    def dir2pos(ds: str) -> Sequence[float]:
        p = [0.0] * 3
        for d in ds.split("_"):
            p = [p[i] + cubelet_dimension * a for i, a in enumerate(dir2axis(d))]
        return tuple(p)

    # ================================ #
    # Worldbody.
    # ================================ #
    root.worldbody.add("light", pos=(0, 0, 1))

    core = root.worldbody.add("body", name="core", childclass="cubelet")
    core.add("geom", dclass="core")

    # Center cubelets: 6.
    for d in axes:
        body = core.add("body", name=d)
        body.add("joint", name=d, type="hinge", axis=dir2axis(d))
        if ADD_ACTUATORS:
            root.actuator.add("motor", name=dir2color[d], joint=d)
        body.add("geom", name=f"cubelet_{d}", material=dir2color[d], pos=dir2pos(d))

    # Edge cubelets: 6C2 - 3 = 12.
    for d1, d2 in list(itertools.combinations(axes, 2)):
        if d1[1] == d2[1]:
            continue
        d = "_".join(sorted([d1, d2]))
        body = core.add("body", name=d)
        body.add("joint", name=d)
        mat = "_".join(sorted([dir2color[d1], dir2color[d2]]))
        body.add("geom", name=f"cubelet_{d}", material=mat, pos=dir2pos(d))

    # Corner cubelets: 4*2=8.
    for d1, d2, d3 in list(itertools.combinations(axes, 3)):
        if d1[1] == d2[1] or d1[1] == d3[1] or d2[1] == d3[1]:
            continue
        d = "_".join(sorted([d1, d2, d3]))
        body = core.add("body", name=d)
        body.add("joint", name=d)
        mat = "_".join(sorted([dir2color[d1], dir2color[d2], dir2color[d3]]))
        body.add("geom", name=f"cubelet_{d}", material=mat, pos=dir2pos(d))
    # ================================ #

    return root


def prettify_xml_string(xml_string: str) -> str:
    root = etree.XML(xml_string, etree.XMLParser(remove_blank_text=True))

    compiler = root.find("compiler")
    compiler.set("texturedir", "assets")

    # Replace nasty filepaths.
    pattern = r"^[a-zA-Z]+(_[a-zA-Z]+)*-\w+\.png"
    textures = root.findall(".//texture")
    for texture in textures:
        for attr, file_name in texture.attrib.items():
            match = re.match(pattern, file_name)
            if match:
                color = match.group(0).split("-")[0]
                texture.set(attr, f"{color}.png")
        # Remove autogenerated texture names.
        if "name" in texture.attrib:
            texture.attrib.pop("name")

    # Remove autogenerated names.
    for light in root.findall(".//light"):
        light.attrib.pop("name")
    for geom in root.findall(".//geom"):
        if "name" in geom.attrib:
            geom.attrib.pop("name")

    # Remove "/" default class.
    default_elem = root.find("default").find(".//*[@class='/']")
    for child in default_elem.iterchildren():
        default_elem.getparent().append(child)
    default_elem.getparent().remove(default_elem)

    # Reorder asset elements: textures first, then materials, then meshes.
    asset = root.find("asset")
    textures = asset.findall(".//texture")
    materials = asset.findall(".//material")
    meshes = asset.findall(".//mesh")
    asset.clear()
    for texture in textures:
        asset.append(texture)
    for material in materials:
        asset.append(material)
    for mesh in meshes:
        asset.append(mesh)

    # TODO(kevin): Figure out how to add line breaks between sections.

    return etree.tostring(root, pretty_print=True).replace(b' class="/"', b"").decode()


def main() -> None:
    model = build()
    xml_string = model.to_xml_string(precision=PRECISION, zero_threshold=ZERO_THRESHOLD)
    pretty_xml_string = prettify_xml_string(xml_string)

    with open(SAVE_DIR / XML_NAME, "w") as f:
        f.write(pretty_xml_string)

    viewer.launch_from_path(str(SAVE_DIR / XML_NAME))


if __name__ == "__main__":
    main()
