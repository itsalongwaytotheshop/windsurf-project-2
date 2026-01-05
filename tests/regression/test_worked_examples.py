"""
Regression tests against workbook worked examples.
"""

import pytest
from typing import Dict, Any
from noise_estimator.core.calculator import NoiseCalculator
from noise_estimator.models.schemas import EstimationRequest


class TestWorkedExamples:
    """Test cases validating against workbook worked examples."""
    
    def test_worked_example_1_basic_scenario(self, noise_calculator, sample_dataset):
        """Test against worked example 1: Basic scenario calculation."""
        # Get worked example from dataset
        worked_examples = sample_dataset.tables.get("worked_examples", [])
        example_1 = None
        
        for example in worked_examples:
            if example.get("id") == "example_1":
                example_1 = example
                break
        
        assert example_1 is not None, "Worked example 1 not found in dataset"
        
        # Create request from example inputs
        inputs = example_1["inputs"]
        request = EstimationRequest(**inputs)
        
        # Calculate result
        result = noise_calculator.calculate(request)
        
        # Get expected outputs
        expected = example_1["expected_outputs"]
        
        # Validate results within tolerance
        tolerance = 0.2  # dB tolerance
        
        assert abs(result.predicted_level_db - expected["predicted_level_db"]) <= tolerance, \
            f"Predicted level mismatch: {result.predicted_level_db} vs {expected['predicted_level_db']}"
        
        assert abs(result.background_db - expected["background_db"]) <= tolerance, \
            f"Background level mismatch: {result.background_db} vs {expected['background_db']}"
        
        assert abs(result.nml_db - expected["nml_db"]) <= tolerance, \
            f"NML level mismatch: {result.nml_db} vs {expected['nml_db']}"
        
        assert abs(result.exceed_background_db - expected["exceed_background_db"]) <= tolerance, \
            f"Background exceedance mismatch: {result.exceed_background_db} vs {expected['exceed_background_db']}"
        
        assert abs(result.exceed_nml_db - expected["exceed_nml_db"]) <= tolerance, \
            f"NML exceedance mismatch: {result.exceed_nml_db} vs {expected['exceed_nml_db']}"
        
        assert result.impact_band.value == expected["impact_band"], \
            f"Impact band mismatch: {result.impact_band.value} vs {expected['impact_band']}"
    
    def test_worked_example_2_distance_based(self, noise_calculator, sample_dataset):
        """Test against worked example 2: Distance-based calculation."""
        # Get worked example from dataset
        worked_examples = sample_dataset.tables.get("worked_examples", [])
        example_2 = None
        
        for example in worked_examples:
            if example.get("id") == "example_2":
                example_2 = example
                break
        
        assert example_2 is not None, "Worked example 2 not found in dataset"
        
        # Create request from example inputs
        inputs = example_2["inputs"]
        request = EstimationRequest(**inputs)
        
        # Calculate result
        result = noise_calculator.calculate(request)
        
        # Get expected outputs
        expected = example_2["expected_outputs"]
        
        # Validate distance results within tolerance
        tolerance = 1.0  # Distance tolerance in meters
        
        assert result.distances is not None, "Distance results should be present for distance-based calculation"
        
        if expected.get("distance_to_exceed_background") is not None:
            assert abs(result.distances.distance_to_exceed_background - expected["distance_to_exceed_background"]) <= tolerance, \
                f"Distance to exceed background mismatch: {result.distances.distance_to_exceed_background} vs {expected['distance_to_exceed_background']}"
        
        if expected.get("distance_to_nml") is not None:
            assert abs(result.distances.distance_to_nml - expected["distance_to_nml"]) <= tolerance, \
                f"Distance to NML mismatch: {result.distances.distance_to_nml} vs {expected['distance_to_nml']}"
        
        assert result.impact_band.value == expected["impact_band"], \
            f"Impact band mismatch: {result.impact_band.value} vs {expected['impact_band']}"
    
    def test_all_worked_examples_regression(self, noise_calculator, sample_dataset):
        """Test all worked examples in the dataset for regression."""
        worked_examples = sample_dataset.tables.get("worked_examples", [])
        
        if not worked_examples:
            pytest.skip("No worked examples found in dataset")
        
        tolerance_db = 0.2
        tolerance_distance = 1.0
        failed_examples = []
        
        for example in worked_examples:
            try:
                # Create request from example inputs
                inputs = example["inputs"]
                request = EstimationRequest(**inputs)
                
                # Calculate result
                result = noise_calculator.calculate(request)
                
                # Get expected outputs
                expected = example["expected_outputs"]
                
                # Validate each expected output
                for field, expected_value in expected.items():
                    if field.endswith("_db"):
                        # dB field validation
                        actual_value = getattr(result, field, None)
                        if actual_value is None:
                            failed_examples.append(f"{example['id']}: Missing field {field}")
                            continue
                        
                        if abs(actual_value - expected_value) > tolerance_db:
                            failed_examples.append(
                                f"{example['id']}: {field} mismatch: {actual_value} vs {expected_value}"
                            )
                    
                    elif field.startswith("distance_to_"):
                        # Distance field validation
                        if result.distances is None:
                            failed_examples.append(f"{example['id']}: Missing distance results")
                            continue
                        
                        actual_value = getattr(result.distances, field, None)
                        if actual_value is None:
                            failed_examples.append(f"{example['id']}: Missing distance field {field}")
                            continue
                        
                        if abs(actual_value - expected_value) > tolerance_distance:
                            failed_examples.append(
                                f"{example['id']}: {field} mismatch: {actual_value} vs {expected_value}"
                            )
                    
                    elif field == "impact_band":
                        # Impact band validation
                        if result.impact_band.value != expected_value:
                            failed_examples.append(
                                f"{example['id']}: impact_band mismatch: {result.impact_band.value} vs {expected_value}"
                            )
                
            except Exception as e:
                failed_examples.append(f"{example['id']}: Calculation failed with error: {str(e)}")
        
        # Assert no failures
        if failed_examples:
            failure_message = "Regression test failures:\n" + "\n".join(failed_examples)
            pytest.fail(failure_message)
    
    def test_calculation_reproducibility(self, noise_calculator, sample_requests):
        """Test that calculations are reproducible (same inputs = same outputs)."""
        from noise_estimator.models.schemas import EstimationRequest
        
        # Test with full estimator scenario
        request_data = sample_requests["full_estimator_scenario"]
        request = EstimationRequest(**request_data)
        
        # Run calculation multiple times
        results = []
        for i in range(5):
            result = noise_calculator.calculate(request)
            results.append(result)
        
        # All results should be identical
        first_result = results[0]
        for i, result in enumerate(results[1:], 1):
            assert result.predicted_level_db == first_result.predicted_level_db, \
                f"Result {i} has different predicted level"
            assert result.background_db == first_result.background_db, \
                f"Result {i} has different background level"
            assert result.nml_db == first_result.nml_db, \
                f"Result {i} has different NML level"
            assert result.impact_band == first_result.impact_band, \
                f"Result {i} has different impact band"
    
    def test_trace_consistency(self, noise_calculator, sample_requests):
        """Test that calculation traces are consistent and informative."""
        from noise_estimator.models.schemas import EstimationRequest
        
        # Test with trace enabled
        request_data = sample_requests["full_estimator_scenario"]
        request_data["include_trace"] = True
        request = EstimationRequest(**request_data)
        
        result = noise_calculator.calculate(request)
        
        # Verify trace is present and contains expected information
        assert result.trace is not None, "Trace should be present when requested"
        
        # Check that key tables are referenced
        assert "scenarios" in result.trace.tables_used, "Scenarios table should be referenced"
        assert "propagation_data" in result.trace.tables_used, "Propagation data should be referenced"
        
        # Check that intermediate values are calculated
        assert "source_level" in result.trace.intermediate_values, "Source level should be calculated"
        assert "received_level" in result.trace.intermediate_values, "Received level should be calculated"
        
        # Check that assumptions are recorded
        assert len(result.trace.assumptions) > 0, "Assumptions should be recorded"
    
    def test_edge_cases_and_boundary_conditions(self, noise_calculator):
        """Test edge cases and boundary conditions."""
        from noise_estimator.models.schemas import (
            EstimationRequest, AssessmentType, CalculationMode, 
            EnvironmentApproach, TimePeriod, PropagationType
        )
        
        # Test with minimum distance
        request = EstimationRequest(
            assessment_type=AssessmentType.FULL_ESTIMATOR,
            calculation_mode=CalculationMode.SCENARIO,
            environment_approach=EnvironmentApproach.REPRESENTATIVE_NOISE_ENVIRONMENT,
            time_period=TimePeriod.DAY,
            propagation_type=PropagationType.RURAL,
            noise_category_id="R1",
            scenario_id="excavation",
            receiver_distance=1.0  # Minimum practical distance
        )
        
        result = noise_calculator.calculate(request)
        assert result.predicted_level_db is not None
        assert result.predicted_level_db > 0
        
        # Test with large distance
        request.receiver_distance = 1000.0  # Large distance
        result = noise_calculator.calculate(request)
        assert result.predicted_level_db is not None
        # Level should be much lower at large distance
        assert result.predicted_level_db < 80.0  # Reasonable upper bound
    
    def test_different_time_periods(self, noise_calculator, sample_requests):
        """Test calculations across different time periods."""
        from noise_estimator.models.schemas import EstimationRequest, TimePeriod
        
        base_request_data = sample_requests["full_estimator_scenario"].copy()
        
        # Test all time periods
        for period in TimePeriod:
            base_request_data["time_period"] = period
            request = EstimationRequest(**base_request_data)
            
            result = noise_calculator.calculate(request)
            
            # Verify calculation completes successfully
            assert result.predicted_level_db is not None
            assert result.background_db is not None
            assert result.nml_db is not None
            
            # Background and NML should vary by time period
            # (This is a basic check - specific values depend on dataset)
            assert result.background_db > 0
            assert result.nml_db > 0
    
    def test_different_propagation_types(self, noise_calculator, sample_requests):
        """Test calculations across different propagation types."""
        from noise_estimator.models.schemas import EstimationRequest, PropagationType
        
        base_request_data = sample_requests["full_estimator_scenario"].copy()
        
        # Test all propagation types
        for prop_type in PropagationType:
            base_request_data["propagation_type"] = prop_type
            request = EstimationRequest(**base_request_data)
            
            result = noise_calculator.calculate(request)
            
            # Verify calculation completes successfully
            assert result.predicted_level_db is not None
            
            # Different propagation types should give different results
            # (This is a basic check - specific relationships depend on dataset)
            assert result.predicted_level_db > 0
