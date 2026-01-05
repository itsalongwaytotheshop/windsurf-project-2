#!/usr/bin/env python3
"""Quick test of the noise calculator"""

from noise_estimator.core.calculator import NoiseCalculator
from noise_estimator.core.dataset import DatasetManager
from noise_estimator.models.schemas import (
    EstimationRequest, AssessmentType, CalculationMode, 
    EnvironmentApproach, TimePeriod, PropagationType
)

# Initialize the calculator
print("Initializing noise calculator...")
dataset_manager = DatasetManager('datasets')
calculator = NoiseCalculator(dataset_manager)

# Test 1: Distance-based scenario calculation
print("\n=== Test 1: Distance-based Scenario ===")
request1 = EstimationRequest(
    assessment_type=AssessmentType.DISTANCE_BASED,
    calculation_mode=CalculationMode.SCENARIO,
    environment_approach=EnvironmentApproach.REPRESENTATIVE_NOISE_ENVIRONMENT,
    time_period=TimePeriod.DAY,
    propagation_type=PropagationType.RURAL,
    noise_category_id="R1",
    scenario_id="excavation",
    receiver_distance=100.0,
    include_trace=True
)

result1 = calculator.calculate(request1)
print(f"Predicted level at 100m: {result1.predicted_level_db:.1f} dB")
print(f"Background level: {result1.background_db:.1f} dB")
print(f"Exceedance: {result1.exceed_background_db:.1f} dB")
print(f"Impact band: {result1.impact_band}")

# Test 2: Full estimator scenario calculation
print("\n=== Test 2: Full Estimator Scenario ===")
request2 = EstimationRequest(
    assessment_type=AssessmentType.FULL_ESTIMATOR,
    calculation_mode=CalculationMode.SCENARIO,
    environment_approach=EnvironmentApproach.REPRESENTATIVE_NOISE_ENVIRONMENT,
    time_period=TimePeriod.NIGHT,
    propagation_type=PropagationType.URBAN,
    noise_category_id="U2",
    scenario_id="paving",
    receiver_distance=50.0,
    include_trace=True
)

result2 = calculator.calculate(request2)
print(f"Predicted level: {result2.predicted_level_db:.1f} dB")
print(f"Background level: {result2.background_db:.1f} dB")
print(f"NML level: {result2.nml_db:.1f} dB")
if result2.distances:
    print(f"Distance to exceed background: {result2.distances.distance_to_exceed_background:.1f} m")
print(f"Impact band: {result2.impact_band}")

# Test 3: User-supplied background
print("\n=== Test 3: User-supplied Background ===")
request3 = EstimationRequest(
    assessment_type=AssessmentType.DISTANCE_BASED,
    calculation_mode=CalculationMode.NOISIEST_PLANT,
    environment_approach=EnvironmentApproach.USER_SUPPLIED_BACKGROUND_LEVEL,
    time_period=TimePeriod.DAY,
    propagation_type=PropagationType.RURAL,
    noise_category_id="R1",
    scenario_id="excavation",
    receiver_distance=75.0,
    user_background_level=60.0  # Custom background level
)

result3 = calculator.calculate(request3)
print(f"Predicted level: {result3.predicted_level_db:.1f} dB")
print(f"User background: {result3.background_db:.1f} dB")
print(f"Exceedance: {result3.exceed_background_db:.1f} dB")

print("\n=== All tests completed successfully! ===")
