# Noise Assessment Wizard - Step-by-Step Guide

## Overview
The Noise Assessment Wizard provides a guided, step-by-step interface for conducting noise impact assessments. It pulls all descriptive information directly from the Transport for NSW spreadsheet and provides explanations at each step.

## Features

### 1. **Guided Step-by-Step Process**
- 9 interactive steps with progress tracking
- Visual indicators for completed, current, and upcoming steps
- Clear explanations at each stage

### 2. **Comprehensive Information Display**
- **Definitions**: 22 key terms extracted from the spreadsheet
- **Guidance**: Detailed explanations for each parameter
- **When to Use**: Context-specific guidance for each option
- **Examples**: Real-world examples for each scenario

### 3. **Interactive Selection Cards**
- Visual card-based interface for each selection
- Hover effects and selection indicators
- Detailed information shown for each option

## Step-by-Step Breakdown

### Step 1: Assessment Type
**Options:**
- **Distance Based Assessment**: Calculate noise at specific distances
- **Full Estimator Assessment**: Comprehensive analysis with affected distances

**Information Provided:**
- When to use each type
- Steps involved in the assessment
- Typical applications

### Step 2: Calculation Mode
**Options:**
- **Scenario-based**: Predefined work scenarios
- **Noisiest Plant**: Conservative estimate using loudest equipment
- **Individual Plant**: Custom equipment selection

### Step 3: Environment Approach
**Options:**
- **Representative Noise Environment**: Uses predefined background levels
- **User Supplied Background Level**: Enter measured background noise

### Step 4: Time Period
**Options:**
- **Daytime (7am - 6pm)**: Standard work hours
- **Evening (6pm - 10pm)**: Restricted hours
- **Nighttime (10pm - 7am)**: Strictest requirements

**Information Displayed:**
- Noise criteria for each period
- Work hour restrictions
- Approval requirements

### Step 5: Propagation Type
**Options:**
- **Rural**: Open country environment
- **Urban**: Built-up areas with buildings
- **Hard Ground**: Reflective surfaces
- **Soft Ground**: Porous surfaces
- **Mixed**: Variable terrain

### Step 6: Location Type (Noise Category)
**Options:**
- **R1 - Rural Residential**: Lower background levels
- **U2 - Urban Industrial**: Higher background levels

**Information Displayed:**
- Noise Management Levels (NML)
- Typical background levels
- Location characteristics

### Step 7: Work Scenario
**Options:**
- **Excavation Works**: Earthmoving and trenching
- **Paving Works**: Road surfacing activities

**Information Displayed:**
- Typical equipment used
- Sound power levels
- Common activities

### Step 8: Distance Entry
- Input field for receiver distance
- Optional background level input
- Distance guidelines and best practices

### Step 9: Review & Calculate
- Summary of all selections
- Validation check
- Calculate button to generate results

## Results Display

After calculation, the wizard displays the comprehensive results including:

1. **Noise Levels**
   - Predicted level
   - Background level
   - Exceedance values
   - Impact band

2. **Notification Requirements**
   - Phone calls required
   - Letter drops needed
   - Site signage
   - Newspaper notifications

3. **Stakeholder Requirements**
   - Affected residents
   - Local businesses
   - Schools and hospitals
   - Community groups

4. **Work Hour Restrictions**
   - Detailed restrictions by period
   - Respite period requirements
   - Maximum consecutive days

5. **Compliance Requirements**
   - EPA requirements
   - Council approvals
   - Transport guidelines
   - WorkCover safety

6. **Mitigation Measures**
   - Standard measures
   - Additional measures
   - Cost and time estimates

7. **Documentation**
   - Downloadable Step 2 Memo
   - Reference documentation
   - Pre-work checklist

## Tips and Best Practices

The wizard displays contextual tips throughout the process:
- Measure background noise at sensitive locations
- Consider worst-case scenarios
- Implement mitigation before out-of-hours work
- Keep records of notifications
- Use monitoring for high-impact projects

## Data Sources

All information is extracted from:
- Transport for NSW Construction and Maintenance Noise Estimator
- EPA Interim Construction Noise Guidelines
- Industry best practices

## Access

The wizard is available at: http://localhost:3001

## Technical Details

- **Frontend**: Next.js 15 with TypeScript
- **UI Components**: shadcn/ui with Tailwind CSS
- **Data**: JSON extracted from Excel spreadsheet
- **Backend**: FastAPI with comprehensive calculation engine
- **Response Format**: Comprehensive results with all compliance requirements
