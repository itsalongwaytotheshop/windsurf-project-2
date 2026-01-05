"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { 
  ChevronLeft, 
  ChevronRight, 
  Info, 
  Lightbulb, 
  Clock, 
  MapPin, 
  Volume2,
  CheckCircle,
  AlertTriangle,
  HelpCircle,
  BookOpen,
  FileText,
  Calculator
} from "lucide-react";
import ComprehensiveResults from "./ComprehensiveResults";
import { ExtendedEstimationResult } from "@/types/estimator";

interface WizardData {
  definitions: Record<string, string>;
  guidance: {
    assessment_types: Record<string, any>;
    calculation_modes: Record<string, any>;
    environment_approaches: Record<string, any>;
    time_periods: Record<string, any>;
    propagation_types: Record<string, any>;
    noise_categories: Record<string, any>;
    scenarios: Record<string, any>;
    mitigation_measures: {
      standard: Array<any>;
      additional: Array<any>;
    };
    notifications: Record<string, any>;
    work_hours: Record<string, any>;
    compliance: Record<string, any>;
  };
  tips: string[];
}

interface FormData {
  assessment_type: string;
  calculation_mode: string;
  environment_approach: string;
  time_period: string;
  propagation_type: string;
  noise_category_id: string;
  scenario_id: string;
  receiver_distance: string;
  user_background_level: string;
  include_trace: boolean;
}

const steps = [
  { id: 1, title: "Assessment Type", icon: FileText },
  { id: 2, title: "Calculation Mode", icon: Calculator },
  { id: 3, title: "Environment", icon: MapPin },
  { id: 4, title: "Time Period", icon: Clock },
  { id: 5, title: "Propagation", icon: Volume2 },
  { id: 6, title: "Location Type", icon: MapPin },
  { id: 7, title: "Work Scenario", icon: BookOpen },
  { id: 8, title: "Distance", icon: MapPin },
  { id: 9, title: "Review & Calculate", icon: CheckCircle },
];

