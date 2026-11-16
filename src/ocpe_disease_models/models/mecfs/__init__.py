"""ME/CFS dynamic stress, PEM and recovery configurations."""

from ...config import compose_phenotypes


def create(phenotype: str = "mecfs-pem"):
    if phenotype != "mecfs-pem":
        raise ValueError(f"Unknown ME/CFS phenotype: {phenotype}")
    return compose_phenotypes([phenotype])


PHENOTYPES = ("mecfs-pem",)
