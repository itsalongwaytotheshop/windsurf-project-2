"""
FastAPI REST service for the noise estimator system.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..core.dataset import DatasetManager
from ..core.calculator import NoiseCalculator
from ..models.schemas import (
    EstimationRequest,
    EstimationResult,
    HealthResponse,
    ListResponse,
    APIResponse,
    ValidationError,
    AssessmentType,
    CalculationMode,
    EnvironmentApproach,
    TimePeriod,
    PropagationType,
    OutputPack,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global components
dataset_manager: Optional[DatasetManager] = None
calculator: Optional[NoiseCalculator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global dataset_manager, calculator
    
    # Initialize components
    try:
        dataset_manager = DatasetManager()
        calculator = NoiseCalculator(dataset_manager)
        
        # Try to load default dataset
        try:
            dataset_manager.load_dataset()
            logger.info("Default dataset loaded successfully")
        except FileNotFoundError:
            logger.warning("No default dataset found. Please extract a dataset first.")
        
        logger.info("Noise Estimator API initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize API: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Noise Estimator API shutting down")


# Create FastAPI app
app = FastAPI(
    title="Noise Estimator API",
    description="REST API for Construction and Maintenance Noise Estimation",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get calculator
def get_calculator() -> NoiseCalculator:
    """Get calculator instance."""
    if calculator is None:
        raise HTTPException(status_code=503, detail="Calculator not initialized")
    return calculator


# Dependency to get dataset manager
def get_dataset_manager() -> DatasetManager:
    """Get dataset manager instance."""
    if dataset_manager is None:
        raise HTTPException(status_code=503, detail="Dataset manager not initialized")
    return dataset_manager


# Pydantic models for API endpoints
class EstimationRequestModel(BaseModel):
    """API model for estimation requests."""
    assessment_type: AssessmentType
    calculation_mode: CalculationMode
    environment_approach: EnvironmentApproach
    time_period: TimePeriod
    propagation_type: PropagationType
    noise_category_id: str
    scenario_id: Optional[str] = None
    plant_ids: Optional[List[str]] = None
    receiver_distance: Optional[float] = None
    user_background_level: Optional[float] = None
    include_trace: bool = False
    output_pack: OutputPack = OutputPack.NONE
    dataset_version: Optional[str] = None


class DatasetVersionParam(BaseModel):
    """Dataset version parameter."""
    version: Optional[str] = None


# Helper functions
def handle_validation_errors(func):
    """Decorator to handle validation errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    return wrapper


# API Endpoints

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        current_dataset = dataset_manager.get_current_dataset() if dataset_manager else None
        dataset_version = current_dataset.metadata.version if current_dataset else None
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            dataset_version=dataset_version
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version="1.0.0"
        )


@app.get("/meta", response_model=Dict[str, Any])
async def get_metadata(dataset_mgr: DatasetManager = Depends(get_dataset_manager)):
    """Get metadata about available datasets."""
    try:
        datasets = dataset_mgr.list_datasets()
        current_dataset = dataset_mgr.get_current_dataset()
        
        metadata = {
            "available_versions": datasets,
            "current_version": current_dataset.metadata.version if current_dataset else None,
            "total_datasets": len(datasets)
        }
        
        if current_dataset:
            metadata.update({
                "current_dataset_info": {
                    "workbook_name": current_dataset.metadata.workbook_name,
                    "extraction_timestamp": current_dataset.metadata.extraction_timestamp,
                    "total_tables": current_dataset.metadata.total_tables,
                    "table_names": list(current_dataset.tables.keys())
                }
            })
        
        return metadata
        
    except Exception as e:
        logger.error(f"Failed to get metadata: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metadata")


@app.get("/lists/scenarios", response_model=ListResponse)
async def list_scenarios(
    version: Optional[str] = Query(None, description="Dataset version"),
    dataset_mgr: DatasetManager = Depends(get_dataset_manager)
):
    """List available scenarios."""
    try:
        dataset = dataset_mgr.load_dataset(version)
        scenarios = dataset_mgr.get_scenarios(dataset)
        
        items = []
        for scen_id, scenario in scenarios.items():
            items.append({
                "id": scen_id,
                "name": scenario.name,
                "description": scenario.description,
                "propagation_type": scenario.propagation_type.value,
                "sound_power_levels": scenario.sound_power_levels
            })
        
        return ListResponse(
            items=items,
            total=len(items),
            dataset_version=dataset.metadata.version
        )
        
    except Exception as e:
        logger.error(f"Failed to list scenarios: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve scenarios")


