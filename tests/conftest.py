"""
Pytest configuration and fixtures for the noise estimator test suite.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

from noise_estimator.core.dataset import DatasetManager
from noise_estimator.core.calculator import NoiseCalculator
from noise_estimator.models.schemas import (
    ExtractedDataset,
    DatasetMetadata,
    TableMetadata,
    NoiseCategory,
    Scenario,
    Plant,
    MitigationMeasure,
    AssessmentType,
    CalculationMode,
    EnvironmentApproach,
    TimePeriod,
    PropagationType,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_dataset():
    """Create a sample dataset for testing."""
    # Sample metadata
    metadata = DatasetMetadata(
        workbook_name="test_workbook.xlsm",
        extraction_timestamp="2024-01-01T00:00:00",
        workbook_hash="abc123def456",
        version="20240101_000000_abc123de",
        total_tables=6,
        sheet_count=10
    )
    
    # Sample noise categories
    noise_categories = [
        {
            "id": "R1",
            "name": "Rural Residential",
            "description": "Rural residential area",
            "time_periods": {
                "day": 45.0,
                "evening": 40.0,
                "night": 35.0
            },
            "nml_values": {
                "day": 55.0,
                "evening": 50.0,
                "night": 45.0
            }
        },
        {
            "id": "U2",
            "name": "Urban Commercial",
            "description": "Urban commercial area",
            "time_periods": {
                "day": 55.0,
                "evening": 50.0,
                "night": 45.0
            },
            "nml_values": {
                "day": 65.0,
                "evening": 60.0,
                "night": 55.0
            }
        }
    ]
    
    # Sample scenarios
    scenarios = [
        {
            "id": "excavation",
            "name": "Excavation Works",
            "description": "General excavation activities",
            "sound_power_levels": {
                "excavator": 105.0,
                "truck": 102.0
            },
            "propagation_type": "rural",
            "applicable_measures": ["standard_1", "additional_1"]
        },
        {
            "id": "paving",
            "name": "Paving Works",
            "description": "Road paving activities",
            "sound_power_levels": {
                "paver": 98.0,
                "roller": 100.0
            },
            "propagation_type": "urban",
            "applicable_measures": ["standard_2"]
        }
    ]
    
    # Sample plants
    plants = [
        {
            "id": "excavator",
            "name": "Excavator",
            "description": "Heavy excavator machine",
            "sound_power_level": 105.0,
            "category": "heavy_equipment",
            "duty_cycle": 0.8,
            "usage_factor": 1.0
        },
        {
            "id": "truck",
            "name": "Dump Truck",
            "description": "Heavy dump truck",
            "sound_power_level": 102.0,
            "category": "vehicles",
            "duty_cycle": 0.6,
            "usage_factor": 1.0
        },
        {
            "id": "paver",
            "name": "Asphalt Paver",
            "description": "Road paving machine",
            "sound_power_level": 98.0,
            "category": "paving_equipment",
            "duty_cycle": 0.9,
            "usage_factor": 1.0
        }
    ]
    
    # Sample mitigation measures
    mitigation_measures = [
        {
            "id": "standard_1",
            "title": "Standard Noise Barrier",
            "text": "Install standard noise barrier along site boundary",
            "type": "standard",
            "trigger_conditions": {
                "impact_band": ["moderately_affected", "highly_affected"]
            },
            "reduction_db": 5.0
        },
        {
            "id": "standard_2",
            "title": "Working Hours Restriction",
            "text": "Restrict noisy activities to standard working hours",
            "type": "standard",
            "trigger_conditions": {
                "impact_band": ["moderately_affected", "highly_affected"]
            },
            "reduction_db": 3.0
        },
        {
            "id": "additional_1",
            "title": "Acoustic Enclosure",
            "text": "Provide acoustic enclosure for noisy equipment",
            "type": "additional",
            "trigger_conditions": {
                "impact_band": ["highly_affected"]
            },
            "reduction_db": 10.0
        }
    ]
    
    # Sample background levels
    background_levels = [
        {
            "category": "R1",
            "time_period": "day",
            "level": 45.0
        },
        {
            "category": "R1",
            "time_period": "evening",
            "level": 40.0
        },
        {
            "category": "R1",
            "time_period": "night",
            "level": 35.0
        },
        {
            "category": "U2",
            "time_period": "day",
            "level": 55.0
        },
        {
            "category": "U2",
            "time_period": "evening",
            "level": 50.0
        },
        {
            "category": "U2",
            "time_period": "night",
            "level": 45.0
        }
    ]
    
    # Sample propagation data
    propagation_data = [
        {
            "propagation_type": "rural",
            "distance": 10,
            "attenuation": 20.0
        },
        {
            "propagation_type": "rural",
            "distance": 50,
            "attenuation": 34.0
        },
        {
            "propagation_type": "rural",
            "distance": 100,
            "attenuation": 40.0
        },
        {
            "propagation_type": "urban",
            "distance": 10,
            "attenuation": 20.0
        },
        {
            "propagation_type": "urban",
            "distance": 50,
            "attenuation": 34.0
        },
        {
            "propagation_type": "urban",
            "distance": 100,
            "attenuation": 40.0
        }
    ]
    
    # Sample distance tables
    distance_tables = [
        {
            "scenario": "excavation",
            "distance": 10,
            "level": 85.0
        },
        {
            "scenario": "excavation",
            "distance": 50,
            "level": 71.0
        },
        {
            "scenario": "excavation",
            "distance": 100,
            "level": 65.0
        }
    ]
    
    # Sample worked examples
    worked_examples = [
        {
            "id": "example_1",
            "description": "Basic scenario calculation",
            "inputs": {
                "assessment_type": "full_estimator",
                "calculation_mode": "scenario",
                "scenario_id": "excavation",
                "noise_category_id": "R1",
                "time_period": "day",
                "propagation_type": "rural",
                "receiver_distance": 50.0,
                "environment_approach": "representative_noise_environment"
            },
            "expected_outputs": {
                "predicted_level_db": 71.0,
                "background_db": 45.0,
                "nml_db": 55.0,
                "exceed_background_db": 26.0,
                "exceed_nml_db": 16.0,
                "impact_band": "highly_affected"
            }
        },
        {
            "id": "example_2",
            "description": "Distance-based calculation",
            "inputs": {
                "assessment_type": "distance_based",
                "calculation_mode": "scenario",
                "scenario_id": "paving",
                "noise_category_id": "U2",
                "time_period": "evening",
                "propagation_type": "urban",
                "environment_approach": "representative_noise_environment"
            },
            "expected_outputs": {
                "distance_to_exceed_background": 25.0,
                "distance_to_nml": 15.0,
                "impact_band": "moderately_affected"
            }
        }
    ]
    
    # Table metadata
    table_metadata = {
        "noise_categories": TableMetadata(
            name="noise_categories",
            sheet_name="Categories",
            cell_range="A1:D3",
            column_types={"id": "string", "name": "string", "description": "string"},
            row_count=2,
            has_headers=True
        ),
        "scenarios": TableMetadata(
            name="scenarios",
            sheet_name="Scenarios",
            cell_range="A1:F2",
            column_types={"id": "string", "name": "string", "sound_power_level": "float"},
            row_count=2,
            has_headers=True
        ),
        "plants": TableMetadata(
            name="plants",
            sheet_name="Plants",
            cell_range="A1:G3",
            column_types={"id": "string", "name": "string", "sound_power_level": "float"},
            row_count=3,
            has_headers=True
        ),
        "mitigation_measures": TableMetadata(
            name="mitigation_measures",
            sheet_name="Measures",
            cell_range="A1:E3",
            column_types={"id": "string", "title": "string", "type": "string"},
            row_count=3,
            has_headers=True
        ),
        "background_levels": TableMetadata(
            name="background_levels",
            sheet_name="Background",
            cell_range="A1:D7",
            column_types={"category": "string", "time_period": "string", "level": "float"},
            row_count=6,
            has_headers=True
        ),
        "propagation_data": TableMetadata(
            name="propagation_data",
            sheet_name="Propagation",
            cell_range="A1:C7",
            column_types={"propagation_type": "string", "distance": "float", "attenuation": "float"},
            row_count=6,
            has_headers=True
        ),
        "distance_tables": TableMetadata(
            name="distance_tables",
            sheet_name="Distances",
            cell_range="A1:D4",
            column_types={"scenario": "string", "distance": "float", "level": "float"},
            row_count=3,
            has_headers=True
        ),
        "worked_examples": TableMetadata(
            name="worked_examples",
            sheet_name="Examples",
            cell_range="A1:E3",
            column_types={"id": "string", "description": "string"},
            row_count=2,
            has_headers=True
        )
    }
    
    # Create dataset
    dataset = ExtractedDataset(
        metadata=metadata,
        tables={
            "noise_categories": noise_categories,
            "scenarios": scenarios,
            "plants": plants,
            "mitigation_measures": mitigation_measures,
            "background_levels": background_levels,
            "propagation_data": propagation_data,
            "distance_tables": distance_tables,
            "worked_examples": worked_examples
        },
        table_metadata=table_metadata
    )
    
    return dataset


@pytest.fixture
def dataset_manager(temp_dir, sample_dataset):
    """Create a dataset manager with sample data."""
    # Save sample dataset to temp directory
    dataset_dir = temp_dir / "datasets" / sample_dataset.metadata.version
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(dataset_dir / "dataset.json", 'w') as f:
        json.dump(sample_dataset.dict(), f, indent=2, default=str)
    
    # Create dataset manager
    manager = DatasetManager(temp_dir / "datasets")
    manager.load_dataset(sample_dataset.metadata.version)
    
    return manager


@pytest.fixture
def noise_calculator(dataset_manager):
    """Create a noise calculator with sample dataset."""
    return NoiseCalculator(dataset_manager)


@pytest.fixture
def sample_requests():
    """Create sample estimation requests for testing."""
    return {
        "full_estimator_scenario": {
            "assessment_type": AssessmentType.FULL_ESTIMATOR,
            "calculation_mode": CalculationMode.SCENARIO,
            "environment_approach": EnvironmentApproach.REPRESENTATIVE_NOISE_ENVIRONMENT,
            "time_period": TimePeriod.DAY,
            "propagation_type": PropagationType.RURAL,
            "noise_category_id": "R1",
            "scenario_id": "excavation",
            "receiver_distance": 50.0,
            "include_trace": True,
            "output_pack": "none"
        },
        "full_estimator_plant": {
            "assessment_type": AssessmentType.FULL_ESTIMATOR,
            "calculation_mode": CalculationMode.INDIVIDUAL_PLANT,
            "environment_approach": EnvironmentApproach.USER_SUPPLIED_BACKGROUND_LEVEL,
            "time_period": TimePeriod.EVENING,
            "propagation_type": PropagationType.URBAN,
            "noise_category_id": "U2",
            "plant_ids": ["excavator", "truck"],
            "receiver_distance": 30.0,
            "user_background_level": 50.0,
            "include_trace": False,
            "output_pack": "step2"
        },
        "distance_based_scenario": {
            "assessment_type": AssessmentType.DISTANCE_BASED,
            "calculation_mode": CalculationMode.SCENARIO,
            "environment_approach": EnvironmentApproach.REPRESENTATIVE_NOISE_ENVIRONMENT,
            "time_period": TimePeriod.DAY,
            "propagation_type": PropagationType.RURAL,
            "noise_category_id": "R1",
            "scenario_id": "excavation",
            "receiver_distance": 100.0,
            "include_trace": True,
            "output_pack": "ref"
        },
        "distance_based_noisiest": {
            "assessment_type": AssessmentType.DISTANCE_BASED,
            "calculation_mode": CalculationMode.NOISIEST_PLANT,
            "environment_approach": EnvironmentApproach.REPRESENTATIVE_NOISE_ENVIRONMENT,
            "time_period": TimePeriod.NIGHT,
            "propagation_type": PropagationType.URBAN,
            "noise_category_id": "U2",
            "scenario_id": "paving",
            "receiver_distance": 50.0,
            "include_trace": False,
            "output_pack": "both"
        }
    }
