"""
Pydantic models and schemas for the noise estimator system.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator, model_validator


class AssessmentType(str, Enum):
    """Type of noise assessment."""
    DISTANCE_BASED = "distance_based"
    FULL_ESTIMATOR = "full_estimator"


class CalculationMode(str, Enum):
    """Calculation mode within assessment type."""
    SCENARIO = "scenario"
    INDIVIDUAL_PLANT = "individual_plant"
    NOISIEST_PLANT = "noisiest_plant"


class EnvironmentApproach(str, Enum):
    """Environment/background approach."""
    REPRESENTATIVE_NOISE_ENVIRONMENT = "representative_noise_environment"
    USER_SUPPLIED_BACKGROUND_LEVEL = "user_supplied_background_level"


class TimePeriod(str, Enum):
    """Time periods for noise assessment."""
    DAY = "day"
    EVENING = "evening"
    NIGHT = "night"
    DAY_EVENING = "day_evening"
    EVENING_NIGHT = "evening_night"
    DAY_EVENING_NIGHT = "day_evening_night"


class PropagationType(str, Enum):
    """Propagation/setting categories."""
    RURAL = "rural"
    URBAN = "urban"
    HARD_GROUND = "hard_ground"
    SOFT_GROUND = "soft_ground"
    MIXED = "mixed"


class ImpactBand(str, Enum):
    """Impact classification bands."""
    NOT_AFFECTED = "not_affected"
    MODERATELY_AFFECTED = "moderately_affected"
    HIGHLY_AFFECTED = "highly_affected"


class OutputPack(str, Enum):
    """Output pack options."""
    NONE = "none"
    STEP2 = "step2"
    REF = "ref"
    BOTH = "both"


class NoiseCategory(BaseModel):
    """Noise area category definition."""
    id: str
    name: str
    description: Optional[str] = None
    time_periods: Dict[TimePeriod, float] = Field(default_factory=dict)
    nml_values: Dict[TimePeriod, float] = Field(default_factory=dict)


class Scenario(BaseModel):
    """Noise scenario definition."""
    id: str
    name: str
    description: Optional[str] = None
    sound_power_levels: Dict[str, float] = Field(default_factory=dict)
    propagation_type: PropagationType
    applicable_measures: List[str] = Field(default_factory=list)


class Plant(BaseModel):
    """Individual plant/equipment definition."""
    id: str
    name: str
    description: Optional[str] = None
    sound_power_level: float
    category: Optional[str] = None
    duty_cycle: float = 1.0
    usage_factor: float = 1.0


class MitigationMeasure(BaseModel):
    """Mitigation measure definition."""
    id: str
    title: str
    text: str
    type: str  # "standard" or "additional"
    trigger_conditions: Dict[str, Any] = Field(default_factory=dict)
    reduction_db: Optional[float] = None


class EstimationRequest(BaseModel):
    """Request for noise estimation calculation."""
    assessment_type: AssessmentType
    calculation_mode: CalculationMode
    environment_approach: EnvironmentApproach
    time_period: TimePeriod
    propagation_type: PropagationType
    noise_category_id: str
    
    # Scenario or plant selection
    scenario_id: Optional[str] = None
    plant_ids: Optional[List[str]] = None
    
    # Distance parameters
    receiver_distance: Optional[float] = None  # For full estimator
    
    # Background level (for user_supplied approach)
    user_background_level: Optional[float] = None
    
    # Additional options
    include_trace: bool = False
    output_pack: OutputPack = OutputPack.NONE
    dataset_version: Optional[str] = None
    
    model_config = {"validate_assignment": True}
    
    @model_validator(mode='after')
    def validate_dependencies(self):
        """Validate cross-field dependencies."""
        if self.calculation_mode == CalculationMode.SCENARIO and not self.scenario_id:
            raise ValueError('scenario_id is required for scenario mode')
        
        if self.calculation_mode == CalculationMode.INDIVIDUAL_PLANT and not self.plant_ids:
            raise ValueError('plant_ids is required for individual plant mode')
        
        if self.assessment_type == AssessmentType.FULL_ESTIMATOR and not self.receiver_distance:
            raise ValueError('receiver_distance is required for full estimator')
        
        if self.environment_approach == EnvironmentApproach.USER_SUPPLIED_BACKGROUND_LEVEL and self.user_background_level is None:
            raise ValueError('user_background_level is required for user supplied background level')
        
        return self


class CalculationTrace(BaseModel):
    """Trace information for calculation auditability."""
    tables_used: Dict[str, Any] = Field(default_factory=dict)
    intermediate_values: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)


class DistanceResult(BaseModel):
    """Distance-based calculation results."""
    distance_to_exceed_background: Optional[float] = None
    distance_to_nml: Optional[float] = None
    distance_to_highly_affected: Optional[float] = None


class EstimationResult(BaseModel):
    """Complete noise estimation result."""
    request_id: str
    dataset_version: str
    workbook_hash: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Input summary
    resolved_inputs: Dict[str, Any] = Field(default_factory=dict)
    
    # Core results
    predicted_level_db: float
    background_db: float
    nml_db: float
    exceed_background_db: float
    exceed_nml_db: float
    impact_band: ImpactBand
    
    # Distance results (if applicable)
    distances: Optional[DistanceResult] = None
    
    # Mitigation measures
    standard_measures: List[MitigationMeasure] = Field(default_factory=list)
    additional_measures: List[MitigationMeasure] = Field(default_factory=list)
    
    # Traceability
    trace: Optional[CalculationTrace] = None
    
    # Narrative packs
    step2_memo_pack: Optional[str] = None
    ref_noise_pack: Optional[str] = None
    
    # Tables
    results_table_markdown: Optional[str] = None
    results_table_csv: Optional[str] = None


class DatasetMetadata(BaseModel):
    """Metadata for extracted datasets."""
    workbook_name: str
    extraction_timestamp: datetime
    workbook_hash: str
    version: str
    total_tables: int
    sheet_count: int


class TableMetadata(BaseModel):
    """Metadata for individual extracted tables."""
    name: str
    sheet_name: str
    cell_range: str
    column_types: Dict[str, str]
    row_count: int
    has_headers: bool = True


class ExtractedDataset(BaseModel):
    """Complete extracted dataset from workbook."""
    metadata: DatasetMetadata
    tables: Dict[str, Any] = Field(default_factory=dict)
    table_metadata: Dict[str, TableMetadata] = Field(default_factory=dict)


class ValidationError(BaseModel):
    """Validation error details."""
    field: str
    message: str
    value: Any


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    data: Optional[Any] = None
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    request_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    dataset_version: Optional[str] = None


class ListResponse(BaseModel):
    """Response for list endpoints."""
    items: List[Dict[str, Any]]
    total: int
    dataset_version: str
