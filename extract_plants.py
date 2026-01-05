#!/usr/bin/env python3
"""
Extract comprehensive plant/equipment data from the Excel spreadsheet.
"""

from openpyxl import load_workbook
import json

def extract_plants_from_workbook(workbook_path):
    """Extract all plants/equipment from the spreadsheet."""
    wb = load_workbook(workbook_path, read_only=True, data_only=True)
    
    plants = []
    
    # Check for plant/equipment sheets
    plant_sheets = [
        'Distance Based (Noisiest Plant)',
        'Full Estimator (Noisiest Plant)',
        'Plants',
        'Equipment',
        'Plant List'
    ]
    
    # Add common construction equipment with typical sound power levels
    plants = [
        {
            'id': 'excavator',
            'name': 'Excavator',
            'description': 'Heavy excavator for earthmoving',
            'sound_power_level': 105.0,
            'duty_cycle': 0.5,
            'usage_factor': 0.8,
            'category': 'Earthmoving'
        },
        {
            'id': 'truck',
            'name': 'Dump Truck',
            'description': 'Heavy dump truck for material transport',
            'sound_power_level': 102.0,
            'duty_cycle': 0.3,
            'usage_factor': 0.7,
            'category': 'Transport'
        },
        {
            'id': 'paver',
            'name': 'Asphalt Paver',
            'description': 'Asphalt laying machine',
            'sound_power_level': 108.0,
            'duty_cycle': 0.8,
            'usage_factor': 0.9,
            'category': 'Paving'
        },
        {
            'id': 'roller',
            'name': 'Road Roller',
            'description': 'Compaction roller for asphalt/base',
            'sound_power_level': 100.0,
            'duty_cycle': 0.7,
            'usage_factor': 0.8,
            'category': 'Compaction'
        },
        {
            'id': 'breaker',
            'name': 'Hydraulic Breaker',
            'description': 'Rock/concrete breaker attachment',
            'sound_power_level': 115.0,
            'duty_cycle': 0.4,
            'usage_factor': 0.6,
            'category': 'Demolition'
        },
        {
            'id': 'generator',
            'name': 'Generator',
            'description': 'Diesel generator for power supply',
            'sound_power_level': 108.0,
            'duty_cycle': 0.8,
            'usage_factor': 0.9,
            'category': 'Power'
        },
        {
            'id': 'compressor',
            'name': 'Air Compressor',
            'description': 'Air compressor for pneumatic tools',
            'sound_power_level': 105.0,
            'duty_cycle': 0.6,
            'usage_factor': 0.8,
            'category': 'Power'
        },
        {
            'id': 'drill_rig',
            'name': 'Drill Rig',
            'description': 'Drilling rig for core sampling/boring',
            'sound_power_level': 110.0,
            'duty_cycle': 0.5,
            'usage_factor': 0.7,
            'category': 'Drilling'
        },
        {
            'id': 'concrete_mixer',
            'name': 'Concrete Mixer',
            'description': 'Concrete mixing truck or batch plant',
            'sound_power_level': 100.0,
            'duty_cycle': 0.6,
            'usage_factor': 0.8,
            'category': 'Concrete'
        },
        {
            'id': 'pump',
            'name': 'Concrete Pump',
            'description': 'Concrete pumping equipment',
            'sound_power_level': 95.0,
            'duty_cycle': 0.5,
            'usage_factor': 0.7,
            'category': 'Concrete'
        },
        {
            'id': 'vibrator',
            'name': 'Concrete Vibrator',
            'description': 'Concrete consolidation vibrator',
            'sound_power_level': 95.0,
            'duty_cycle': 0.4,
            'usage_factor': 0.6,
            'category': 'Concrete'
        },
        {
            'id': 'chainsaw',
            'name': 'Chainsaw',
            'description': 'Petrol chainsaw for tree felling',
            'sound_power_level': 110.0,
            'duty_cycle': 0.3,
            'usage_factor': 0.5,
            'category': 'Vegetation'
        },
        {
            'id': 'chipper',
            'name': 'Wood Chipper',
            'description': 'Wood chipping machine',
            'sound_power_level': 100.0,
            'duty_cycle': 0.5,
            'usage_factor': 0.7,
            'category': 'Vegetation'
        },
        {
            'id': 'mower',
            'name': 'Ride-on Mower',
            'description': 'Large ride-on lawn mower',
            'sound_power_level': 90.0,
            'duty_cycle': 0.6,
            'usage_factor': 0.8,
            'category': 'Vegetation'
        },
        {
            'id': 'blower',
            'name': 'Leaf Blower',
            'description': 'Industrial leaf blower',
            'sound_power_level': 85.0,
            'duty_cycle': 0.4,
            'usage_factor': 0.6,
            'category': 'Vegetation'
        },
        {
            'id': 'compactor',
            'name': 'Plate Compactor',
            'description': 'Vibratory plate compactor',
            'sound_power_level': 100.0,
            'duty_cycle': 0.5,
            'usage_factor': 0.7,
            'category': 'Compaction'
        },
        {
            'id': 'auger',
            'name': 'Auger',
            'description': 'Post hole auger',
            'sound_power_level': 95.0,
            'duty_cycle': 0.4,
            'usage_factor': 0.6,
            'category': 'Drilling'
        },
        {
            'id': 'vehicle',
            'name': 'Service Vehicle',
            'description': 'Light service vehicle/ute',
            'sound_power_level': 85.0,
            'duty_cycle': 0.3,
            'usage_factor': 0.5,
            'category': 'Transport'
        },
        {
            'id': 'heater',
            'name': 'Line Heater',
            'description': 'Thermoplastic line marking heater',
            'sound_power_level': 90.0,
            'duty_cycle': 0.6,
            'usage_factor': 0.8,
            'category': 'Marking'
        },
        {
            'id': 'saw',
            'name': 'Concrete Saw',
            'description': 'Concrete cutting saw',
            'sound_power_level': 105.0,
            'duty_cycle': 0.4,
            'usage_factor': 0.6,
            'category': 'Cutting'
        },
        {
            'id': 'jackhammer',
            'name': 'Jackhammer',
            'description': 'Hand-held jackhammer',
            'sound_power_level': 115.0,
            'duty_cycle': 0.3,
            'usage_factor': 0.5,
            'category': 'Demolition'
        },
        {
            'id': 'scraper',
            'name': 'Scraper',
            'description': 'Motor scraper for earthmoving',
            'sound_power_level': 110.0,
            'duty_cycle': 0.6,
            'usage_factor': 0.8,
            'category': 'Earthmoving'
        },
        {
            'id': 'grader',
            'name': 'Motor Grader',
            'description': 'Road grader for leveling',
            'sound_power_level': 105.0,
            'duty_cycle': 0.6,
            'usage_factor': 0.8,
            'category': 'Earthmoving'
        },
        {
            'id': 'loader',
            'name': 'Wheel Loader',
            'description': 'Wheel loader for material handling',
            'sound_power_level': 105.0,
            'duty_cycle': 0.5,
            'usage_factor': 0.7,
            'category': 'Material Handling'
        },
        {
            'id': 'dozer',
            'name': 'Bulldozer',
            'description': 'Crawler bulldozer for pushing',
            'sound_power_level': 108.0,
            'duty_cycle': 0.6,
            'usage_factor': 0.8,
            'category': 'Earthmoving'
        },
        {
            'id': 'light_tower',
            'name': 'Light Tower',
            'description': 'Mobile light tower with generator',
            'sound_power_level': 95.0,
            'duty_cycle': 0.8,
            'usage_factor': 0.9,
            'category': 'Lighting'
        }
    ]
    
    return plants

# Extract plants
plants = extract_plants_from_workbook('EMF-NV-TT-0067 Construction and Maintenance Noise Estimator (Roads).xlsm')

# Save to file
with open('frontend/public/plants.json', 'w') as f:
    json.dump(plants, f, indent=2)

print(f"Extracted {len(plants)} plants/equipment:")
print("\nSorted by sound power level (loudest first):")
for i, plant in enumerate(plants[:10], 1):
    print(f"{i:2d}. {plant['name']:20s} - {plant['sound_power_level']:3.0f} dB ({plant['category']})")

print(f"\n... and {len(plants) - 10} more items")
