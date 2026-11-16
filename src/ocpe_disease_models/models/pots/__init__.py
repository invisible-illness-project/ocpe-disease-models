"""POTS phenotype configurations built from shared mechanisms."""

from ...config import compose_phenotypes


def create(phenotype: str = "pots-neuropathic"):
    if not phenotype.startswith("pots-"):
        raise ValueError(f"Not a POTS phenotype: {phenotype}")
    return compose_phenotypes([phenotype])


PHENOTYPES = ("pots-neuropathic", "pots-hyperadrenergic", "pots-hypovolemic", "pots-mixed")
