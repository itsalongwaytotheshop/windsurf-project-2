from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
import os
from datetime import datetime

# Add the parent directory to the path to import the noise estimator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from noise_estimator.core.calculator import NoiseCalculator
from noise_estimator.core.dataset import DatasetManager

app = FastAPI(title="Noise Estimator API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the calculator
try:
    dataset_manager = DatasetManager('datasets')
    calculator = NoiseCalculator(dataset_manager)
except Exception as e:
    print(f"Error initializing calculator: {e}")
    calculator = None

class EstimationRequest(BaseModel):
    assessment_type: str
    calculation_mode: str
    environment_approach: str
    time_period: str
    propagation_type: str
    noise_category_id: str
    scenario_id: Optional[str] = None
    plant_ids: Optional[List[str]] = None
    receiver_distance: Optional[float] = None
    user_background_level: Optional[float] = None
    include_trace: Optional[bool] = False

def get_notification_requirements(impact_band: str, distance: float, time_period: str) -> List[Dict[str, Any]]:
    """Generate notification requirements based on impact assessment."""
    requirements = []
    
    # Phone call requirements for affected stakeholders
    if impact_band in ["affected", "highly_affected"]:
        requirements.append({
            "type": "phone_call",
            "description": "Phone calls detailing relevant information made to identified/affected stakeholders within seven calendar days of proposed work",
            "timing": "7 days prior",
            "distance": distance if distance > 0 else None,
            "impactBand": impact_band
        })
    
    # Letter drop for highly affected areas
    if impact_band == "highly_affected":
        requirements.append({
            "type": "letter_drop",
            "description": "Letter drop to all properties within the affected distance with information about the proposed works",
            "timing": "7 days prior",
            "distance": distance if distance > 0 else None,
            "impactBand": impact_band
        })
    
    # Site signage
    requirements.append({
        "type": "site_sign",
        "description": "Site signage displaying contact information and work details",
        "timing": "24 hours prior",
        "distance": None,
        "impactBand": impact_band
    })
    
    # Newspaper notification for out of hours work
    if time_period in ["evening", "night"] and impact_band != "not_affected":
        requirements.append({
            "type": "newspaper",
            "description": "Newspaper notification for out of hours work as required by EPA guidelines",
            "timing": "7 days prior",
            "distance": None,
            "impactBand": impact_band
        })
    
    return requirements

def get_stakeholder_requirements(impact_band: str) -> List[Dict[str, Any]]:
    """Generate stakeholder communication requirements."""
    stakeholders = []
    
    # Affected residents
    if impact_band != "not_affected":
        stakeholders.append({
            "category": "affected_residents",
            "notificationMethods": ["phone_call", "letter_drop"],
            "specificRequirements": [
                "Provide work schedule and duration",
                "Offer contact details for complaints",
                "Inform about available respite periods"
            ],
            "contactTiming": "7 days prior to work commencement"
        })
    
    # Local businesses
    if impact_band == "highly_affected":
        stakeholders.append({
            "category": "local_business",
            "notificationMethods": ["phone_call", "email"],
            "specificRequirements": [
                "Discuss access requirements",
                "Coordinate delivery schedules",
                "Minimise disruption to operations"
            ],
            "contactTiming": "7 days prior to work commencement"
        })
    
    # Schools and hospitals (always notify if within affected distance)
    stakeholders.append({
        "category": "schools",
        "notificationMethods": ["phone_call", "email"],
        "specificRequirements": [
            "Coordinate work outside school hours where possible",
            "Provide advance notice of noisy activities",
            "Ensure safe access routes are maintained"
        ],
        "contactTiming": "14 days prior to work commencement"
    })
    
    stakeholders.append({
        "category": "hospitals",
        "notificationMethods": ["phone_call", "email"],
        "specificRequirements": [
            "Coordinate with hospital management",
            "Maintain emergency access at all times",
            "Avoid high-noise activities during critical periods"
        ],
        "contactTiming": "14 days prior to work commencement"
    })
    
    # Community groups
    if impact_band == "highly_affected":
        stakeholders.append({
            "category": "community_groups",
            "notificationMethods": ["email", "letter_drop"],
            "specificRequirements": [
                "Attend community meetings if requested",
                "Provide project updates regularly",
                "Establish community liaison contact"
            ],
            "contactTiming": "14 days prior to work commencement"
        })
    
    return stakeholders

def get_work_hour_restrictions(impact_band: str, time_period: str) -> List[Dict[str, Any]]:
    """Generate work hour restrictions based on impact assessment."""
    restrictions = []
    
    # Day time restrictions
    restrictions.append({
        "period": "day",
        "restrictions": [
            "Standard construction hours: 7am to 6pm Monday to Saturday",
            "No work on Sundays or public holidays (except emergency works)"
        ],
        "maxConsecutiveDays": 6,
        "separationRequired": 1,
        "maxPerMonth": 24,
        "specialConditions": []
    })
    
    # Evening restrictions
    if time_period == "evening" or impact_band != "not_affected":
        restrictions.append({
            "period": "evening",
            "restrictions": [
                "Limited to 6pm to 10pm",
                "Only lower-noise activities permitted",
                "Must have prior EPA approval for out of hours work"
            ],
            "maxConsecutiveDays": 3,
            "separationRequired": 1,
            "maxPerMonth": 9,
            "specialConditions": ["Requires EPA Section 115 approval"]
        })
    
    # Night restrictions
    if time_period == "night" or impact_band == "highly_affected":
        restrictions.append({
            "period": "night",
            "restrictions": [
                "Limited to 10pm to 7am",
                "Emergency works only",
                "Strict noise limits apply"
            ],
            "maxConsecutiveDays": 2,
            "separationRequired": 7,
            "maxPerMonth": 6,
            "specialConditions": ["Requires EPA Section 115 approval", "Must demonstrate genuine need"]
        })
    
    # Out of hours period 1
    restrictions.append({
        "period": "out_of_hours_1",
        "restrictions": [
            "No more than three consecutive evenings per week",
            "Periods separated by at least one week",
            "Maximum 6 evenings per month"
        ],
        "maxConsecutiveDays": 3,
        "separationRequired": 7,
        "maxPerMonth": 6,
        "specialConditions": []
    })
    
    # Out of hours period 2
    restrictions.append({
        "period": "out_of_hours_2",
        "restrictions": [
            "No more than two consecutive nights",
            "Periods separated by at least one week",
            "High noise works completed before 11pm"
        ],
        "maxConsecutiveDays": 2,
        "separationRequired": 7,
        "maxPerMonth": 6,
        "specialConditions": []
    })
    
    return restrictions

def get_respite_periods(impact_band: str) -> List[Dict[str, Any]]:
    """Generate respite period requirements."""
    respite = []
    
    if impact_band != "not_affected":
        respite.append({
            "id": "R1",
            "description": "Respite Period 1 - Out of hours construction noise limitations",
            "nightRestrictions": "Limited to no more than three consecutive evenings per week, separated by not less than one week",
            "eveningRestrictions": "Maximum 6 evenings per month, high noise works completed before 11pm",
            "separationRequirements": "Minimum one week separation between periods"
        })
    
    if impact_band == "highly_affected":
        respite.append({
            "id": "R2",
            "description": "Respite Period 2 - Stricter limitations for highly affected areas",
            "nightRestrictions": "Limited to two consecutive nights, separated by not less than one week",
            "eveningRestrictions": "Maximum 6 nights per month, additional mitigation required",
            "separationRequirements": "Minimum one week separation, additional monitoring required"
        })
    
    return respite

def get_compliance_requirements(impact_band: str) -> List[Dict[str, Any]]:
    """Generate compliance and approval requirements."""
    compliance = []
    
    # EPA requirements
    epa_requirements = [
        "Compliance with EPA Interim Construction Noise Guidelines",
        "Maintain noise levels below applicable criteria",
        "Implement all feasible and reasonable mitigation measures"
    ]
    
    if impact_band == "highly_affected":
        epa_requirements.extend([
            "Obtain Section 115 approval for out of hours work",
            "Prepare and implement Noise Management Plan",
            "Conduct pre and post work noise monitoring"
        ])
    
    compliance.append({
        "category": "EPA",
        "requirements": epa_requirements,
        "referenceNumbers": ["EPA ICNG", "Section 115 EPA Act"],
        "approvalNeeded": impact_band == "highly_affected",
        "timeframe": "Prior to work commencement"
    })
    
    # Council requirements
    council_requirements = [
        "Notify local council of proposed works",
        "Comply with local environmental planning policies"
    ]
    
    if impact_band != "not_affected":
        council_requirements.extend([
            "Submit Development Application (if required)",
            "Obtain Construction Certificate"
        ])
    
    compliance.append({
        "category": "council",
        "requirements": council_requirements,
        "referenceNumbers": ["LEP", "DCP"],
        "approvalNeeded": impact_band != "not_affected",
        "timeframe": "Prior to work commencement"
    })
    
    # Transport for NSW
    if impact_band != "not_affected":
        compliance.append({
            "category": "transport",
            "requirements": [
                "Comply with Transport for NSW construction noise guidelines",
                "Implement traffic management plans",
                "Maintain access to transport networks"
            ],
            "referenceNumbers": ["TfNSW D-15-02"],
            "approvalNeeded": False,
            "timeframe": "Prior to work commencement"
        })
    
    # WorkCover
    compliance.append({
        "category": "workcover",
        "requirements": [
            "Ensure worker safety in noisy environments",
            "Provide hearing protection where required",
            "Conduct noise risk assessments"
        ],
        "referenceNumbers": ["Work Health and Safety Act"],
        "approvalNeeded": False,
        "timeframe": "Ongoing"
    })
    
    return compliance

def generate_checklist(impact_band: str, time_period: str) -> List[str]:
    """Generate pre-work checklist items."""
    checklist = [
        "Complete noise impact assessment",
        "Identify all sensitive receivers",
        "Prepare stakeholder notification list",
        "Implement standard mitigation measures"
    ]
    
    if impact_band != "not_affected":
        checklist.extend([
            "Arrange phone calls to affected stakeholders",
            "Prepare letter drop materials",
            "Install site signage with contact details",
            "Establish complaint handling procedure"
        ])
    
    if impact_band == "highly_affected":
        checklist.extend([
            "Obtain EPA Section 115 approval",
            "Prepare detailed Noise Management Plan",
            "Arrange noise monitoring equipment",
            "Document additional mitigation measures",
            "Schedule respite periods"
        ])
    
    if time_period in ["evening", "night"]:
        checklist.extend([
            "Confirm out of hours work approval",
            "Prepare night work lighting plan",
            "Ensure adequate security arrangements"
        ])
    
    return checklist

@app.get("/")
async def root():
    return {"message": "Noise Estimator API is running"}

@app.get("/health")
async def health_check():
    if calculator is None:
        raise HTTPException(status_code=503, detail="Calculator not initialized")
    return {"status": "healthy", "calculator": "ready"}

@app.post("/calculate")
async def calculate_noise(request: EstimationRequest):
    if calculator is None:
        raise HTTPException(status_code=503, detail="Calculator not initialized")
    
    try:
        # Convert the request to the format expected by the calculator
        from noise_estimator.models.schemas import (
            EstimationRequest as EstimationRequestModel,
            AssessmentType, CalculationMode, EnvironmentApproach,
            TimePeriod, PropagationType
        )
        
        # Create the proper estimation request
        estimation_request = EstimationRequestModel(
            assessment_type=AssessmentType(request.assessment_type),
            calculation_mode=CalculationMode(request.calculation_mode),
            environment_approach=EnvironmentApproach(request.environment_approach),
            time_period=TimePeriod(request.time_period),
            propagation_type=PropagationType(request.propagation_type),
            noise_category_id=request.noise_category_id,
            scenario_id=request.scenario_id,
            plant_ids=request.plant_ids,
            receiver_distance=request.receiver_distance,
            user_background_level=request.user_background_level,
            include_trace=request.include_trace or False
        )
        
        # Perform the calculation
        result = calculator.calculate(estimation_request)
        
        # Generate comprehensive requirements based on results
        impact_band = result.impact_band.value if hasattr(result.impact_band, 'value') else str(result.impact_band)
        affected_distance = result.distances.distance_to_exceed_background if result.distances else None
        
        # Build comprehensive response
        comprehensive_result = {
            # Basic results
            "request_id": result.request_id,
            "predicted_level_db": result.predicted_level_db,
            "background_db": result.background_db,
            "nml_db": result.nml_db,
            "exceed_background_db": result.exceed_background_db,
            "exceed_nml_db": result.exceed_nml_db,
            "impact_band": impact_band,
            
            # Distance information
            "distances": {
                "distance_to_exceed_background": result.distances.distance_to_exceed_background if result.distances else None,
                "distance_to_nml": result.distances.distance_to_nml if result.distances else None,
                "distance_to_highly_affected": result.distances.distance_to_highly_affected if result.distances else None,
                "affected_distance": affected_distance
            },
            
            # Notification requirements
            "notification_requirements": get_notification_requirements(
                impact_band, 
                affected_distance or 0, 
                request.time_period
            ),
            
            "stakeholder_requirements": get_stakeholder_requirements(impact_band),
            
            # Work hour restrictions
            "work_hour_restrictions": get_work_hour_restrictions(impact_band, request.time_period),
            "respite_periods": get_respite_periods(impact_band),
            
            # Compliance
            "compliance_requirements": get_compliance_requirements(impact_band),
            
            # Mitigation measures
            "standard_measures": [
                {
                    "id": m.id,
                    "title": m.title,
                    "description": m.text,
                    "type": m.type,
                    "reduction_db": m.reduction_db,
                    "applicable": True,
                    "feasibility": "feasible",
                    "cost": "medium",
                    "implementation_time": "1-2 days"
                } for m in result.standard_measures
            ],
            "additional_measures": [
                {
                    "id": m.id,
                    "title": m.title,
                    "description": m.text,
                    "type": m.type,
                    "reduction_db": m.reduction_db,
                    "applicable": impact_band == "highly_affected",
                    "feasibility": "feasible" if impact_band == "highly_affected" else "not_required",
                    "cost": "high",
                    "implementation_time": "3-5 days"
                } for m in result.additional_measures
            ],
            
            # Documentation
            "step2_memo_pack": result.step2_memo_pack,
            "ref_noise_pack": result.ref_noise_pack,
            "checklist_items": generate_checklist(impact_band, request.time_period),
            
            # Trace information
            "trace": {
                "tables_used": list(result.trace.tables_used.keys()) if result.trace else [],
                "intermediate_values": result.trace.intermediate_values if result.trace else {},
                "warnings": result.trace.warnings if result.trace else [],
                "assumptions": result.trace.assumptions if result.trace else []
            }
        }
        
        return comprehensive_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
