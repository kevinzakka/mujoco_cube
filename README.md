# MuJoCo 3x3x3 Puzzle Cube

[![build][tests-badge]][tests]

[tests-badge]: https://github.com/kevinzakka/mujoco_cube/actions/workflows/ci.yml/badge.svg
[tests]: https://github.com/kevinzakka/mujoco_cube/actions/workflows/ci.yml

[MuJoCo] model of a 3x3x3 puzzle cube, along with a script to procedurally generate it. Inspired by the [Rubik's Cube].

<p float="left">
  <img src="cube3x3x3.gif" width="400">
</p>

## Play with the model

Just drag and drop the `cube_3x3x3.xml` file into the simulate window.

## Generate the model

First install the dependencies:

```bash
pip install -r requirements.txt
```

Then run the following to generate the assets and XML file:

```bash
python build_textures.py  # Creates the assets/ dir.
python build_mjcf.py  # Creates cube_3x3x3.xml.
```

[MuJoCo]: https://github.com/deepmind/mujoco
[Rubik's Cube]: https://en.wikipedia.org/wiki/Rubik%27s_Cube
