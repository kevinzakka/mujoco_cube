"""Generate per-cubelet meshes with UV coordinates into the sticker atlas."""

from typing import Mapping, Sequence

import numpy as np
import trimesh

from build_textures import SWATCH_ORDER

# Vertices of the chamfered cubelet, obtained via ``process_mesh.py``.
CUBELET_VERTICES = np.array(
    """
    0.008075 0.0095 -0.008075   -0.008075 0.0095 -0.008075
    0.008075 0.0095 0.008075    -0.008075 0.0095 0.008075
    -0.0095 0.008075 -0.008075  -0.0095 -0.008075 -0.008075
    -0.0095 0.008075 0.008075   -0.0095 -0.008075 0.008075
    0.008075 -0.0095 -0.008075  0.008075 -0.0095 0.008075
    -0.008075 -0.0095 -0.008075 -0.008075 -0.0095 0.008075
    0.0095 0.008075 0.008075    0.0095 -0.008075 0.008075
    0.0095 0.008075 -0.008075   0.0095 -0.008075 -0.008075
    0.008075 0.008075 0.0095    -0.008075 0.008075 0.0095
    0.008075 -0.008075 0.0095   -0.008075 -0.008075 0.0095
    0.008075 -0.008075 -0.0095  -0.008075 -0.008075 -0.0095
    0.008075 0.008075 -0.0095   -0.008075 0.008075 -0.0095
    """.split(),
    dtype=float,
).reshape(-1, 3)

_EXT = 0.0095  # Half-extent of the cubelet (sticker faces sit here).
_HALF = 0.008075  # Half-width of a square sticker face.
_N = len(SWATCH_ORDER)  # Number of atlas swatches.
_PAD = 0.01  # UV inset (in swatch fractions) to avoid bilinear bleed at seams.

# Map a direction string to (axis, sign).
_DIR2AXIS = {
    "pX": (0, 1), "nX": (0, -1),
    "pY": (1, 1), "nY": (1, -1),
    "pZ": (2, 1), "nZ": (2, -1),
}


def _swatch_uv(name: str, tu: float, tv: float) -> Sequence[float]:
    """Map an in-swatch coordinate (tu, tv) in [0, 1]^2 to atlas UV."""
    i = SWATCH_ORDER.index(name)
    u = (i + _PAD + tu * (1.0 - 2.0 * _PAD)) / _N
    v = _PAD + tv * (1.0 - 2.0 * _PAD)
    return u, v


def _classify(normal: np.ndarray, centroid: np.ndarray):
    """Return (axis, sign) if the triangle lies on a square sticker face, else None."""
    axis = int(np.argmax(np.abs(normal)))
    on_axis = abs(abs(normal[axis]) - 1.0) < 1e-6
    on_face = abs(abs(centroid[axis]) - _EXT) < 1e-6
    if on_axis and on_face:
        return axis, int(np.sign(normal[axis]))
    return None


def build_cubelet_mesh(
    dir2color: Mapping[str, str],
) -> tuple[list[float], list[float], list[int]]:
    """Build a cubelet mesh whose sticker faces use the colors in ``dir2color``."""
    hull = trimesh.convex.convex_hull(CUBELET_VERTICES)
    # Map colored faces keyed by (axis, sign).
    face_color = {_DIR2AXIS[d]: c for d, c in dir2color.items()}

    verts: list[float] = []
    uvs: list[float] = []
    faces: list[int] = []
    for tri, normal, centroid in zip(
        hull.triangles, hull.face_normals, hull.triangles_center
    ):
        face = _classify(normal, centroid)
        color = face_color.get(face, "black") if face is not None else "black"
        base = len(verts) // 3
        for vertex in tri:
            verts.extend(float(c) for c in vertex)
            if color == "black":
                uvs.extend(_swatch_uv("black", 0.5, 0.5))
            else:
                axis, _ = face
                u_ax, v_ax = (a for a in range(3) if a != axis)
                tu = (vertex[u_ax] + _HALF) / (2.0 * _HALF)
                tv = (vertex[v_ax] + _HALF) / (2.0 * _HALF)
                uvs.extend(_swatch_uv(color, tu, tv))
        faces.extend((base, base + 1, base + 2))

    return verts, uvs, faces
