import mujoco
import numpy as np
from absl.testing import absltest
from pathlib import Path

_XML_FILE = Path(__file__).parent / "cube_3x3x3.xml"


class Cube3x3x3Test(absltest.TestCase):
    """Tests for the cube_3x3x3.xml model."""

    def test_can_compile_and_step(self) -> None:
        """Tests that we can compile the model and step the physics."""
        model = mujoco.MjModel.from_xml_path(str(_XML_FILE))
        data = mujoco.MjData(model)
        mujoco.mj_step(model, data)

    def test_mass(self) -> None:
        """Tests that the total mass of the cube is what we expect."""
        model = mujoco.MjModel.from_xml_path(str(_XML_FILE))
        np.testing.assert_almost_equal(model.body_subtreemass[0], 0.0685, decimal=6)

    def test_freejoint(self) -> None:
        """Tests that adding a freejoint to the cube does not throw an error."""
        spec = mujoco.MjSpec.from_file(str(_XML_FILE))
        spec.body("core").add_freejoint()
        model = spec.compile()
        mujoco.mj_step(model, mujoco.MjData(model))


if __name__ == "__main__":
    absltest.main()
