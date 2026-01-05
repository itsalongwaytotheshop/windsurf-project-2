#!/bin/bash

echo "Testing the Noise Estimator Application"
echo "======================================"
echo ""

# Test backend health
echo "1. Testing backend health..."
curl -s http://localhost:8000/health | python -m json.tool
echo ""

# Test a calculation
echo "2. Testing a sample calculation..."
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "assessment_type": "distance_based",
    "calculation_mode": "scenario",
    "environment_approach": "representative_noise_environment",
    "time_period": "day",
    "propagation_type": "rural",
    "noise_category_id": "R1",
    "scenario_id": "excavation",
    "receiver_distance": 100
  }' | python -c "
import json, sys
data = json.load(sys.stdin)
print(f'Success! Calculation completed.')
print(f'Request ID: {data[\"request_id\"]}')
print(f'Predicted Level: {data[\"predicted_level_db\"]} dB')
print(f'Background Level: {data[\"background_db\"]} dB')
print(f'Impact Band: {data[\"impact_band\"]}')
"
echo ""

echo "3. Access the frontend at: http://localhost:3000"
echo ""
echo "The application is ready to use!"
