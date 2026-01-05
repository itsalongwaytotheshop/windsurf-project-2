#!/usr/bin/env python3
"""Comprehensive test of the noise calculator with various scenarios"""

from noise_estimator.core.calculator import NoiseCalculator
from noise_estimator.core.dataset import DatasetManager
from noise_estimator.models.schemas import (
    EstimationRequest, AssessmentType, CalculationMode, 
    EnvironmentApproach, TimePeriod, PropagationType
)

def print_separator(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

# Initialize the calculator
print("Initializing noise calculator...")
dataset_manager = DatasetManager('datasets')
calculator = NoiseCalculator(dataset_manager)

# Test different scenarios
print_separator("1. Distance-based Scenario Calculation")
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
print(f"Scenario: {result1.resolved_inputs['scenario'].name}")
print(f"Distance: {request1.receiver_distance}m")
print(f"Predicted level: {result1.predicted_level_db:.1f} dB")
print(f"Background level: {result1.background_db:.1f} dB")
print(f"Exceedance: {result1.exceed_background_db:.1f} dB")
print(f"Impact band: {result1.impact_band}")

# Show trace information
if result1.trace:
    print("\nTrace Information:")
    print(f"- Tables used: {list(result1.trace.tables_used.keys())}")
    combined_swl = result1.trace.intermediate_values.get('combined_swl_db')
    if combined_swl is not None:
        print(f"- Combined SWL: {combined_swl:.1f} dB")
    else:
        print("- Combined SWL: N/A")

print_separator("2. Full Estimator with Distance Finding")
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
print(f"Scenario: {result2.resolved_inputs['scenario'].name}")
print(f"Receiver distance: {request2.receiver_distance}m")
print(f"Predicted level: {result2.predicted_level_db:.1f} dB")
print(f"Background level: {result2.background_db:.1f} dB")
print(f"NML level: {result2.nml_db:.1f} dB")
print(f"Impact band: {result2.impact_band}")

print_separator("3. Noisiest Plant Calculation")
request3 = EstimationRequest(
    assessment_type=AssessmentType.DISTANCE_BASED,
    calculation_mode=CalculationMode.NOISIEST_PLANT,
    environment_approach=EnvironmentApproach.REPRESENTATIVE_NOISE_ENVIRONMENT,
    time_period=TimePeriod.DAY,
    propagation_type=PropagationType.RURAL,
    noise_category_id="R1",
    scenario_id="excavation",  # Used to get the plants
    receiver_distance=75.0
)

result3 = calculator.calculate(request3)
print(f"Distance: {request3.receiver_distance}m")
print(f"Predicted level: {result3.predicted_level_db:.1f} dB")
print(f"Background level: {result3.background_db:.1f} dB")
print(f"Exceedance: {result3.exceed_background_db:.1f} dB")

print_separator("4. User-supplied Background Level")
request4 = EstimationRequest(
    assessment_type=AssessmentType.DISTANCE_BASED,
    calculation_mode=CalculationMode.SCENARIO,
    environment_approach=EnvironmentApproach.USER_SUPPLIED_BACKGROUND_LEVEL,
    time_period=TimePeriod.DAY,
    propagation_type=PropagationType.RURAL,
    noise_category_id="R1",
    scenario_id="excavation",
    receiver_distance=50.0,
    user_background_level=60.0  # Custom background
)

result4 = calculator.calculate(request4)
print(f"User background: {result4.background_db:.1f} dB")
print(f"Predicted level: {result4.predicted_level_db:.1f} dB")
print(f"Exceedance: {result4.exceed_background_db:.1f} dB")

print_separator("5. Different Time Periods")
for period in [TimePeriod.DAY, TimePeriod.EVENING, TimePeriod.NIGHT]:
    request = EstimationRequest(
        assessment_type=AssessmentType.DISTANCE_BASED,
        calculation_mode=CalculationMode.SCENARIO,
        environment_approach=EnvironmentApproach.REPRESENTATIVE_NOISE_ENVIRONMENT,
        time_period=period,
        propagation_type=PropagationType.RURAL,
        noise_category_id="R1",
        scenario_id="excavation",
        receiver_distance=100.0
    )
    result = calculator.calculate(request)
    print(f"{period.value.capitalize():8s}: Background={result.background_db:5.1f} dB, "
          f"Predicted={result.predicted_level_db:5.1f} dB, "
          f"Exceed={result.exceed_background_db:5.1f} dB")

print_separator("6. Different Propagation Types")
for prop_type in [PropagationType.RURAL, PropagationType.URBAN, PropagationType.HARD_GROUND]:
    request = EstimationRequest(
        assessment_type=AssessmentType.DISTANCE_BASED,
        calculation_mode=CalculationMode.SCENARIO,
        environment_approach=EnvironmentApproach.REPRESENTATIVE_NOISE_ENVIRONMENT,
        time_period=TimePeriod.DAY,
        propagation_type=prop_type,
        noise_category_id="R1",
        scenario_id="excavation",
        receiver_distance=100.0
    )
    result = calculator.calculate(request)
    print(f"{prop_type.value:15s}: Predicted={result.predicted_level_db:5.1f} dB")

print_separator("7. Distance vs Level Analysis")
print("Distance (m) | Level (dB) | Background | Exceed")
print("-" * 45)
for distance in [10, 25, 50, 100, 200, 500]:
    request = EstimationRequest(
        assessment_type=AssessmentType.DISTANCE_BASED,
        calculation_mode=CalculationMode.SCENARIO,
        environment_approach=EnvironmentApproach.REPRESENTATIVE_NOISE_ENVIRONMENT,
        time_period=TimePeriod.DAY,
        propagation_type=PropagationType.RURAL,
        noise_category_id="R1",
        scenario_id="excavation",
        receiver_distance=distance
    )
    result = calculator.calculate(request)
    print(f"{distance:11d} | {result.predicted_level_db:10.1f} | "
          f"{result.background_db:9.1f} | {result.exceed_background_db:7.1f}")

print_separator("Test Complete!")
print("All calculations completed successfully!")
