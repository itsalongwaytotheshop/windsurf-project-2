// Extended types for the noise estimator application
export interface NotificationRequirement {
  type: 'phone_call' | 'letter_drop' | 'email' | 'site_signage' | 'newspaper';
  description: string;
  timing: string;
  distance_threshold?: number;
  details: string[];
}

export interface StakeholderRequirement {
  category: string;
  notification_methods: string[];
  contact_timing: string;
  specific_requirements: string[];
}

export interface WorkHourRestriction {
  period: string;
  max_consecutive_days: number;
  separation_required: number;
  max_per_month: number;
  restrictions: string[];
}

export interface RespitePeriod {
  id: string;
  description: string;
  night_restrictions: string;
  evening_restrictions: string;
}

export interface ComplianceRequirement {
  category: string;
  requirements: string[];
  reference_numbers: string[];
  approval_needed: boolean;
  timeframe: string;
}

export interface MitigationMeasure {
  id: string;
  title: string;
  description: string;
  type: 'standard' | 'additional';
  reduction_db: number;
  applicable: boolean;
  feasibility: 'feasible' | 'not_feasible' | 'conditional';
  reason?: string;
  cost: 'low' | 'medium' | 'high';
  implementation_time: string;
}

export interface ChecklistItem {
  id: string;
  text: string;
  category: string;
  required: boolean;
}

export interface ExtendedEstimationResult {
  // Basic results
  request_id: string;
  predicted_level_db: number;
  background_db: number;
  nml_db: number;
  exceed_background_db: number;
  exceed_nml_db: number;
  impact_band: string;
  
  // Distance information
  distances: {
    distance_to_exceed_background: number | null;
    distance_to_nml: number | null;
    distance_to_highly_affected: number | null;
    affected_distance: number | null;
  };
  
  // Notification requirements
  notification_requirements: NotificationRequirement[];
  stakeholder_requirements: StakeholderRequirement[];
  
  // Work hour restrictions
  work_hour_restrictions: WorkHourRestriction[];
  respite_periods: RespitePeriod[];
  
  // Compliance
  compliance_requirements: ComplianceRequirement[];
  
  // Mitigation measures
  standard_measures: MitigationMeasure[];
  additional_measures: MitigationMeasure[];
  
  // Documentation
  step2_memo_pack: string | null;
  ref_noise_pack: string | null;
  checklist_items: ChecklistItem[];
  
  // Trace information
  trace: {
    tables_used: string[];
    intermediate_values: Record<string, any>;
    warnings: string[];
    assumptions: string[];
  };
}

export enum ImpactBand {
  NOT_AFFECTED = "not_affected",
  AFFECTED = "affected",
  HIGHLY_AFFECTED = "highly_affected"
}

export interface ProjectDetails {
  name: string;
  location: string;
  description: string;
  startDate: string;
  endDate: string;
  contactPerson: string;
  contactPhone: string;
  contactEmail: string;
  projectType: 'construction' | 'maintenance' | 'emergency';
}

export interface SiteConstraints {
  accessRestrictions: string[];
  nearbySensitiveReceivers: {
    type: 'residential' | 'school' | 'hospital' | 'business';
    distance: number;
    description: string;
  }[];
  physicalConstraints: string[];
  environmentalConstraints: string[];
}
