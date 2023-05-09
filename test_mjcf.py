from dm_control import mjcf
import numpy as np
from absl.testing import absltest
from pathlib import Path

_XML_FILE = Path(__file__).parent / "cube_3x3x3.xml"


class Cube3x3x3Test(absltest.TestCase):
    """Tests for the cube_3x3x3.xml model."""

    def test_can_compile_and_step(self) -> None:
        """Tests that we can compile the model and step the physics."""
        model = mjcf.from_path(str(_XML_FILE))
        physics = mjcf.Physics.from_mjcf_model(model)
        physics.step()

    def test_mass(self) -> None:
        """Tests that the total mass of the cube is what we expect."""
        model = mjcf.from_path(str(_XML_FILE))
        physics = mjcf.Physics.from_mjcf_model(model)
        expected_mass = 0.0685
        actual_mass = physics.bind(model.worldbody).subtreemass
        np.testing.assert_almost_equal(actual_mass, expected_mass, decimal=6)

    def test_freejoint(self) -> None:
        """Tests that adding a freejoint to the cube does not throw an error."""
        model = mjcf.from_path(str(_XML_FILE))
        model.worldbody.find("body", "core").add("freejoint")
        physics = mjcf.Physics.from_mjcf_model(model)
        physics.step()


if __name__ == "__main__":
    absltest.main()
