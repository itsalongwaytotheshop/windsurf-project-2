"""
Noise Estimator Automation System

A production-ready system for construction and maintenance noise estimation
that replicates Excel macro workbook calculations without requiring Excel at runtime.
"""

__version__ = "1.0.0"
__author__ = "Noise Estimator Team"

from .core.calculator import NoiseCalculator
from .core.dataset import DatasetManager
from .models.schemas import (
    EstimationRequest,
    EstimationResult,
    AssessmentType,
    CalculationMode,
    EnvironmentApproach,
    TimePeriod,
    PropagationType,
    ImpactBand,
)

__all__ = [
    "NoiseCalculator",
    "DatasetManager", 
    "EstimationRequest",
    "EstimationResult",
    "AssessmentType",
    "CalculationMode",
    "EnvironmentApproach",
    "TimePeriod",
    "PropagationType",
    "ImpactBand",
]
