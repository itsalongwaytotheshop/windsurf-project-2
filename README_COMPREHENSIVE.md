# Comprehensive Noise Estimator Application

A full-featured noise estimation tool with compliance requirements, notifications, and stakeholder management for construction and maintenance projects.

## Features

### Core Functionality
- **Noise Level Calculations**: Calculate predicted noise levels based on various scenarios
- **Impact Assessment**: Determine if areas are NOT_AFFECTED, AFFECTED, or HIGHLY_AFFECTED
- **Distance Analysis**: Calculate affected distances and exceedance zones
- **Multiple Assessment Types**: Distance-based and Full Estimator modes
- **Scenario Support**: Pre-defined work scenarios (excavation, paving, etc.)

### Compliance & Requirements
- **Notification Requirements**: Automatically generates required notifications based on impact level
  - Phone calls to affected stakeholders
  - Letter drops for highly affected areas
  - Site signage requirements
  - Newspaper notifications for out-of-hours work
- **Stakeholder Management**: Identifies and provides communication requirements for:
  - Affected residents
  - Local businesses
  - Schools and hospitals
  - Community groups
- **Work Hour Restrictions**: Detailed restrictions for different time periods
  - Standard day work hours
  - Evening work limitations
  - Night work restrictions
  - Out-of-hours period requirements
- **Respite Periods**: Automatic calculation of required break periods
- **Compliance Tracking**: EPA, Council, Transport for NSW, and WorkCover requirements

### Mitigation Measures
- **Standard Measures**: Required mitigation for all projects
- **Additional Measures**: Extra measures for highly affected areas
- Cost and implementation time estimates
- Feasibility assessments

### Documentation
- **Step 2 Memo Pack**: Comprehensive notification and communication plan
- **Reference Noise Pack**: Technical documentation
- **Pre-work Checklist**: Automated checklist based on project requirements
- **Calculation Trace**: Full audit trail of assumptions and data sources

## Quick Start

### Prerequisites
- Python 3.13+ with virtual environment
- Node.js 18+
- npm

### Running the Application

1. **Start both servers:**
```bash
./start_app.sh
```

2. **Manual startup:**
```bash
# Terminal 1 - Backend
source venv/bin/activate
python backend_server.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Using the Application

### Basic Calculation
1. Fill in the calculation parameters:
   - Assessment Type (Distance Based or Full Estimator)
   - Calculation Mode (Scenario, Noisiest Plant, Individual Plant)
   - Environment Approach (Representative or User-supplied background)
   - Time Period (Day, Evening, Night)
   - Propagation Type (Rural, Urban, Hard Ground, etc.)
   - Noise Category (R1 Rural Residential, U2 Urban Industrial)
   - Scenario (if applicable)
   - Distance (for Full Estimator mode)

2. Click "Calculate Noise Level & Requirements"

### Understanding Results

#### Impact Bands
- **NOT_AFFECTED**: Noise levels below criteria
- **AFFECTED**: Noise exceeds background but within reasonable limits
- **HIGHLY_AFFECTED**: Significantly exceeds criteria, requires extensive mitigation

#### Notification Requirements
Based on the impact assessment, the system will generate:
- **Phone Calls**: Required for affected stakeholders (7 days prior)
- **Letter Drop**: Required for highly affected areas (7 days prior)
- **Site Signage**: Always required (24 hours prior)
- **Newspaper**: Required for out-of-hours work (7 days prior)

#### Work Hour Restrictions
- **Day Work**: 7am-6pm Mon-Sat, max 6 consecutive days
- **Evening Work**: 6pm-10pm, max 3 consecutive days, EPA approval required
- **Night Work**: 10pm-7am, emergency only, max 2 consecutive days
- **Out of Hours**: Specific respite periods apply

#### Compliance Requirements
- **EPA**: ICNG compliance, Section 115 approval for out-of-hours work
- **Council**: Development applications, construction certificates
- **Transport**: Traffic management, network access
- **WorkCover**: Worker safety, hearing protection

## API Reference

### Endpoints

#### POST /calculate
Perform a comprehensive noise estimation calculation.

**Request Body:**
```json
{
  "assessment_type": "distance_based|full_estimator",
  "calculation_mode": "scenario|noisiest_plant|individual_plant",
  "environment_approach": "representative_noise_environment|user_supplied_background_level",
  "time_period": "day|evening|night",
  "propagation_type": "rural|urban|hard_ground|soft_ground|mixed",
  "noise_category_id": "R1|U2",
  "scenario_id": "excavation|paving",
  "receiver_distance": 100.0,
  "user_background_level": 45.0,
  "include_trace": true
}
```

**Response:**
```json
{
  "request_id": "uuid",
  "predicted_level_db": 55.0,
  "background_db": 45.0,
  "nml_db": 55.0,
  "exceed_background_db": 10.0,
  "exceed_nml_db": 0.0,
  "impact_band": "affected|highly_affected|not_affected",
  "distances": {
    "distance_to_exceed_background": 100.0,
    "affected_distance": 150.0
  },
  "notification_requirements": [...],
  "stakeholder_requirements": [...],
  "work_hour_restrictions": [...],
  "respite_periods": [...],
  "compliance_requirements": [...],
  "standard_measures": [...],
  "additional_measures": [...],
  "checklist_items": [...],
  "trace": {...}
}
```

## Examples

### Example 1: Daytime Excavation in Rural Area
```json
{
  "assessment_type": "distance_based",
  "calculation_mode": "scenario",
  "environment_approach": "representative_noise_environment",
  "time_period": "day",
  "propagation_type": "rural",
  "noise_category_id": "R1",
  "scenario_id": "excavation",
  "receiver_distance": 100
}
```
**Result**: NOT_AFFECTED
- Basic notifications required
- Standard work hours apply
- Standard mitigation measures

### Example 2: Nighttime Paving in Urban Area
```json
{
  "assessment_type": "full_estimator",
  "calculation_mode": "scenario",
  "environment_approach": "representative_noise_environment",
  "time_period": "night",
  "propagation_type": "urban",
  "noise_category_id": "U2",
  "scenario_id": "paving",
  "receiver_distance": 50
}
```
**Result**: HIGHLY_AFFECTED
- Phone calls and letter drop required
- EPA Section 115 approval needed
- Extensive mitigation measures
- Respite periods required

## Best Practices

1. **Always use trace mode** for documentation purposes
2. **Consider multiple scenarios** to find the optimal approach
3. **Implement all feasible mitigation measures** before considering out-of-hours work
4. **Maintain records** of all notifications and complaints
5. **Review compliance requirements** early in the planning process

## Troubleshooting

1. **Backend not starting**: Check virtual environment and dependencies
2. **Frontend errors**: Ensure Node.js is up to date, run `npm install`
3. **CORS errors**: Verify both servers are running on correct ports
4. **Calculation errors**: Check input parameters and dataset availability

## Development

### Backend
- FastAPI framework
- Pydantic for validation
- Comprehensive notification and compliance logic
- Full audit trail support

### Frontend
- Next.js 15 with TypeScript
- shadcn/ui components
- Responsive design
- Download functionality for documentation packs

## Data Sources

The application uses the Transport for NSW Construction and Maintenance Noise Estimator dataset:
- Noise categories and background levels
- Work scenarios and sound power levels
- Plant equipment data
- Mitigation measure library
- Compliance requirement matrices