export default function NoiseWizard() {
  const [currentStep, setCurrentStep] = useState(0);
  const [wizardData, setWizardData] = useState<WizardData | null>(null);
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [plants, setPlants] = useState<any[]>([]);
  const [formData, setFormData] = useState<FormData>({
    assessment_type: "",
    calculation_mode: "",
    environment_approach: "",
    time_period: "",
    propagation_type: "",
    noise_category_id: "",
    scenario_id: "",
    receiver_distance: "100",
    user_background_level: "",
    include_trace: true,
  });
  const [result, setResult] = useState<ExtendedEstimationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load wizard data
    fetch('/wizard-data.json')
      .then(res => res.json())
      .then(data => setWizardData(data))
      .catch(err => console.error('Failed to load wizard data:', err));
    
    // Load scenarios
    fetch('/scenarios.json')
      .then(res => res.json())
      .then(data => setScenarios(data))
      .catch(err => console.error('Failed to load scenarios:', err));
    
    // Load plants
    fetch('/plants.json')
      .then(res => res.json())
      .then(data => setPlants(data))
      .catch(err => console.error('Failed to load plants:', err));
  }, []);

  const handleInputChange = (field: keyof FormData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const calculateProgress = () => ((currentStep + 1) / steps.length) * 100;

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {
        ...formData,
        receiver_distance: formData.assessment_type === "full_estimator" ? parseFloat(formData.receiver_distance) : undefined,
        user_background_level: formData.environment_approach === "user_supplied_background_level" ? parseFloat(formData.user_background_level) : undefined,
        scenario_id: formData.calculation_mode === "scenario" ? formData.scenario_id : undefined,
      };

      const response = await fetch("/api/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Calculation failed");
      }

      const calculationResult = await response.json();
      setResult(calculationResult);
      setCurrentStep(steps.length); // Move to results step
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    if (!wizardData) return <div>Loading...</div>;

    const step = steps[currentStep];

    switch (step.id) {
      case 1: // Assessment Type
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-2">Choose Your Assessment Type</h3>
              <p className="text-sm text-muted-foreground mb-4">
                The assessment type determines how the noise calculation will be performed.
              </p>
            </div>

            <div className="grid gap-4">
              {Object.entries(wizardData.guidance.assessment_types).map(([key, value]) => (
                <Card 
                  key={key} 
                  className={`cursor-pointer transition-all ${
                    formData.assessment_type === key ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => handleInputChange('assessment_type', key)}
                >
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="h-5 w-5" />
                      {value.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-3">{value.description}</p>
                    <div className="space-y-2">
                      <div>
                        <span className="font-medium text-sm">When to use:</span>
                        <p className="text-sm">{value.when_to_use}</p>
                      </div>
                      <div>
                        <span className="font-medium text-sm">Steps involved:</span>
                        <ul className="text-sm list-disc list-inside mt-1">
                          {value.steps.map((step: string, i: number) => (
                            <li key={i}>{step}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {wizardData.tips[0] && (
              <Alert>
                <Lightbulb className="h-4 w-4" />
                <AlertDescription>{wizardData.tips[0]}</AlertDescription>
              </Alert>
            )}
          </div>
        );

      case 2: // Calculation Mode
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-2">Select Calculation Mode</h3>
              <p className="text-sm text-muted-foreground">
                Choose how you want to model the noise source.
              </p>
            </div>

            <div className="grid gap-4">
              {Object.entries(wizardData.guidance.calculation_modes).map(([key, value]) => (
                <Card 
                  key={key} 
                  className={`cursor-pointer transition-all ${
                    formData.calculation_mode === key ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => handleInputChange('calculation_mode', key)}
                >
                  <CardHeader>
                    <CardTitle>{value.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-2">{value.description}</p>
                    <p className="text-sm"><strong>When to use:</strong> {value.when_to_use}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                <strong>Definition:</strong> {wizardData.definitions["Calculation Mode"] || "The method used to model noise sources in your assessment."}
              </AlertDescription>
            </Alert>
          </div>
        );

      case 3: // Environment Approach
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-2">Environment Approach</h3>
              <p className="text-sm text-muted-foreground">
                How will you determine the background noise level?
              </p>
            </div>

            <div className="grid gap-4">
              {Object.entries(wizardData.guidance.environment_approaches).map(([key, value]) => (
                <Card 
                  key={key} 
                  className={`cursor-pointer transition-all ${
                    formData.environment_approach === key ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => handleInputChange('environment_approach', key)}
                >
                  <CardHeader>
                    <CardTitle>{value.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-2">{value.description}</p>
                    <p className="text-sm"><strong>When to use:</strong> {value.when_to_use}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Alert>
              <HelpCircle className="h-4 w-4" />
              <AlertDescription>
                <strong>Background Noise:</strong> {wizardData.definitions["Background noise level"] || "The underlying level of noise present in the ambient environment."}
              </AlertDescription>
            </Alert>
          </div>
        );

      case 4: // Time Period
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-2">Select Work Time Period</h3>
              <p className="text-sm text-muted-foreground">
                Different time periods have different noise criteria and restrictions.
              </p>
            </div>

            <div className="grid gap-4">
              {Object.entries(wizardData.guidance.time_periods).map(([key, value]) => (
                <Card 
                  key={key} 
                  className={`cursor-pointer transition-all ${
                    formData.time_period === key ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => handleInputChange('time_period', key)}
                >
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Clock className="h-5 w-5" />
                      {value.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-2">{value.description}</p>
                    <div className="space-y-1 text-sm">
                      <p><strong>Restrictions:</strong> {value.restrictions}</p>
                      <p><strong>Typical Background:</strong> {value.typical_background}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <strong>Important:</strong> Night and evening work require EPA approval and additional notifications.
              </AlertDescription>
            </Alert>
          </div>
        );

      case 5: // Propagation Type
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-2">Select Propagation Environment</h3>
              <p className="text-sm text-muted-foreground">
                The environment affects how noise travels from the source to receivers.
              </p>
            </div>

            <div className="grid gap-4">
              {Object.entries(wizardData.guidance.propagation_types).map(([key, value]) => (
                <Card 
                  key={key} 
                  className={`cursor-pointer transition-all ${
                    formData.propagation_type === key ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => handleInputChange('propagation_type', key)}
                >
                  <CardHeader>
                    <CardTitle>{value.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-2">{value.description}</p>
                    <div className="space-y-1 text-sm">
                      <p><strong>Characteristics:</strong> {value.characteristics}</p>
                      <p><strong>Example:</strong> {value.example}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                <strong>Tip:</strong> {wizardData.tips[6] || "Consider the actual site conditions when selecting propagation type."}
              </AlertDescription>
            </Alert>
          </div>
        );

      case 6: // Noise Category
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-2">Select Location Type</h3>
              <p className="text-sm text-muted-foreground">
                This determines the noise criteria for your location.
              </p>
            </div>

            <div className="grid gap-4">
              <Card 
                className={`cursor-pointer transition-all ${
                  formData.noise_category_id === "R1" ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                }`}
                onClick={() => handleInputChange('noise_category_id', 'R1')}
              >
                <CardHeader>
                  <CardTitle>R1 - Rural Residential</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-2">
                    Rural residential areas with lower background noise levels
                  </p>
                  <div className="text-sm space-y-1">
                    <p><strong>Day NML:</strong> 55 dB</p>
                    <p><strong>Evening NML:</strong> 50 dB</p>
                    <p><strong>Night NML:</strong> 45 dB</p>
                  </div>
                </CardContent>
              </Card>

              <Card 
                className={`cursor-pointer transition-all ${
                  formData.noise_category_id === "U2" ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                }`}
                onClick={() => handleInputChange('noise_category_id', 'U2')}
              >
                <CardHeader>
                  <CardTitle>U2 - Urban Industrial</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-2">
                    Urban industrial areas with higher background noise levels
                  </p>
                  <div className="text-sm space-y-1">
                    <p><strong>Day NML:</strong> 65 dB</p>
                    <p><strong>Evening NML:</strong> 60 dB</p>
                    <p><strong>Night NML:</strong> 55 dB</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Alert>
              <HelpCircle className="h-4 w-4" />
              <AlertDescription>
                <strong>NML:</strong> Noise Management Level - the maximum permitted noise level for the location.
              </AlertDescription>
            </Alert>
          </div>
        );

      case 7: // Work Scenario
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-2">
                {formData.calculation_mode === "scenario" ? "Select Work Scenario" : "Select Noisiest Plant"}
              </h3>
              <p className="text-sm text-muted-foreground">
                {formData.calculation_mode === "scenario" 
                  ? "Choose the type of work that best matches your project."
                  : "Select the noisiest piece of equipment for a conservative assessment."
                }
              </p>
            </div>

            {formData.calculation_mode === "scenario" ? (
              <div className="space-y-4">
                {/* Group scenarios by category */}
                <div className="space-y-6">
                  {/* Construction Scenarios */}
                  <div>
                    <h4 className="font-medium text-sm text-muted-foreground mb-3">Construction & Earthworks</h4>
                    <div className="grid gap-3">
                      {scenarios.filter(s => ['excavation', 'road_works', 'bridge_works', 'demolition', 'concrete_works', 'drilling'].includes(s.id)).map((scenario) => (
                        <Card 
                          key={scenario.id}
                          className={`cursor-pointer transition-all ${
                            formData.scenario_id === scenario.id ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                          }`}
                          onClick={() => handleInputChange('scenario_id', scenario.id)}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <h5 className="font-medium">{scenario.name}</h5>
                                <p className="text-sm text-muted-foreground mt-1">{scenario.description}</p>
                                <div className="mt-2">
                                  <p className="text-xs font-medium text-muted-foreground">Equipment:</p>
                                  <div className="flex flex-wrap gap-1 mt-1">
                                    {Object.keys(scenario.sound_power_levels).map((equipment) => (
                                      <Badge key={equipment} variant="outline" className="text-xs">
                                        {equipment} ({scenario.sound_power_levels[equipment]} dB)
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>

                  {/* Road & Infrastructure Scenarios */}
                  <div>
                    <h4 className="font-medium text-sm text-muted-foreground mb-3">Road & Infrastructure</h4>
                    <div className="grid gap-3">
                      {scenarios.filter(s => ['paving', 'paving_asphalt', 'line_marking', 'signage_installation', 'stormwater_works', 'utility_installation'].includes(s.id)).map((scenario) => (
                        <Card 
                          key={scenario.id}
                          className={`cursor-pointer transition-all ${
                            formData.scenario_id === scenario.id ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                          }`}
                          onClick={() => handleInputChange('scenario_id', scenario.id)}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <h5 className="font-medium">{scenario.name}</h5>
                                <p className="text-sm text-muted-foreground mt-1">{scenario.description}</p>
                                <div className="mt-2">
                                  <p className="text-xs font-medium text-muted-foreground">Equipment:</p>
                                  <div className="flex flex-wrap gap-1 mt-1">
                                    {Object.keys(scenario.sound_power_levels).map((equipment) => (
                                      <Badge key={equipment} variant="outline" className="text-xs">
                                        {equipment} ({scenario.sound_power_levels[equipment]} dB)
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>

                  {/* Environmental & Maintenance Scenarios */}
                  <div>
                    <h4 className="font-medium text-sm text-muted-foreground mb-3">Environmental & Maintenance</h4>
                    <div className="grid gap-3">
                      {scenarios.filter(s => ['landscaping', 'tree_removal'].includes(s.id)).map((scenario) => (
                        <Card 
                          key={scenario.id}
                          className={`cursor-pointer transition-all ${
                            formData.scenario_id === scenario.id ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                          }`}
                          onClick={() => handleInputChange('scenario_id', scenario.id)}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <h5 className="font-medium">{scenario.name}</h5>
                                <p className="text-sm text-muted-foreground mt-1">{scenario.description}</p>
                                <div className="mt-2">
                                  <p className="text-xs font-medium text-muted-foreground">Equipment:</p>
                                  <div className="flex flex-wrap gap-1 mt-1">
                                    {Object.keys(scenario.sound_power_levels).map((equipment) => (
                                      <Badge key={equipment} variant="outline" className="text-xs">
                                        {equipment} ({scenario.sound_power_levels[equipment]} dB)
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                </div>

                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    Sound power levels shown are typical values for each equipment type. 
                    Actual levels may vary based on equipment size and operating conditions.
                  </AlertDescription>
                </Alert>
              </div>
            ) : formData.calculation_mode === "noisiest_plant" ? (
              <div className="space-y-4">
                <Alert className="bg-orange-50 border-orange-200">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>Conservative Assessment:</strong> Select the noisiest piece of equipment 
                    that will be used on site. This provides a worst-case noise level for your assessment.
                  </AlertDescription>
                </Alert>

                <div className="space-y-6">
                  {/* Group plants by category */}
                  {['Demolition', 'Drilling', 'Earthmoving', 'Power', 'Paving', 'Material Handling', 'Transport', 'Concrete', 'Compaction', 'Cutting', 'Vegetation', 'Lighting', 'Marking'].map(category => {
                    const categoryPlants = plants.filter(p => p.category === category);
                    if (categoryPlants.length === 0) return null;
                    
                    return (
                      <div key={category}>
                        <h4 className="font-medium text-sm text-muted-foreground mb-3">{category}</h4>
                        <div className="grid gap-3">
                          {categoryPlants.map((plant) => (
                            <Card 
                              key={plant.id}
                              className={`cursor-pointer transition-all ${
                                formData.scenario_id === plant.id ? 'ring-2 ring-orange-500 bg-orange-50' : 'hover:bg-gray-50'
                              }`}
                              onClick={() => handleInputChange('scenario_id', plant.id)}
                            >
                              <CardContent className="p-4">
                                <div className="flex items-start justify-between">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                      <h5 className="font-medium">{plant.name}</h5>
                                      <Badge variant="destructive" className="text-xs">
                                        {plant.sound_power_level} dB
                                      </Badge>
                                    </div>
                                    <p className="text-sm text-muted-foreground mt-1">{plant.description}</p>
                                    <div className="mt-2 grid grid-cols-2 gap-4 text-xs text-muted-foreground">
                                      <div>
                                        <span className="font-medium">Duty Cycle:</span> {plant.duty_cycle * 100}%
                                      </div>
                                      <div>
                                        <span className="font-medium">Usage Factor:</span> {plant.usage_factor * 100}%
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>

                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    The noisiest plant mode assumes the selected equipment is operating continuously 
                    at its maximum sound power level. This provides a conservative estimate for 
                    planning and approval purposes.
                  </AlertDescription>
                </Alert>
              </div>
            ) : (
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  Individual plant selection will be available in the next version.
                </AlertDescription>
              </Alert>
            )}
          </div>
        );

      case 8: // Distance
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-2">Enter Distance to Receiver</h3>
              <p className="text-sm text-muted-foreground">
                How far is the nearest sensitive receiver from the noise source?
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <Label htmlFor="distance">Distance (meters)</Label>
                <Input
                  type="number"
                  step="0.1"
                  value={formData.receiver_distance}
                  onChange={(e) => handleInputChange('receiver_distance', e.target.value)}
                  placeholder="Enter distance in meters"
                  className="mt-2"
                />
              </div>

              {formData.environment_approach === "user_supplied_background_level" && (
                <div>
                  <Label htmlFor="background">Background Level (dB)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={formData.user_background_level}
                    onChange={(e) => handleInputChange('user_background_level', e.target.value)}
                    placeholder="Enter measured background level"
                    className="mt-2"
                  />
                </div>
              )}
            </div>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium mb-2">Distance Guidelines:</h4>
              <ul className="text-sm space-y-1 list-disc list-inside">
                <li>Measure to the nearest residential property</li>
                <li>Include any horizontal distance barriers</li>
                <li>Consider the closest window or outdoor living area</li>
                <li>For apartments, measure to the nearest affected unit</li>
              </ul>
            </div>
          </div>
        );

      case 9: // Review
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-2">Review Your Selections</h3>
              <p className="text-sm text-muted-foreground">
                Please review your inputs before calculating.
              </p>
            </div>

            <div className="grid gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Assessment Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="font-medium">Assessment Type:</span>
                    <span>{wizardData.guidance.assessment_types[formData.assessment_type]?.title}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Calculation Mode:</span>
                    <span>{wizardData.guidance.calculation_modes[formData.calculation_mode]?.title}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Environment:</span>
                    <span>{wizardData.guidance.environment_approaches[formData.environment_approach]?.title}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Time Period:</span>
                    <span>{wizardData.guidance.time_periods[formData.time_period]?.title}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Propagation:</span>
                    <span>{wizardData.guidance.propagation_types[formData.propagation_type]?.title}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Location Type:</span>
                    <span>{formData.noise_category_id}</span>
                  </div>
                  {formData.scenario_id && (
                    <div className="flex justify-between">
                      <span className="font-medium">
                        {formData.calculation_mode === "noisiest_plant" ? "Noisiest Plant:" : "Scenario:"}
                      </span>
                      <span>
                        {formData.calculation_mode === "noisiest_plant" 
                          ? (plants.find(p => p.id === formData.scenario_id)?.name || formData.scenario_id)
                          : (scenarios.find(s => s.id === formData.scenario_id)?.name || formData.scenario_id)
                        }
                      </span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="font-medium">Distance:</span>
                    <span>{formData.receiver_distance} meters</span>
                  </div>
                </CardContent>
              </Card>

              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Click "Calculate" to generate your comprehensive noise assessment including notifications, compliance requirements, and mitigation measures.
                </AlertDescription>
              </Alert>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  if (result) {
    return (
      <div className="container mx-auto p-6">
        <Button onClick={() => {
          setResult(null);
          setCurrentStep(0);
        }} className="mb-4">
          <ChevronLeft className="h-4 w-4 mr-2" />
          Start New Assessment
        </Button>
        <ComprehensiveResults result={result} />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Noise Assessment Wizard</h1>
        <p className="text-muted-foreground">
          Step-by-step guidance through your noise impact assessment
        </p>
      </div>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Step {currentStep + 1} of {steps.length}</span>
          <span className="text-sm text-muted-foreground">{steps[currentStep].title}</span>
        </div>
        <Progress value={calculateProgress()} className="w-full" />
      </div>

      {/* Step Navigation */}
      <div className="flex items-center justify-center mb-6 space-x-2">
        {steps.map((step, index) => (
          <div
            key={step.id}
            className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-colors ${
              index === currentStep
                ? 'border-blue-500 bg-blue-500 text-white'
                : index < currentStep
                ? 'border-green-500 bg-green-500 text-white'
                : 'border-gray-300 text-gray-400'
            }`}
          >
            {index < currentStep ? (
              <CheckCircle className="h-5 w-5" />
            ) : (
              <step.icon className="h-5 w-5" />
            )}
          </div>
        ))}
      </div>

      {/* Step Content */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          {renderStepContent()}
        </CardContent>
      </Card>

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={prevStep}
          disabled={currentStep === 0}
        >
          <ChevronLeft className="h-4 w-4 mr-2" />
          Previous
        </Button>

        {currentStep === steps.length - 1 ? (
          <Button onClick={handleCalculate} disabled={loading || !formData.assessment_type}>
            {loading && <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-blue-500" />}
            Calculate Assessment
          </Button>
        ) : (
          <Button onClick={nextStep} disabled={!getStepValidity()}>
            Next
            <ChevronRight className="h-4 w-4 ml-2" />
          </Button>
        )}
      </div>

      {error && (
        <Alert variant="destructive" className="mt-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  );

  function getStepValidity() {
    switch (currentStep) {
      case 0: return !!formData.assessment_type;
      case 1: return !!formData.calculation_mode;
      case 2: return !!formData.environment_approach;
      case 3: return !!formData.time_period;
      case 4: return !!formData.propagation_type;
      case 5: return !!formData.noise_category_id;
      case 6: return formData.calculation_mode !== "scenario" || !!formData.scenario_id;
      case 7: return !!formData.receiver_distance;
      default: return true;
    }
  }
}
