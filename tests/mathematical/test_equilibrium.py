"""VAL-MATH-EQUILIBRIUM: configured supine fixed points and flow identities."""

from __future__ import annotations

import numpy as np
import pytest

from ocpe_disease_models.config import compose_phenotypes, load_protocol
from ocpe_disease_models.models.shared.model import STATE_NAMES

pytestmark = pytest.mark.mathematical

ALL_PHENOTYPE_IDS = (
    "healthy-reference",
    "pots-neuropathic",
    "pots-hyperadrenergic",
    "pots-hypovolemic",
    "pots-mixed",
    "eds-heds-vascular",
    "eds-heds-mecfs-comorbid",
    "mecfs-pem",
    "long-covid-autonomic",
    "long-covid-exertional",
)


@pytest.mark.parametrize("phenotype_id", ALL_PHENOTYPE_IDS)
def test_complete_supine_state_is_a_fixed_point(phenotype_id):
    patient = compose_phenotypes([phenotype_id])
    protocol, _ = load_protocol("resting-baseline")
    state = patient.initial_state()
    derivative = patient.rhs(0.0, state, protocol)
    assert np.max(np.abs(derivative)) < 1e-9, (
        f"{phenotype_id} supine residual: "
        + ", ".join(
            f"{name}={value:.3g}"
            for name, value in zip(STATE_NAMES, derivative, strict=True)
        )
    )


@pytest.mark.parametrize("phenotype_id", ALL_PHENOTYPE_IDS)
def test_supine_cardiac_output_and_venous_return_identities(phenotype_id):
    patient = compose_phenotypes([phenotype_id])
    protocol, _ = load_protocol("resting-baseline")
    derived = patient._derived(0.0, patient.initial_state(), protocol)
    assert derived["cardiac_output"] == pytest.approx(
        derived["heart_rate"] * derived["stroke_volume"] / 60.0,
        rel=1e-12,
    )
    assert derived["venous_return"] == pytest.approx(
        derived["cardiac_output"], rel=1e-10
    )
    assert derived["systemic_flow"] == pytest.approx(
        derived["cardiac_output"], rel=1e-10
    )
    assert derived["splanchnic_arterial_flow"] == pytest.approx(
        derived["splanchnic_venous_return"], rel=1e-10
    )
    assert derived["lower_limb_arterial_flow"] == pytest.approx(
        derived["lower_limb_venous_return"], rel=1e-10
    )
    assert derived["other_systemic_arterial_flow"] == pytest.approx(
        derived["other_systemic_venous_return"], rel=1e-10
    )
