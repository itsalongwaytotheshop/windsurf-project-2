"""
Core noise calculation engine.
Implements dB arithmetic, propagation calculations, and noise estimation logic.
"""

import math
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
import logging

import numpy as np
from scipy import optimize

from .dataset import DatasetManager
from ..models.schemas import (
    EstimationRequest, EstimationResult,
    AssessmentType, CalculationMode, EnvironmentApproach,
    TimePeriod, PropagationType, NoiseCategory, Scenario, Plant,
    MitigationMeasure, ImpactBand, DistanceResult, CalculationTrace
)

logger = logging.getLogger(__name__)


class NoiseCalculator:
    """Core noise calculation engine."""
    
    def __init__(self, dataset_manager: DatasetManager):
        """Initialize calculator with dataset manager.
        
        Args:
            dataset_manager: Dataset manager instance.
        """
        self.dataset_manager = dataset_manager
        self._tolerance_db = 0.2  # Default tolerance for calculations
    
    def calculate(self, request: EstimationRequest) -> EstimationResult:
        """Perform noise estimation calculation.
        
        Args:
            request: Estimation request parameters.
            
        Returns:
            Complete estimation result.
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Load dataset
        dataset = self.dataset_manager.load_dataset(request.dataset_version)
        
        # Initialize trace
        trace = CalculationTrace() if request.include_trace else None
        
        try:
            # Resolve inputs
            resolved_inputs = self._resolve_inputs(request, dataset, trace)
            
            # Perform calculation based on assessment type
            if request.assessment_type == AssessmentType.FULL_ESTIMATOR:
                result = self._calculate_full_estimator(request, resolved_inputs, dataset, trace)
            else:  # DISTANCE_BASED
                result = self._calculate_distance_based(request, resolved_inputs, dataset, trace)
            
            # Apply common post-processing
            result = self._post_process_result(result, request, resolved_inputs, dataset)
            
            logger.info(f"Calculation completed for request {request_id}")
            return result
            
        except Exception as e:
            logger.error(f"Calculation failed for request {request_id}: {e}")
            raise
    
    def _resolve_inputs(self, request: EstimationRequest, dataset, trace: Optional[CalculationTrace]) -> Dict[str, Any]:
        """Resolve and validate all inputs."""
        resolved = {
            "assessment_type": request.assessment_type,
            "calculation_mode": request.calculation_mode,
            "environment_approach": request.environment_approach,
            "time_period": request.time_period,
            "propagation_type": request.propagation_type,
            "noise_category_id": request.noise_category_id,
            "mode": AssessmentType.DISTANCE_BASED if request.assessment_type == AssessmentType.DISTANCE_BASED else AssessmentType.FULL_ESTIMATOR,
            "scenario_mode": CalculationMode.SCENARIO if request.calculation_mode in [CalculationMode.SCENARIO, CalculationMode.NOISIEST_PLANT] else CalculationMode.INDIVIDUAL_PLANT,
        }
        
        # Get noise category
        categories = self.dataset_manager.get_noise_categories(dataset)
        if request.noise_category_id not in categories:
            raise ValueError(f"Noise category {request.noise_category_id} not found")
        
        category = categories[request.noise_category_id]
        resolved["category"] = category
        
        # Get background level
        if request.environment_approach == EnvironmentApproach.REPRESENTATIVE_NOISE_ENVIRONMENT:
            background = self._get_representative_background(category, request.time_period, dataset)
        else:
            background = request.user_background_level
        
        resolved["background_level"] = background
        
        # Get NML
        nml = category.nml_values.get(request.time_period, 50.0)  # Default fallback
        resolved["nml_level"] = nml
        
        # Resolve scenario or plants
        if request.calculation_mode in [CalculationMode.SCENARIO, CalculationMode.NOISIEST_PLANT]:
            scenarios = self.dataset_manager.get_scenarios(dataset)
            if request.scenario_id not in scenarios:
                raise ValueError(f"Scenario {request.scenario_id} not found")
            
            scenario = scenarios[request.scenario_id]
            resolved["scenario"] = scenario
            
        if request.calculation_mode in [CalculationMode.INDIVIDUAL_PLANT]:
            plants = self.dataset_manager.get_plants(dataset)
            resolved_plants = []
            for plant_id in request.plant_ids:
                if plant_id not in plants:
                    raise ValueError(f"Plant {plant_id} not found")
                resolved_plants.append(plants[plant_id])
            resolved["plants"] = resolved_plants
        
        # Distance for full estimator
        if request.assessment_type == AssessmentType.FULL_ESTIMATOR:
            resolved["receiver_distance"] = request.receiver_distance
        
        # Distance for distance-based calculations
        if request.assessment_type == AssessmentType.DISTANCE_BASED:
            # For distance-based, the receiver_distance is used as the calculation distance
            resolved["distance"] = request.receiver_distance or 100.0
        
        # Add to trace
        if trace:
            trace.assumptions.append(f"Using {request.environment_approach.value} background approach")
            trace.assumptions.append(f"Propagation type: {request.propagation_type.value}")
            trace.assumptions.append(f"Time period: {request.time_period.value}")
        
        return resolved
    
    def _calculate_full_estimator(self, request: EstimationRequest, inputs: Dict[str, Any], dataset, trace: Optional[CalculationTrace]) -> EstimationResult:
        """Calculate full estimator results."""
        distance = inputs["receiver_distance"]
        background = inputs["background_level"]
        nml = inputs["nml_level"]
        
        # Calculate source levels
        if request.calculation_mode == CalculationMode.SCENARIO:
            source_level = self._calculate_scenario_level(inputs["scenario"], inputs, dataset, trace)
        else:  # INDIVIDUAL_PLANT
            source_level = self._calculate_plants_level(inputs["plants"], inputs, dataset, trace)
        
        # Apply propagation
        received_level = self._apply_propagation(source_level, distance, inputs["propagation_type"], dataset, trace)
        
        # Calculate exceedances
        exceed_background = received_level - background
        exceed_nml = received_level - nml
        
        # Determine impact band
        impact_band = self._determine_impact_band(exceed_background, exceed_nml, dataset)
        
        # Get mitigation measures
        standard_measures, additional_measures = self._get_mitigation_measures(
            impact_band, inputs, dataset, trace
        )
        
        # Create result
        result = EstimationResult(
            request_id=str(uuid.uuid4()),
            dataset_version=dataset.metadata.version,
            workbook_hash=dataset.metadata.workbook_hash,
            resolved_inputs=inputs,
            predicted_level_db=received_level,
            background_db=background,
            nml_db=nml,
            exceed_background_db=exceed_background,
            exceed_nml_db=exceed_nml,
            impact_band=impact_band,
            standard_measures=standard_measures,
            additional_measures=additional_measures,
            trace=trace
        )
        
        return result
    
    def _calculate_distance_based(self, request: EstimationRequest, inputs: Dict[str, Any], dataset, trace: Optional[CalculationTrace]) -> EstimationResult:
        """Calculate distance-based results."""
        background = inputs["background_level"]
        nml = inputs["nml_level"]
        
        # For distance-based mode, calculate at the specified distance
        if inputs["mode"] == AssessmentType.DISTANCE_BASED:
            if inputs["scenario_mode"] == CalculationMode.SCENARIO:
                # For scenario mode, calculate combined level at distance
                received_level = self._calculate_scenario_level_at_distance(
                    inputs["scenario"], inputs["distance"], inputs["propagation_type"], 
                    dataset, trace
                )
            else:  # NOISIEST_PLANT
                # For noisiest plant mode, find the highest SWL and calculate at distance
                source_level = self._calculate_noisiest_plant_level(inputs, dataset, trace)
                received_level = self._apply_propagation(
                    source_level, inputs["distance"], inputs["propagation_type"], 
                    dataset, trace
                )
        else:  # FULL_ESTIMATOR
            # For full estimator, we need to find distances to thresholds
            if inputs["scenario_mode"] == CalculationMode.SCENARIO:
                source_level = self._calculate_scenario_level(inputs["scenario"], inputs, dataset, trace)
            else:  # NOISIEST_PLANT
                source_level = self._calculate_noisiest_plant_level(inputs, dataset, trace)
            
            # Calculate distances to thresholds
            distances = self._calculate_distances_to_thresholds(
                source_level, background, nml, inputs["propagation_type"], dataset, trace
            )
            
            # For full estimator, use a reference distance for the result
            reference_distance = distances.distance_to_exceed_background or 100.0
            received_level = self._apply_propagation(
                source_level, reference_distance, inputs["propagation_type"], 
                dataset, trace
            )
        
        # For distance-based calculations, distances are not calculated
        # Create empty distances object
        distances = DistanceResult(
            distance_to_exceed_background=None,
            distance_to_nml=None,
            distance_to_highly_affected=None
        )
        
        # Calculate exceedances at reference distance
        exceed_background = received_level - background
        exceed_nml = received_level - nml
        
        # Determine impact band
        impact_band = self._determine_impact_band(exceed_background, exceed_nml, dataset)
        
        # Get mitigation measures
        standard_measures, additional_measures = self._get_mitigation_measures(
            impact_band, inputs, dataset, trace
        )
        
        # Create result
        result = EstimationResult(
            request_id=str(uuid.uuid4()),
            dataset_version=dataset.metadata.version,
            workbook_hash=dataset.metadata.workbook_hash,
            resolved_inputs=inputs,
            predicted_level_db=received_level,
            background_db=background,
            nml_db=nml,
            exceed_background_db=exceed_background,
            exceed_nml_db=exceed_nml,
            impact_band=impact_band,
            distances=distances,
            standard_measures=standard_measures,
            additional_measures=additional_measures,
            trace=trace
        )
        
        return result
    
    def _calculate_scenario_level_at_distance(self, scenario: Scenario, distance: float, propagation_type: str, dataset, trace: Optional[CalculationTrace]) -> float:
        """Calculate combined level for a scenario at a specific distance."""
        # This is similar to _calculate_scenario_level but for a specific distance
        
        if trace:
            trace.tables_used["scenarios"] = scenario.id
            trace.intermediate_values["scenario_swl"] = scenario.sound_power_levels
        
        # Calculate each plant's contribution at the receiver
        linear_contributions = []
        
        for plant_id, swl in scenario.sound_power_levels.items():
            # Calculate received level for this plant
            received_level = self._apply_propagation(swl, distance, propagation_type, dataset, None)
            
            # Convert to linear units for summing
            linear_level = 10 ** (received_level / 10)
            linear_contributions.append(linear_level)
            
            if trace:
                trace.intermediate_values[f"plant_{plant_id}_received_level"] = received_level
                trace.intermediate_values[f"plant_{plant_id}_linear"] = linear_level
        
        # Sum in linear units and convert back to dB
        if linear_contributions:
            total_linear = sum(linear_contributions)
            combined_level = 10 * math.log10(total_linear)
            
            if trace:
                trace.intermediate_values["total_linear_sum"] = total_linear
                trace.intermediate_values["combined_level_db"] = combined_level
            
            return combined_level
        else:
            raise ValueError(f"No sound power levels found for scenario {scenario.id}")
    
    def _calculate_scenario_level(self, scenario: Scenario, inputs: Dict[str, Any], dataset, trace: Optional[CalculationTrace]) -> float:
        """Calculate combined sound power level for a scenario."""
        # For full estimator mode, we need the SWL, not the received level
        # The propagation will be applied later
        
        if trace:
            trace.tables_used["scenarios"] = scenario.id
            trace.intermediate_values["scenario_swl"] = scenario.sound_power_levels
        
        # If scenario has multiple SWL values, combine them using dB sum
        swl_values = list(scenario.sound_power_levels.values())
        if not swl_values:
            raise ValueError(f"No sound power levels found for scenario {scenario.id}")
        
        if len(swl_values) == 1:
            return swl_values[0]
        else:
            # Use dB summing for multiple sources
            total_linear = sum(10 ** (swl / 10) for swl in swl_values)
            combined_swl = 10 * math.log10(total_linear)
            
            if trace:
                trace.intermediate_values["total_linear_swl_sum"] = total_linear
                trace.intermediate_values["combined_swl_db"] = combined_swl
            
            return combined_swl
    
    def _calculate_plants_level(self, plants: List[Plant], inputs: Dict[str, Any], dataset, trace: Optional[CalculationTrace]) -> float:
        """Calculate combined sound power level for multiple plants."""
        if trace:
            trace.tables_used["plants"] = [plant.id for plant in plants]
        
        # Apply duty cycle and usage factors
        adjusted_levels = []
        for plant in plants:
            adjusted_level = plant.sound_power_level + 10 * math.log10(plant.duty_cycle * plant.usage_factor)
            adjusted_levels.append(adjusted_level)
            
            if trace:
                trace.intermediate_values[f"plant_{plant.id}_adjusted_swl"] = adjusted_level
        
        return self._db_sum(adjusted_levels)
    
    def _calculate_noisiest_plant_level(self, inputs: Dict[str, Any], dataset, trace: Optional[CalculationTrace]) -> float:
        """Calculate sound power level for noisiest plant in scenario."""
        # For noisiest plant mode, find the highest SWL in the scenario
        scenario = inputs["scenario"]
        swl_values = list(scenario.sound_power_levels.values())
        
        if not swl_values:
            raise ValueError(f"No sound power levels found for scenario {scenario.id}")
        
        noisiest_swl = max(swl_values)
        
        if trace:
            trace.intermediate_values["noisiest_plant_swl"] = noisiest_swl
        
        return noisiest_swl
    
    def _apply_propagation(self, source_level: float, distance: float, propagation_type: str, dataset, trace: Optional[CalculationTrace], barrier_adjustment: float = 0) -> float:
        """Apply propagation attenuation using Concawe model."""
        if distance <= 0:
            raise ValueError("Distance must be positive")
        
        # Get Concawe attenuation data
        concawe_data = self.dataset_manager.get_concawe_data(dataset)
        
        # Round distance to nearest table value
        rounded_distance = round(distance)
        
        # Find the closest distance in the table
        available_distances = sorted([int(d) for d in concawe_data.keys() if d is not None])
        if not available_distances:
            # If no Concawe data available, fall back to simple geometric spreading
            if trace:
                trace.warnings.append("No Concawe data available, using geometric spreading")
            geometric_spreading = 20 * math.log10(distance)
            return source_level - geometric_spreading + barrier_adjustment
        
        closest_distance = min(available_distances, key=lambda x: abs(x - rounded_distance))
        
        # Get attenuation for the propagation type
        propagation_map = {
            "Water": "hard",
            "Developed settlements (urban and suburban areas)": "urban", 
            "Rural": "rural"
        }
        
        prop_key = propagation_map.get(propagation_type, "rural")
        attenuation_at_distance = concawe_data.get(str(closest_distance), {}).get(prop_key, 0)
        
        # Calculate received level using Excel formula logic:
        # Level = SWL - 110 + ConcaweAttenuation + BarrierAdjustment
        # The -110 is a reference adjustment used in the Excel workbook
        received_level = source_level - 110 + attenuation_at_distance + barrier_adjustment
        
        if trace:
            trace.intermediate_values.update({
                "concawe_distance_used": closest_distance,
                "concawe_attenuation": attenuation_at_distance,
                "barrier_adjustment": barrier_adjustment,
                "received_level": received_level
            })
        
        return received_level
    
    def _get_ground_absorption(self, distance: float, propagation_type: PropagationType, propagation_data: Dict[str, Any]) -> float:
        """Get ground absorption based on propagation type and distance."""
        # Default ground absorption values (dB per doubling of distance)
        # These would typically come from the dataset
        ground_factors = {
            PropagationType.RURAL: 1.5,      # Soft ground, high absorption
            PropagationType.URBAN: 0.5,      # Mixed ground, moderate absorption
            PropagationType.HARD_GROUND: 0.0, # Hard ground, minimal absorption
            PropagationType.SOFT_GROUND: 2.0, # Very soft ground, high absorption
            PropagationType.MIXED: 1.0,       # Mixed conditions
        }
        
        factor = ground_factors.get(propagation_type, 1.0)
        
        # Apply factor based on distance (simplified model)
        # In reality, this would use more complex tables from the workbook
        if distance <= 10:
            return factor * 0.5
        elif distance <= 100:
            return factor * 1.0
        else:
            return factor * 1.5
    
    def _calculate_distances_to_thresholds(self, source_level: float, background: float, nml: float, propagation_type: PropagationType, dataset, trace: Optional[CalculationTrace]) -> DistanceResult:
        """Calculate distances to various thresholds using goal seek/inversion."""
        
        def level_at_distance(d: float) -> float:
            """Helper function to get level at a given distance."""
            return self._apply_propagation(source_level, d, propagation_type, dataset, None)
        
        # Calculate distance to exceed background
        distance_to_background = self._find_distance_for_level(
            source_level, background, propagation_type, dataset, "background"
        )
        
        # Calculate distance to NML
        distance_to_nml = self._find_distance_for_level(
            source_level, nml, propagation_type, dataset, "nml"
        )
        
        # Calculate distance to highly affected threshold
        # Typically defined as background + 10dB or similar
        highly_affected_threshold = background + 10.0
        distance_to_highly_affected = self._find_distance_for_level(
            source_level, highly_affected_threshold, propagation_type, dataset, "highly_affected"
        )
        
        distances = DistanceResult(
            distance_to_exceed_background=distance_to_background,
            distance_to_nml=distance_to_nml,
            distance_to_highly_affected=distance_to_highly_affected
        )
        
        if trace:
            trace.intermediate_values.update({
                "distance_to_background": distance_to_background,
                "distance_to_nml": distance_to_nml,
                "distance_to_highly_affected": distance_to_highly_affected
            })
        
        return distances
    
    def _find_distance_for_level(self, source_level: float, target_level: float, propagation_type: PropagationType, dataset, target_name: str) -> Optional[float]:
        """Find distance that results in target level using numerical methods."""
        
        def level_difference(d: float) -> float:
            """Difference between actual level and target at distance d."""
            actual_level = self._apply_propagation(source_level, d, propagation_type, dataset, None)
            return actual_level - target_level
        
        # Check if target is achievable
        level_at_1m = level_difference(1.0)
        level_at_1000m = level_difference(1000.0)
        
        # If the level is already below target at 1m, distance is 1m
        if level_at_1m <= 0:
            return 1.0
        
        # If the level is still above target at 1000m, we can't find a solution
        if level_at_1000m > 0:
            logger.warning(f"Cannot achieve {target_name} level of {target_level}dB at distances up to 1000m")
            return None
        
        try:
            # Use binary search to find distance
            result = optimize.brentq(
                level_difference,
                1.0,
                1000.0,
                xtol=0.1,  # 0.1m precision
                rtol=0.01   # 1% relative tolerance
            )
            return round(result, 1)
            
        except (ValueError, RuntimeError) as e:
            logger.warning(f"Failed to find distance for {target_name}: {e}")
            return None
    
    def _determine_impact_band(self, exceed_background: float, exceed_nml: float, dataset) -> ImpactBand:
        """Determine impact band based on exceedances."""
        # These thresholds would typically come from the dataset
        # Default implementation:
        
        if exceed_nml <= 0:
            return ImpactBand.NOT_AFFECTED
        elif exceed_nml <= 5:
            return ImpactBand.MODERATELY_AFFECTED
        else:
            return ImpactBand.HIGHLY_AFFECTED
    
    def _get_mitigation_measures(self, impact_band: ImpactBand, inputs: Dict[str, Any], dataset, trace: Optional[CalculationTrace]) -> Tuple[List[MitigationMeasure], List[MitigationMeasure]]:
        """Get applicable mitigation measures."""
        measures = self.dataset_manager.get_mitigation_measures(dataset)
        
        standard_measures = []
        additional_measures = []
        
        for measure in measures.values():
            # Check if measure is applicable based on impact band and other conditions
            if self._is_measure_applicable(measure, impact_band, inputs):
                if measure.type == "standard":
                    standard_measures.append(measure)
                else:
                    additional_measures.append(measure)
        
        if trace:
            trace.tables_used["mitigation_measures"] = [m.id for m in standard_measures + additional_measures]
        
        return standard_measures, additional_measures
    
    def _is_measure_applicable(self, measure: MitigationMeasure, impact_band: ImpactBand, inputs: Dict[str, Any]) -> bool:
        """Check if a mitigation measure is applicable."""
        # Simple implementation - in reality, this would use complex logic from the workbook
        conditions = measure.trigger_conditions
        
        # Check impact band condition
        if "impact_band" in conditions:
            required_bands = conditions["impact_band"]
            if isinstance(required_bands, str):
                required_bands = [required_bands]
            if impact_band.value not in required_bands:
                return False
        
        # Check other conditions
        for condition, value in conditions.items():
            if condition in inputs and inputs[condition] != value:
                return False
        
        return True
    
    def _get_representative_background(self, category: NoiseCategory, time_period: TimePeriod, dataset) -> float:
        """Get representative background level for category and time period."""
        # Try to get from category first
        if time_period in category.time_periods:
            return category.time_periods[time_period]
        
        # Fall back to background levels table
        background_data = self.dataset_manager.get_background_levels(dataset)
        
        for entry in background_data:
            if (entry.get("category") == category.id and 
                entry.get("time_period") == time_period.value):
                return entry.get("level", 45.0)  # Default fallback
        
        # Default background levels if no data found
        defaults = {
            TimePeriod.DAY: 45.0,
            TimePeriod.EVENING: 40.0,
            TimePeriod.NIGHT: 35.0,
        }
        
        return defaults.get(time_period, 40.0)
    
    def _db_sum(self, levels: List[float]) -> float:
        """Sum multiple dB levels using log-summing."""
        if not levels:
            return 0.0
        
        if len(levels) == 1:
            return levels[0]
        
        # Convert to linear, sum, convert back to dB
        linear_sum = sum(10 ** (level / 10) for level in levels)
        return 10 * math.log10(linear_sum)
    
    def _post_process_result(self, result: EstimationResult, request: EstimationRequest, inputs: Dict[str, Any], dataset) -> EstimationResult:
        """Apply post-processing to results."""
        # Round values appropriately
        result.predicted_level_db = round(result.predicted_level_db, 1)
        result.background_db = round(result.background_db, 1)
        result.nml_db = round(result.nml_db, 1)
        result.exceed_background_db = round(result.exceed_background_db, 1)
        result.exceed_nml_db = round(result.exceed_nml_db, 1)
        
        # Generate output packs if requested
        if request.output_pack.value in ["step2", "both"]:
            result.step2_memo_pack = self._generate_step2_memo(result, inputs)
        
        if request.output_pack.value in ["ref", "both"]:
            result.ref_noise_pack = self._generate_ref_noise_section(result, inputs)
        
        # Generate tables
        result.results_table_markdown = self._generate_results_table_markdown(result)
        result.results_table_csv = self._generate_results_table_csv(result)
        
        return result
    
    def _generate_step2_memo(self, result: EstimationResult, inputs: Dict[str, Any]) -> str:
        """Generate Step 2 memo paragraph pack."""
        lines = []
        
        # Assessment summary
        assessment_type = "full estimator" if inputs["assessment_type"].value == "full_estimator" else "distance-based"
        mode = inputs["calculation_mode"].value.replace("_", " ")
        
        lines.append(f"A noise assessment was conducted using the {assessment_type} approach in {mode} mode.")
        lines.append(f"The assessment considered {inputs['time_period'].value} time period conditions")
        lines.append(f"for the {inputs['category'].name} noise category ({inputs['noise_category_id']}).")
        
        # Background approach
        if inputs["environment_approach"].value == "representative_noise_environment":
            lines.append(f"A representative background noise level of {result.background_db} dB was used.")
        else:
            lines.append(f"A user-supplied background noise level of {result.background_db} dB was used.")
        
        # Results
        lines.append(f"The predicted noise level at the receiver is {result.predicted_level_db} dB LAeq(15min),")
        lines.append(f"which exceeds the background by {result.exceed_background_db} dB")
        lines.append(f"and the applicable Noise Management Level by {result.exceed_nml_db} dB.")
        
        # Impact classification
        lines.append(f"The impact is classified as {result.impact_band.value.replace('_', ' ')}.")
        
        # Mitigation
        if result.standard_measures:
            measures_text = ", ".join(m.title for m in result.standard_measures[:3])
            lines.append(f"Standard mitigation measures include: {measures_text}.")
        
        if result.additional_measures:
            measures_text = ", ".join(m.title for m in result.additional_measures[:2])
            lines.append(f"Additional measures recommended: {measures_text}.")
        
        # Key assumptions
        lines.append(f"Key assumptions include {inputs['propagation_type'].value} propagation conditions")
        if "receiver_distance" in inputs:
            lines.append(f"and a receiver distance of {inputs['receiver_distance']} m.")
        else:
            lines.append("with distances calculated to relevant thresholds.")
        
        return "\n".join(lines)
    
    def _generate_ref_noise_section(self, result: EstimationResult, inputs: Dict[str, Any]) -> str:
        """Generate REF noise section paragraph pack."""
        lines = []
        
        # Methodology
        lines.append("## Noise Assessment Methodology")
        lines.append("")
        lines.append("The noise assessment was conducted using the EMF-NV-TT-0067 Construction and Maintenance")
        lines.append("Noise Estimator (Roads) methodology. This approach aligns with industry standard")
        lines.append("practices for construction noise prediction and assessment.")
        lines.append("")
        
        # Assessment parameters
        lines.append("### Assessment Parameters")
        lines.append("")
        lines.append(f"- **Assessment Type**: {inputs['assessment_type'].value.replace('_', ' ').title()}")
        lines.append(f"- **Calculation Mode**: {inputs['calculation_mode'].value.replace('_', ' ').title()}")
        lines.append(f"- **Noise Category**: {inputs['category'].name} ({inputs['noise_category_id']})")
        lines.append(f"- **Time Period**: {inputs['time_period'].value.title()}")
        lines.append(f"- **Propagation Conditions**: {inputs['propagation_type'].value.replace('_', ' ').title()}")
        
        if inputs["environment_approach"].value == "representative_noise_environment":
            lines.append(f"- **Background Level**: Representative ({result.background_db} dB)")
        else:
            lines.append(f"- **Background Level**: User supplied ({result.background_db} dB)")
        
        lines.append(f"- **Noise Management Level**: {result.nml_db} dB")
        
        if "receiver_distance" in inputs:
            lines.append(f"- **Receiver Distance**: {inputs['receiver_distance']} m")
        
        lines.append("")
        
        # Results summary
        lines.append("### Assessment Results")
        lines.append("")
        lines.append(f"The predicted noise level at the receiver location is {result.predicted_level_db} dB")
        lines.append(f"LAeq(15min). This represents an exceedance of {result.exceed_background_db} dB above")
        lines.append(f"the background level and {result.exceed_nml_db} dB above the applicable Noise")
        lines.append(f"Management Level. The impact is classified as {result.impact_band.value.replace('_', ' ').title()}.")
        lines.append("")
        
        # Mitigation measures
        lines.append("### Mitigation Measures")
        lines.append("")
        
        if result.standard_measures:
            lines.append("#### Standard Measures")
            for measure in result.standard_measures:
                lines.append(f"- {measure.title}: {measure.text}")
            lines.append("")
        
        if result.additional_measures:
            lines.append("#### Additional Measures")
            for measure in result.additional_measures:
                lines.append(f"- {measure.title}: {measure.text}")
            lines.append("")
        
        # Residual impact
        lines.append("### Residual Impact Statement")
        lines.append("")
        if result.exceed_nml_db <= 0:
            lines.append("With the implementation of standard mitigation measures, the predicted noise levels")
            lines.append("are expected to remain within the applicable Noise Management Level.")
        else:
            lines.append(f"Even with the implementation of standard and additional mitigation measures,")
            lines.append(f"a residual exceedance of {result.exceed_nml_db} dB above the Noise Management Level is")
            lines.append("anticipated. Further mitigation or alternative construction methods should be considered.")
        
        return "\n".join(lines)
    
    def _generate_results_table_markdown(self, result: EstimationResult) -> str:
        """Generate results table in markdown format."""
        lines = []
        lines.append("| Parameter | Value |")
        lines.append("|-----------|-------|")
        lines.append(f"| Predicted Level | {result.predicted_level_db} dB |")
        lines.append(f"| Background Level | {result.background_db} dB |")
        lines.append(f"| Noise Management Level | {result.nml_db} dB |")
        lines.append(f"| Exceedance Above Background | {result.exceed_background_db} dB |")
        lines.append(f"| Exceedance Above NML | {result.exceed_nml_db} dB |")
        lines.append(f"| Impact Band | {result.impact_band.value.replace('_', ' ').title()} |")
        
        if result.distances:
            if result.distances.distance_to_exceed_background:
                lines.append(f"| Distance to Exceed Background | {result.distances.distance_to_exceed_background} m |")
            if result.distances.distance_to_nml:
                lines.append(f"| Distance to NML | {result.distances.distance_to_nml} m |")
            if result.distances.distance_to_highly_affected:
                lines.append(f"| Distance to Highly Affected | {result.distances.distance_to_highly_affected} m |")
        
        return "\n".join(lines)
    
    def _generate_results_table_csv(self, result: EstimationResult) -> str:
        """Generate results table in CSV format."""
        lines = []
        lines.append("Parameter,Value")
        lines.append(f"Predicted Level,{result.predicted_level_db} dB")
        lines.append(f"Background Level,{result.background_db} dB")
        lines.append(f"Noise Management Level,{result.nml_db} dB")
        lines.append(f"Exceedance Above Background,{result.exceed_background_db} dB")
        lines.append(f"Exceedance Above NML,{result.exceed_nml_db} dB")
        lines.append(f"Impact Band,{result.impact_band.value.replace('_', ' ').title()}")
        
        if result.distances:
            if result.distances.distance_to_exceed_background:
                lines.append(f"Distance to Exceed Background,{result.distances.distance_to_exceed_background} m")
            if result.distances.distance_to_nml:
                lines.append(f"Distance to NML,{result.distances.distance_to_nml} m")
            if result.distances.distance_to_highly_affected:
                lines.append(f"Distance to Highly Affected,{result.distances.distance_to_highly_affected} m")
        
        return "\n".join(lines)
