"""EDS/hEDS vascular-mechanics configurations; subtype-specific limitations apply."""

from ...config import compose_phenotypes


def create(phenotype: str = "eds-heds-vascular"):
    if not phenotype.startswith("eds-"):
        raise ValueError(f"Not an EDS phenotype: {phenotype}")
    return compose_phenotypes([phenotype])


PHENOTYPES = ("eds-heds-vascular", "eds-heds-mecfs-comorbid")