@app.get("/lists/plants", response_model=ListResponse)
async def list_plants(
    version: Optional[str] = Query(None, description="Dataset version"),
    dataset_mgr: DatasetManager = Depends(get_dataset_manager)
):
    """List available plants."""
    try:
        dataset = dataset_mgr.load_dataset(version)
        plants = dataset_mgr.get_plants(dataset)
        
        items = []
        for plant_id, plant in plants.items():
            items.append({
                "id": plant_id,
                "name": plant.name,
                "description": plant.description,
                "sound_power_level": plant.sound_power_level,
                "category": plant.category,
                "duty_cycle": plant.duty_cycle,
                "usage_factor": plant.usage_factor
            })
        
        return ListResponse(
            items=items,
            total=len(items),
            dataset_version=dataset.metadata.version
        )
        
    except Exception as e:
        logger.error(f"Failed to list plants: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve plants")


@app.get("/lists/categories", response_model=ListResponse)
async def list_categories(
    version: Optional[str] = Query(None, description="Dataset version"),
    dataset_mgr: DatasetManager = Depends(get_dataset_manager)
):
    """List available noise categories."""
    try:
        dataset = dataset_mgr.load_dataset(version)
        categories = dataset_mgr.get_noise_categories(dataset)
        
        items = []
        for cat_id, category in categories.items():
            items.append({
                "id": cat_id,
                "name": category.name,
                "description": category.description,
                "time_periods": category.time_periods,
                "nml_values": category.nml_values
            })
        
        return ListResponse(
            items=items,
            total=len(items),
            dataset_version=dataset.metadata.version
        )
        
    except Exception as e:
        logger.error(f"Failed to list categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve categories")


@app.post("/estimate/full/scenario", response_model=APIResponse)
async def estimate_full_scenario(
    request: EstimationRequestModel,
    calc: NoiseCalculator = Depends(get_calculator)
):
    """Full estimator calculation for scenario mode."""
    try:
        # Convert to internal request model
        internal_request = EstimationRequest(**request.dict())
        
        # Validate request
        if internal_request.calculation_mode != CalculationMode.SCENARIO:
            raise HTTPException(
                status_code=400, 
                detail="This endpoint only supports scenario mode"
            )
        
        if internal_request.scenario_id is None:
            raise HTTPException(
                status_code=400,
                detail="scenario_id is required for scenario mode"
            )
        
        # Perform calculation
        result = calc.calculate(internal_request)
        
        return APIResponse(
            success=True,
            data=result.dict(),
            request_id=result.request_id
        )
        
    except ValueError as e:
        logger.error(f"Validation error in full scenario estimate: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in full scenario estimate: {e}")
        raise HTTPException(status_code=500, detail="Calculation failed")


@app.post("/estimate/full/plant", response_model=APIResponse)
async def estimate_full_plant(
    request: EstimationRequestModel,
    calc: NoiseCalculator = Depends(get_calculator)
):
    """Full estimator calculation for individual plant mode."""
    try:
        # Convert to internal request model
        internal_request = EstimationRequest(**request.dict())
        
        # Validate request
        if internal_request.calculation_mode != CalculationMode.INDIVIDUAL_PLANT:
            raise HTTPException(
                status_code=400,
                detail="This endpoint only supports individual plant mode"
            )
        
        if internal_request.plant_ids is None or not internal_request.plant_ids:
            raise HTTPException(
                status_code=400,
                detail="plant_ids is required for individual plant mode"
            )
        
        # Perform calculation
        result = calc.calculate(internal_request)
        
        return APIResponse(
            success=True,
            data=result.dict(),
            request_id=result.request_id
        )
        
    except ValueError as e:
        logger.error(f"Validation error in full plant estimate: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in full plant estimate: {e}")
        raise HTTPException(status_code=500, detail="Calculation failed")


