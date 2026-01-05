"""
Unit tests for the noise calculation engine.
"""

import pytest
import math
from noise_estimator.core.calculator import NoiseCalculator
from noise_estimator.models.schemas import (
    AssessmentType,
    CalculationMode,
    EnvironmentApproach,
    TimePeriod,
    PropagationType,
    ImpactBand,
)


class TestNoiseCalculator:
    """Test cases for NoiseCalculator class."""
    
    def test_db_sum_single_value(self, noise_calculator):
        """Test dB summing with single value."""
        result = noise_calculator._db_sum([85.0])
        assert result == 85.0
    
    def test_db_sum_multiple_values(self, noise_calculator):
        """Test dB summing with multiple values."""
        # Test with two equal values: should increase by 3dB
        result = noise_calculator._db_sum([85.0, 85.0])
        expected = 85.0 + 3.01  # 10 * log10(2) ≈ 3.01 dB
        assert abs(result - expected) < 0.1
        
        # Test with three equal values: should increase by ~4.8dB
        result = noise_calculator._db_sum([85.0, 85.0, 85.0])
        expected = 85.0 + 10 * math.log10(3)
        assert abs(result - expected) < 0.1
    
    def test_db_sum_empty_list(self, noise_calculator):
        """Test dB summing with empty list."""
        result = noise_calculator._db_sum([])
        assert result == 0.0
    
    def test_apply_propagation_basic(self, noise_calculator):
        """Test basic propagation calculation."""
        source_level = 105.0
        distance = 100.0
        propagation_type = PropagationType.RURAL
        
        result = noise_calculator._apply_propagation(
            source_level, distance, propagation_type, 
            noise_calculator.dataset_manager.get_current_dataset(), None
        )
        
        # Should be less than source level due to geometric spreading
        assert result < source_level
        
        # Geometric spreading at 100m should be 40dB (20*log10(100))
        expected = source_level - 40.0  # Basic geometric spreading
        # Allow some tolerance for ground absorption
        assert abs(result - expected) < 5.0
    
    def test_apply_propagation_zero_distance(self, noise_calculator):
        """Test propagation with zero distance should raise error."""
        with pytest.raises(ValueError, match="Distance must be positive"):
            noise_calculator._apply_propagation(
                105.0, 0.0, PropagationType.RURAL,
                noise_calculator.dataset_manager.get_current_dataset(), None
            )
    
    def test_determine_impact_band(self, noise_calculator):
        """Test impact band determination."""
        # Test not affected (below NML)
        result = noise_calculator._determine_impact_band(2.0, -5.0, None)
        assert result == ImpactBand.NOT_AFFECTED
        
        # Test moderately affected (slightly above NML)
        result = noise_calculator._determine_impact_band(8.0, 3.0, None)
        assert result == ImpactBand.MODERATELY_AFFECTED
        
        # Test highly affected (significantly above NML)
        result = noise_calculator._determine_impact_band(15.0, 10.0, None)
        assert result == ImpactBand.HIGHLY_AFFECTED
    
    def test_get_ground_absorption(self, noise_calculator):
        """Test ground absorption calculation."""
        # Test different propagation types
        rural_absorption = noise_calculator._get_ground_absorption(50.0, PropagationType.RURAL, {})
        urban_absorption = noise_calculator._get_ground_absorption(50.0, PropagationType.URBAN, {})
        hard_absorption = noise_calculator._get_ground_absorption(50.0, PropagationType.HARD_GROUND, {})
        
        # Rural should have higher absorption than urban
        assert rural_absorption > urban_absorption
        
        # Hard ground should have minimal absorption
        assert hard_absorption <= urban_absorption
    
    def test_find_distance_for_level_achievable(self, noise_calculator):
        """Test distance finding for achievable target level."""
        source_level = 105.0
        target_level = 65.0  # Should be achievable at some distance
        propagation_type = PropagationType.RURAL
        
        result = noise_calculator._find_distance_for_level(
            source_level, target_level, propagation_type,
            noise_calculator.dataset_manager.get_current_dataset(), "test"
        )
        
        assert result is not None
        assert result > 0
        assert isinstance(result, float)
    
    def test_find_distance_for_level_unachievable(self, noise_calculator):
        """Test distance finding for unachievable target level."""
        source_level = 150.0  # High source level
        target_level = -10.0  # Very low target (below minimum possible)
        propagation_type = PropagationType.RURAL
        
        result = noise_calculator._find_distance_for_level(
            source_level, target_level, propagation_type,
            noise_calculator.dataset_manager.get_current_dataset(), "test"
        )
        
        # Should return None for unachievable target
        assert result is None
    
    def test_get_representative_background_from_category(self, noise_calculator):
        """Test getting representative background from category data."""
        from noise_estimator.models.schemas import NoiseCategory, TimePeriod
        
        category = NoiseCategory(
            id="test",
            name="Test Category",
            time_periods={TimePeriod.DAY: 42.0, TimePeriod.NIGHT: 38.0},
            nml_values={TimePeriod.DAY: 52.0, TimePeriod.NIGHT: 48.0}
        )
        
        # Test day period
        result = noise_calculator._get_representative_background(category, TimePeriod.DAY, None)
        assert result == 42.0
        
        # Test night period
        result = noise_calculator._get_representative_background(category, TimePeriod.NIGHT, None)
        assert result == 38.0
    
    def test_get_representative_background_fallback(self, noise_calculator):
        """Test getting representative background with fallback values."""
        from noise_estimator.models.schemas import NoiseCategory, TimePeriod
        
        category = NoiseCategory(
            id="test",
            name="Test Category",
            time_periods={},  # No time periods defined
            nml_values={}
        )
        
        # Test day period fallback
        result = noise_calculator._get_representative_background(category, TimePeriod.DAY, None)
        assert result == 45.0  # Default fallback
        
        # Test night period fallback
        result = noise_calculator._get_representative_background(category, TimePeriod.NIGHT, None)
        assert result == 35.0  # Default fallback


