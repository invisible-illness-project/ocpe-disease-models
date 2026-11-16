"""Long COVID autonomic and exertional physiological subgroups."""

from ...config import compose_phenotypes


def create(phenotype: str = "long-covid-autonomic"):
    if not phenotype.startswith("long-covid-"):
        raise ValueError(f"Not a Long COVID phenotype: {phenotype}")
    return compose_phenotypes([phenotype])


PHENOTYPES = ("long-covid-autonomic", "long-covid-exertional")
