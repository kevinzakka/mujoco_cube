from dm_control import mjcf, mujoco
from PIL import Image

res = (480, 640)  # Render resolution.
xml_file = "cube_3x3x3.xml"
model = mjcf.from_path(xml_file)

# Ensure offscreen buffer size supports rendering at `res`.
getattr(model.visual, "global").offheight = res[0]
getattr(model.visual, "global").offwidth = res[1]

physics = mjcf.Physics.from_mjcf_model(model)
camera = mujoco.MovableCamera(physics, height=res[0], width=res[1])

# Render the model and pan the camera around it.
frames = []
rot = 360.0
delta = 10.0
for i in range(int(rot / delta)):
    camera._render_camera.azimuth = i * delta
    frames.append(Image.fromarray(camera.render()))

# Save the frames as a gif.
frames[0].save(
    "cube3x3x3.gif",
    format="GIF",
    append_images=frames[1:],
    save_all=True,
    loop=0,
    duration=100,
)