@app.post("/estimate/distance/scenario", response_model=APIResponse)
async def estimate_distance_scenario(
    request: EstimationRequestModel,
    calc: NoiseCalculator = Depends(get_calculator)
):
    """Distance-based calculation for scenario mode."""
    try:
        # Convert to internal request model
        internal_request = EstimationRequest(**request.dict())
        
        # Validate request
        if internal_request.assessment_type != AssessmentType.DISTANCE_BASED:
            raise HTTPException(
                status_code=400,
                detail="This endpoint only supports distance-based assessment"
            )
        
        if internal_request.calculation_mode != CalculationMode.SCENARIO:
            raise HTTPException(
                status_code=400,
                detail="This endpoint only supports scenario mode"
            )
        
        if internal_request.scenario_id is None:
            raise HTTPException(
                status_code=400,
                detail="scenario_id is required for scenario mode"
            )
        
        # Perform calculation
        result = calc.calculate(internal_request)
        
        return APIResponse(
            success=True,
            data=result.dict(),
            request_id=result.request_id
        )
        
    except ValueError as e:
        logger.error(f"Validation error in distance scenario estimate: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in distance scenario estimate: {e}")
        raise HTTPException(status_code=500, detail="Calculation failed")


@app.post("/estimate/distance/noisiest_plant", response_model=APIResponse)
async def estimate_distance_noisiest_plant(
    request: EstimationRequestModel,
    calc: NoiseCalculator = Depends(get_calculator)
):
    """Distance-based calculation for noisiest plant mode."""
    try:
        # Convert to internal request model
        internal_request = EstimationRequest(**request.dict())
        
        # Validate request
        if internal_request.assessment_type != AssessmentType.DISTANCE_BASED:
            raise HTTPException(
                status_code=400,
                detail="This endpoint only supports distance-based assessment"
            )
        
        if internal_request.calculation_mode != CalculationMode.NOISIEST_PLANT:
            raise HTTPException(
                status_code=400,
                detail="This endpoint only supports noisiest plant mode"
            )
        
        if internal_request.scenario_id is None:
            raise HTTPException(
                status_code=400,
                detail="scenario_id is required for noisiest plant mode"
            )
        
        # Perform calculation
        result = calc.calculate(internal_request)
        
        return APIResponse(
            success=True,
            data=result.dict(),
            request_id=result.request_id
        )
        
    except ValueError as e:
        logger.error(f"Validation error in distance noisiest plant estimate: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in distance noisiest plant estimate: {e}")
        raise HTTPException(status_code=500, detail="Calculation failed")


@app.post("/estimate", response_model=APIResponse)
async def estimate_universal(
    request: EstimationRequestModel,
    calc: NoiseCalculator = Depends(get_calculator)
):
    """Universal estimation endpoint that handles all calculation types."""
    try:
        # Convert to internal request model
        internal_request = EstimationRequest(**request.dict())
        
        # Perform calculation
        result = calc.calculate(internal_request)
        
        return APIResponse(
            success=True,
            data=result.dict(),
            request_id=result.request_id
        )
        
    except ValueError as e:
        logger.error(f"Validation error in universal estimate: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in universal estimate: {e}")
        raise HTTPException(status_code=500, detail="Calculation failed")


@app.get("/datasets", response_model=Dict[str, Any])
async def list_datasets(dataset_mgr: DatasetManager = Depends(get_dataset_manager)):
    """List available datasets with detailed information."""
    try:
        datasets = dataset_mgr.list_datasets()
        dataset_info = {}
        
        for version in datasets:
            info = dataset_mgr.get_dataset_info(version)
            dataset_info[version] = info
        
        return {
            "datasets": dataset_info,
            "total": len(datasets),
            "current": dataset_mgr.get_current_dataset().metadata.version if dataset_mgr.get_current_dataset() else None
        }
        
    except Exception as e:
        logger.error(f"Failed to list datasets: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve datasets")


