#!/usr/bin/env python3
"""
Update the calculator to use Concawe propagation model from the Excel workbook.
"""

import json
import math
from pathlib import Path

# Load the Concawe data from the extracted workbook logic
with open("docs/workbook_logic.json", 'r') as f:
    workbook_logic = json.load(f)

# Extract Concawe table data
concawe_data = workbook_logic["key_logic"]["concawe_tables"]["distance_levels"]

# Convert to a more usable format
concawe_table = {}
for row in concawe_data[1:]:  # Skip header
    if row and len(row) >= 5:
        distance = int(row[1])
        hard = float(row[2]) if row[2] is not None else None
        urban = float(row[3]) if row[3] is not None else None
        rural = float(row[4]) if row[4] is not None else None
        
        if distance is not None:
            concawe_table[distance] = {
                "hard": hard,
                "urban": urban,
                "rural": rural
            }

# Save the Concawe table as a dataset
concawe_dataset = {
    "metadata": {
        "name": "Concawe Propagation Table",
        "version": "1.0",
        "description": "Distance-based attenuation values from Concawe model",
        "source": "EMF-NV-TT-0067 Construction and Maintenance Noise Estimator (Roads).xlsm"
    },
    "concawe_attenuation": concawe_table
}

# Save to datasets directory
datasets_dir = Path("datasets")
datasets_dir.mkdir(exist_ok=True)

with open(datasets_dir / "concawe_propagation.json", 'w') as f:
    json.dump(concawe_dataset, f, indent=2)

print(f"Saved Concawe propagation table with {len(concawe_table)} distance points")

# Create an updated calculator that uses Concawe
calculator_update = '''
# Update to _apply_propagation method to use Concawe
def _apply_propagation(self, source_level: float, distance: float, propagation_type: str, dataset, trace: Optional[CalculationTrace]) -> float:
    """Apply propagation attenuation using Concawe model."""
    if distance <= 0:
        raise ValueError("Distance must be positive")
    
    # Get Concawe attenuation data
    concawe_data = dataset.get("concawe_attenuation", {})
    
    # Round distance to nearest table value
    rounded_distance = round(distance)
    
    # Find the closest distance in the table
    available_distances = sorted([d for d in concawe_data.keys() if d is not None])
    closest_distance = min(available_distances, key=lambda x: abs(x - rounded_distance))
    
    # Get attenuation for the propagation type
    propagation_map = {
        "Water": "hard",
        "Developed settlements (urban and suburban areas)": "urban", 
        "Rural": "rural"
    }
    
    prop_key = propagation_map.get(propagation_type, "rural")
    attenuation_at_distance = concawe_data.get(closest_distance, {}).get(prop_key, 0)
    
    # Calculate received level using Excel formula logic:
    # Level = SWL - 110 + ConcaweAttenuation + BarrierAdjustment
    # The -110 is a reference adjustment used in the Excel workbook
    received_level = source_level - 110 + attenuation_at_distance
    
    if trace:
        trace.intermediate_values.update({
            "concawe_distance_used": closest_distance,
            "concawe_attenuation": attenuation_at_distance,
            "received_level": received_level
        })
    
    return received_level
'''

print("\nCalculator update code generated:")
print(calculator_update)
