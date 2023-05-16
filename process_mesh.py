"""Process the CAD mesh to get vertex information for MuJoCo."""

import trimesh
import numpy as np

mesh = trimesh.load_mesh("cubelet.stl")

# Scale to meters.
mesh.apply_scale(0.001)

# Translate to origin.
mesh.apply_translation(-mesh.centroid)

# Print the vertices.
for vertex in mesh.vertices:
    print(f"{vertex[0]:.6g} {vertex[1]:.6g} {vertex[2]:.6g}")

# Confirm cube size is 0.019.
np.testing.assert_equal(mesh.extents, [0.019] * 3)
