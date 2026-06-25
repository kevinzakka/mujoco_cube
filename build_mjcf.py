"""Build a 3x3 cube MJCF using the MuJoCo spec (MjSpec) API."""

import itertools
from pathlib import Path
from typing import Iterator, Mapping, Sequence

import mujoco
from mujoco import viewer

from cubelet_mesh import build_cubelet_mesh

SAVE_DIR = Path(__file__).parent
NAME = "Cube 3x3x3"
XML_NAME = "cube_3x3x3.xml"

CUBE_MASS = 0.0685  # Total mass of the cube in kg.
CUBELET_DIMENSION = 0.019  # Distance between adjacent cubelet centers in m.

# Sticker color on each cubelet face, keyed by axis direction.
DIR2COLOR = {
    "pX": "red", "nX": "orange",
    "pY": "blue", "nY": "green",
    "pZ": "white", "nZ": "yellow",
}


def dir2axis(d: str) -> Sequence[float]:
    s = -1 if d[0] == "n" else 1
    return tuple(s if d[1] == ax else 0 for ax in "XYZ")


def dir2pos(dirs: Sequence[str]) -> Sequence[float]:
    return tuple(sum(CUBELET_DIMENSION * dir2axis(d)[i] for d in dirs) for i in range(3))


def cubelets() -> Iterator[tuple[str, ...]]:
    """Yield every cubelet as a tuple of face directions: 6 centers, 12 edges, 8 corners."""
    for n in (1, 2, 3):
        for axes in itertools.combinations("XYZ", n):
            for signs in itertools.product("pn", repeat=n):
                yield tuple(sorted(s + ax for s, ax in zip(signs, axes)))


def build() -> mujoco.MjSpec:
    spec = mujoco.MjSpec()
    spec.modelname = NAME
    spec.memory = 600 * 1024

    spec.compiler.degree = False  # Radians.
    spec.compiler.texturedir = "assets"
    spec.option.timestep = 0.01
    spec.option.integrator = mujoco.mjtIntegrator.mjINT_IMPLICITFAST

    spec.visual.headlight.diffuse = [0.6, 0.6, 0.6]
    spec.visual.headlight.ambient = [0.3, 0.3, 0.3]
    spec.visual.headlight.specular = [0, 0, 0]
    spec.visual.global_.azimuth = 180
    spec.visual.global_.elevation = -20
    spec.stat.extent = 0.1
    spec.stat.meansize = 0.0087

    # Defaults.
    spec.default.geom.mass = CUBE_MASS / 27
    spec.default.actuator.ctrlrange = [-0.05, 0.05]
    cubelet = spec.add_default("cubelet", spec.default)
    cubelet.geom.type = mujoco.mjtGeom.mjGEOM_MESH
    cubelet.geom.material = "sticker"
    cubelet.geom.condim = 1
    cubelet.joint.type = mujoco.mjtJoint.mjJNT_BALL
    cubelet.joint.armature = 1e-4
    cubelet.joint.damping = [5e-4] * 3
    cubelet.joint.frictionloss = 1e-3
    core = spec.add_default("core", spec.default)
    core.geom.type = mujoco.mjtGeom.mjGEOM_SPHERE
    core.geom.size = [0.01, 0, 0]
    core.geom.contype = 0
    core.geom.conaffinity = 0
    core.geom.group = 4

    # Assets: a gradient skybox and a single UV sticker atlas / material.
    spec.add_texture(
        type=mujoco.mjtTexture.mjTEXTURE_SKYBOX,
        builtin=mujoco.mjtBuiltin.mjBUILTIN_GRADIENT,
        width=512,
        height=512,
    )
    spec.add_texture(name="sticker", type=mujoco.mjtTexture.mjTEXTURE_2D, file="sticker.png")
    material = spec.add_material(name="sticker")
    material.textures[mujoco.mjtTextureRole.mjTEXROLE_RGB] = "sticker"

    # Worldbody.
    spec.worldbody.add_light(pos=[0, 0, 1], castshadow=False)
    core_body = spec.worldbody.add_body(name="core", childclass="cubelet")
    core_body.add_geom(core)

    for dirs in cubelets():
        name = "_".join(dirs)
        body = core_body.add_body(name=name)
        colors: Mapping[str, str] = {d: DIR2COLOR[d] for d in dirs}
        if len(dirs) == 1:  # Center: a single actuated hinge.
            (d,) = dirs
            body.add_joint(name=name, type=mujoco.mjtJoint.mjJNT_HINGE, axis=dir2axis(d))
            spec.add_actuator(name=DIR2COLOR[d], trntype=mujoco.mjtTrn.mjTRN_JOINT, target=name)
        else:  # Edge / corner: a free-spinning ball joint.
            body.add_joint(name=name)
        vert, texcoord, face = build_cubelet_mesh(colors)
        spec.add_mesh(name=name, uservert=vert, usertexcoord=texcoord, userface=face)
        body.add_geom(meshname=name, pos=dir2pos(dirs))

    return spec


def main() -> None:
    spec = build()
    spec.compile()  # Validate.
    (SAVE_DIR / XML_NAME).write_text(spec.to_xml())
    viewer.launch_from_path(str(SAVE_DIR / XML_NAME))


if __name__ == "__main__":
    main()