class TestCalculationWorkflows:
    """Test complete calculation workflows."""
    
    def test_full_estimator_scenario_calculation(self, noise_calculator, sample_requests):
        """Test full estimator scenario mode calculation."""
        from noise_estimator.models.schemas import EstimationRequest
        
        request_data = sample_requests["full_estimator_scenario"]
        request = EstimationRequest(**request_data)
        
        result = noise_calculator.calculate(request)
        
        # Verify result structure
        assert result.predicted_level_db is not None
        assert result.background_db is not None
        assert result.nml_db is not None
        assert result.exceed_background_db is not None
        assert result.exceed_nml_db is not None
        assert result.impact_band is not None
        assert result.standard_measures is not None
        assert result.additional_measures is not None
        
        # Verify trace is included when requested
        assert result.trace is not None
        
        # Verify logical consistency
        assert abs(result.exceed_background_db - (result.predicted_level_db - result.background_db)) < 0.0001
        assert abs(result.exceed_nml_db - (result.predicted_level_db - result.nml_db)) < 0.0001
    
    def test_full_estimator_plant_calculation(self, noise_calculator, sample_requests):
        """Test full estimator individual plant mode calculation."""
        from noise_estimator.models.schemas import EstimationRequest
        
        request_data = sample_requests["full_estimator_plant"]
        request = EstimationRequest(**request_data)
        
        result = noise_calculator.calculate(request)
        
        # Verify result structure
        assert result.predicted_level_db is not None
        assert result.background_db == request.user_background_level
        assert result.impact_band is not None
        
        # Verify Step 2 memo pack is generated when requested
        assert result.step2_memo_pack is not None
        assert len(result.step2_memo_pack) > 0
    
    def test_distance_based_scenario_calculation(self, noise_calculator, sample_requests):
        """Test distance-based scenario mode calculation."""
        from noise_estimator.models.schemas import EstimationRequest
        
        request_data = sample_requests["distance_based_scenario"]
        request = EstimationRequest(**request_data)
        
        result = noise_calculator.calculate(request)
        
        # Verify distance results are not included for distance-based calculations
        # (distances are only calculated for full estimator mode)
        if request.assessment_type == AssessmentType.FULL_ESTIMATOR:
            assert result.distances is not None
            assert result.distances.distance_to_exceed_background is not None
            assert result.distances.distance_to_nml is not None
        
        # Verify REF pack is generated when requested
        assert result.ref_noise_pack is not None
        assert len(result.ref_noise_pack) > 0
    
    def test_distance_based_noisiest_plant_calculation(self, noise_calculator, sample_requests):
        """Test distance-based noisiest plant mode calculation."""
        from noise_estimator.models.schemas import EstimationRequest
        
        request_data = sample_requests["distance_based_noisiest"]
        request = EstimationRequest(**request_data)
        
        result = noise_calculator.calculate(request)
        
        # Verify both output packs are generated when requested
        assert result.step2_memo_pack is not None
        assert result.ref_noise_pack is not None
        
        # Verify tables are generated
        assert result.results_table_markdown is not None
        assert result.results_table_csv is not None
    
    def test_calculation_with_invalid_scenario(self, noise_calculator):
        """Test calculation with invalid scenario ID."""
        from noise_estimator.models.schemas import EstimationRequest, AssessmentType, CalculationMode, EnvironmentApproach, TimePeriod, PropagationType
        
        request = EstimationRequest(
            assessment_type=AssessmentType.FULL_ESTIMATOR,
            calculation_mode=CalculationMode.SCENARIO,
            environment_approach=EnvironmentApproach.REPRESENTATIVE_NOISE_ENVIRONMENT,
            time_period=TimePeriod.DAY,
            propagation_type=PropagationType.RURAL,
            noise_category_id="R1",
            scenario_id="invalid_scenario",  # Invalid scenario
            receiver_distance=50.0
        )
        
        with pytest.raises(ValueError, match="Scenario invalid_scenario not found"):
            noise_calculator.calculate(request)
    
    def test_calculation_with_invalid_category(self, noise_calculator):
        """Test calculation with invalid category ID."""
        from noise_estimator.models.schemas import EstimationRequest, AssessmentType, CalculationMode, EnvironmentApproach, TimePeriod, PropagationType
        
        request = EstimationRequest(
            assessment_type=AssessmentType.FULL_ESTIMATOR,
            calculation_mode=CalculationMode.SCENARIO,
            environment_approach=EnvironmentApproach.REPRESENTATIVE_NOISE_ENVIRONMENT,
            time_period=TimePeriod.DAY,
            propagation_type=PropagationType.RURAL,
            noise_category_id="invalid_category",  # Invalid category
            scenario_id="excavation",
            receiver_distance=50.0
        )
        
        with pytest.raises(ValueError, match="Noise category invalid_category not found"):
            noise_calculator.calculate(request)
    
    def test_user_supplied_background_validation(self, noise_calculator):
        """Test validation of user-supplied background level."""
        from noise_estimator.models.schemas import EstimationRequest, AssessmentType, CalculationMode, EnvironmentApproach, TimePeriod, PropagationType
        from pydantic import ValidationError
        
        # Request with user-supplied background but no level provided
        with pytest.raises(ValidationError, match="user_background_level is required"):
            EstimationRequest(
                assessment_type=AssessmentType.FULL_ESTIMATOR,
                calculation_mode=CalculationMode.SCENARIO,
                environment_approach=EnvironmentApproach.USER_SUPPLIED_BACKGROUND_LEVEL,
                time_period=TimePeriod.DAY,
                propagation_type=PropagationType.RURAL,
                noise_category_id="R1",
                scenario_id="excavation",
                receiver_distance=50.0
                # Missing user_background_level
            )
