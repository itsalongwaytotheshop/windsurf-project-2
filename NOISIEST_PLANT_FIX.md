# Fixed: Noisiest Plant Mode

## Problem
When selecting "Noisiest Plant" as the calculation mode, the wizard was incorrectly asking for a scenario selection instead of showing individual plant/equipment options.

## Solution

### 1. Created Comprehensive Plant Database
- Extracted **26 different plants/equipment** from industry standards
- Each plant includes:
  - ID and name
  - Description
  - Sound power level (dB)
  - Duty cycle
  - Usage factor
  - Equipment category

### 2. Updated Wizard Interface
- **Dynamic Step Title**: Changes based on calculation mode
  - "Select Work Scenario" for scenario mode
  - "Select Noisiest Plant" for noisiest plant mode

- **Plant Selection View** (for noisiest plant mode):
  - Organized by equipment categories:
    - Demolition (Breaker, Jackhammer)
    - Drilling (Drill Rig, Auger)
    - Earthmoving (Excavator, Dozer, Grader, Scraper)
    - Power (Generator, Compressor)
    - Paving (Asphalt Paver)
    - Transport (Dump Truck, Service Vehicle)
    - And 8 more categories

- **Visual Indicators**:
  - Orange highlight for selected plant
  - Red badge showing sound power level
  - Duty cycle and usage factor displayed

### 3. Conservative Assessment Warning
Added clear explanation that noisiest plant mode:
- Provides a worst-case noise level
- Assumes continuous operation at maximum
- Used for conservative planning and approval

### 4. Updated Review Step
Now correctly shows:
- "Noisiest Plant:" label instead of "Scenario:"
- Selected plant name from plant database

## Available Equipment Categories

1. **Demolition** - Hydraulic Breaker (115 dB), Jackhammer (115 dB)
2. **Drilling** - Drill Rig (110 dB), Auger (95 dB)
3. **Earthmoving** - Excavator (105 dB), Bulldozer (108 dB), Grader (105 dB), Scraper (110 dB)
4. **Power** - Generator (108 dB), Air Compressor (105 dB)
5. **Paving** - Asphalt Paver (108 dB)
6. **Material Handling** - Wheel Loader (105 dB)
7. **Transport** - Dump Truck (102 dB), Service Vehicle (85 dB)
8. **Concrete** - Concrete Mixer (100 dB), Pump (95 dB), Vibrator (95 dB)
9. **Compaction** - Road Roller (100 dB), Plate Compactor (100 dB)
10. **Cutting** - Concrete Saw (105 dB)
11. **Vegetation** - Chainsaw (110 dB), Wood Chipper (100 dB), Mower (90 dB), Blower (85 dB)
12. **Lighting** - Light Tower (95 dB)
13. **Marking** - Line Heater (90 dB)

## Usage
1. Select "Distance Based Assessment" in Step 1
2. Choose "Noisiest Plant" in Step 2
3. Complete other steps as normal
4. In Step 7, select from the comprehensive plant list
5. Review shows "Noisiest Plant:" with selected equipment

The wizard now properly supports both scenario-based and noisiest plant calculation modes with appropriate interfaces for each.
