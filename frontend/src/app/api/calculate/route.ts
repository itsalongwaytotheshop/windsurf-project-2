import { NextRequest, NextResponse } from 'next/server';

// Types for the API
interface EstimationRequest {
  assessment_type: 'distance_based' | 'full_estimator';
  calculation_mode: 'scenario' | 'noisiest_plant' | 'individual_plant';
  environment_approach: 'representative_noise_environment' | 'user_supplied_background_level';
  time_period: 'day' | 'evening' | 'night';
  propagation_type: 'rural' | 'urban' | 'hard_ground' | 'soft_ground' | 'mixed';
  noise_category_id: string;
  scenario_id?: string;
  plant_ids?: string[];
  receiver_distance?: number;
  user_background_level?: number;
  include_trace?: boolean;
}

interface EstimationResult {
  request_id: string;
  dataset_version: string;
  timestamp: string;
  resolved_inputs: any;
  predicted_level_db: number;
  background_db: number;
  nml_db: number;
  exceed_background_db: number;
  exceed_nml_db: number;
  impact_band: string;
  standard_measures: any[];
  additional_measures: any[];
  trace?: any;
  distances?: any;
  results_table_markdown: string;
  results_table_csv: string;
}

export async function POST(request: NextRequest) {
  try {
    const body: EstimationRequest = await request.json();
    
    // Call the Python backend
    const response = await fetch('http://localhost:8000/calculate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { error: errorText },
        { status: response.status }
      );
    }

    const result: EstimationResult = await response.json();
    
    return NextResponse.json(result);
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}
