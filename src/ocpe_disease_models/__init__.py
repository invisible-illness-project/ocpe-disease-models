"""Literature-grounded disease models using OCPE semantic infrastructure."""

__version__ = "0.1.0"
OCPE_COMMIT = "3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d"

from .models.shared.model import (  # noqa: E402
    ComputationalPatient,
    ModelParameters,
    SimulationResult,
)

__all__ = ["ComputationalPatient", "ModelParameters", "SimulationResult"]