@app.post("/datasets/{version}/load")
async def load_dataset(
    version: str,
    dataset_mgr: DatasetManager = Depends(get_dataset_manager)
):
    """Load a specific dataset version."""
    try:
        dataset = dataset_mgr.load_dataset(version)
        
        return {
            "success": True,
            "message": f"Dataset {version} loaded successfully",
            "dataset_info": {
                "version": dataset.metadata.version,
                "workbook_name": dataset.metadata.workbook_name,
                "total_tables": dataset.metadata.total_tables
            }
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Dataset version {version} not found")
    except Exception as e:
        logger.error(f"Failed to load dataset {version}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load dataset")


@app.get("/validate/worked_examples", response_model=Dict[str, Any])
async def validate_worked_examples(
    version: Optional[str] = Query(None, description="Dataset version"),
    calc: NoiseCalculator = Depends(get_calculator),
    dataset_mgr: DatasetManager = Depends(get_dataset_manager)
):
    """Validate calculations against worked examples."""
    try:
        dataset = dataset_mgr.load_dataset(version)
        worked_examples = dataset.tables.get("worked_examples", [])
        
        if not worked_examples:
            return {
                "success": True,
                "message": "No worked examples found in dataset",
                "total_examples": 0,
                "passed": 0,
                "failed": 0
            }
        
        passed = 0
        failed = 0
        tolerance_db = 0.2
        tolerance_distance = 1.0
        results = []
        
        for example in worked_examples:
            try:
                # Create request from example inputs
                inputs = example["inputs"]
                request = EstimationRequest(**inputs)
                
                # Calculate result
                result = calc.calculate(request)
                
                # Get expected outputs
                expected = example["expected_outputs"]
                
                # Validate
                example_passed = True
                validation_details = {}
                
                for field, expected_value in expected.items():
                    if field.endswith("_db"):
                        actual_value = getattr(result, field, None)
                        if actual_value is None:
                            example_passed = False
                            validation_details[field] = {
                                "expected": expected_value,
                                "actual": None,
                                "difference": None,
                                "passed": False
                            }
                        else:
                            difference = abs(actual_value - expected_value)
                            passed_validation = difference <= tolerance_db
                            if not passed_validation:
                                example_passed = False
                            
                            validation_details[field] = {
                                "expected": expected_value,
                                "actual": actual_value,
                                "difference": difference,
                                "passed": passed_validation
                            }
                    
                    elif field.startswith("distance_to_"):
                        if result.distances is None:
                            example_passed = False
                            validation_details[field] = {
                                "expected": expected_value,
                                "actual": None,
                                "difference": None,
                                "passed": False
                            }
                        else:
                            actual_value = getattr(result.distances, field, None)
                            if actual_value is None:
                                example_passed = False
                                validation_details[field] = {
                                    "expected": expected_value,
                                    "actual": None,
                                    "difference": None,
                                    "passed": False
                                }
                            else:
                                difference = abs(actual_value - expected_value)
                                passed_validation = difference <= tolerance_distance
                                if not passed_validation:
                                    example_passed = False
                                
                                validation_details[field] = {
                                    "expected": expected_value,
                                    "actual": actual_value,
                                    "difference": difference,
                                    "passed": passed_validation
                                }
                    
                    elif field == "impact_band":
                        actual_value = result.impact_band.value
                        passed_validation = actual_value == expected_value
                        if not passed_validation:
                            example_passed = False
                        
                        validation_details[field] = {
                            "expected": expected_value,
                            "actual": actual_value,
                            "passed": passed_validation
                        }
                
                if example_passed:
                    passed += 1
                else:
                    failed += 1
                
                results.append({
                    "example_id": example.get("id", "Unknown"),
                    "description": example.get("description", ""),
                    "passed": example_passed,
                    "validation_details": validation_details
                })
                
            except Exception as e:
                failed += 1
                results.append({
                    "example_id": example.get("id", "Unknown"),
                    "description": example.get("description", ""),
                    "passed": False,
                    "error": str(e)
                })
        
        return {
            "success": failed == 0,
            "total_examples": len(worked_examples),
            "passed": passed,
            "failed": failed,
            "tolerance_db": tolerance_db,
            "tolerance_distance": tolerance_distance,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Failed to validate worked examples: {e}")
        raise HTTPException(status_code=500, detail="Validation failed")


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return APIResponse(
        success=False,
        errors=[{
            "field": "general",
            "message": exc.detail,
            "value": None
        }]
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return APIResponse(
        success=False,
        errors=[{
            "field": "general",
            "message": "Internal server error",
            "value": None
        }]
    )
