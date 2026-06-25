"""Render a spinning GIF of the cube."""

import mujoco
from PIL import Image

res = (480, 640)  # Render resolution (height, width).
xml_file = "cube_3x3x3.xml"

model = mujoco.MjModel.from_xml_path(xml_file)
data = mujoco.MjData(model)
mujoco.mj_forward(model, data)

renderer = mujoco.Renderer(model, *res)
camera = mujoco.MjvCamera()
mujoco.mjv_defaultFreeCamera(model, camera)

# Render the model and pan the camera around it.
frames = []
rot = 360.0
delta = 10.0
for i in range(int(rot / delta)):
    camera.azimuth = i * delta
    renderer.update_scene(data, camera)
    frames.append(Image.fromarray(renderer.render()))

# Save the frames as a gif.
frames[0].save(
    "cube3x3x3.gif",
    format="GIF",
    append_images=frames[1:],
    save_all=True,
    loop=0,
    duration=100,
)
