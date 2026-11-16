"""OCPE adapter interface for ocpe-disease-models.

Loads and strictly validates the external OCPE domain package
``ocpe/packages/disease-models`` against the pinned upstream OCPE engine and
specification, and exposes the registered quantities, the declarative
shared cardiovascular/autonomic model, and observation validation through
stable, generic OCPE APIs (``ocpe.load`` / ``ocpe.validate`` /
``ocpe.validate_observation`` / ``ocpe.Resolver``).
"""

from .adapter import (
    MODEL_CURIE,
    OCPE_SPEC_VERSION,
    PACKAGE_ID,
    PACKAGE_VERSION,
    UPSTREAM_COMMIT,
    UPSTREAM_REPOSITORY,
    DiseaseModelsOCPEAdapter,
    OCPEAdapterError,
    OCPERegistryError,
    default_package_dir,
    load_adapter,
)

__all__ = [
    "MODEL_CURIE",
    "OCPE_SPEC_VERSION",
    "PACKAGE_ID",
    "PACKAGE_VERSION",
    "UPSTREAM_COMMIT",
    "UPSTREAM_REPOSITORY",
    "DiseaseModelsOCPEAdapter",
    "OCPEAdapterError",
    "OCPERegistryError",
    "default_package_dir",
    "load_adapter",
]
