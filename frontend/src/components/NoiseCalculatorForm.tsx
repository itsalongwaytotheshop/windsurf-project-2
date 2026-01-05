"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2 } from "lucide-react";
import ComprehensiveResults from "./ComprehensiveResults";
import { ExtendedEstimationResult } from "@/types/estimator";

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

export default function NoiseCalculatorForm() {
  const [formData, setFormData] = useState<FormData>({
    assessment_type: "distance_based",
    calculation_mode: "scenario",
    environment_approach: "representative_noise_environment",
    time_period: "day",
    propagation_type: "rural",
    noise_category_id: "R1",
    scenario_id: "excavation",
    receiver_distance: "100",
    user_background_level: "",
    include_trace: false,
  });

  const [result, setResult] = useState<ExtendedEstimationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (field: keyof FormData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Calculation failed");
      }

      const calculationResult = await response.json();
      setResult(calculationResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold">Noise Estimator</h1>
        <p className="text-muted-foreground mt-2">Calculate construction and maintenance noise levels with comprehensive compliance requirements</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Calculation Parameters</CardTitle>
          <CardDescription>
            Configure the noise estimation parameters below
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="assessment_type">Assessment Type</Label>
                <Select
                  value={formData.assessment_type}
                  onValueChange={(value) => handleInputChange("assessment_type", value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select assessment type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="distance_based">Distance Based</SelectItem>
                    <SelectItem value="full_estimator">Full Estimator</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="calculation_mode">Calculation Mode</Label>
                <Select
                  value={formData.calculation_mode}
                  onValueChange={(value) => handleInputChange("calculation_mode", value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select calculation mode" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="scenario">Scenario</SelectItem>
                    <SelectItem value="noisiest_plant">Noisiest Plant</SelectItem>
                    <SelectItem value="individual_plant">Individual Plant</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="environment_approach">Environment Approach</Label>
                <Select
                  value={formData.environment_approach}
                  onValueChange={(value) => handleInputChange("environment_approach", value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select environment approach" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="representative_noise_environment">Representative Noise Environment</SelectItem>
                    <SelectItem value="user_supplied_background_level">User Supplied Background Level</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="time_period">Time Period</Label>
                <Select
                  value={formData.time_period}
                  onValueChange={(value) => handleInputChange("time_period", value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select time period" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="day">Day</SelectItem>
                    <SelectItem value="evening">Evening</SelectItem>
                    <SelectItem value="night">Night</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="propagation_type">Propagation Type</Label>
                <Select
                  value={formData.propagation_type}
                  onValueChange={(value) => handleInputChange("propagation_type", value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select propagation type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="rural">Rural</SelectItem>
                    <SelectItem value="urban">Urban</SelectItem>
                    <SelectItem value="hard_ground">Hard Ground</SelectItem>
                    <SelectItem value="soft_ground">Soft Ground</SelectItem>
                    <SelectItem value="mixed">Mixed</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="noise_category_id">Noise Category</Label>
                <Select
                  value={formData.noise_category_id}
                  onValueChange={(value) => handleInputChange("noise_category_id", value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select noise category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="R1">R1 - Rural Residential</SelectItem>
                    <SelectItem value="U2">U2 - Urban Industrial</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {formData.calculation_mode === "scenario" && (
                <div className="space-y-2">
                  <Label htmlFor="scenario_id">Scenario</Label>
                  <Select
                    value={formData.scenario_id}
                    onValueChange={(value) => handleInputChange("scenario_id", value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select scenario" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="excavation">Excavation Works</SelectItem>
                      <SelectItem value="paving">Paving Works</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}

              {formData.assessment_type === "full_estimator" && (
                <div className="space-y-2">
                  <Label htmlFor="receiver_distance">Receiver Distance (m)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={formData.receiver_distance}
                    onChange={(e) => handleInputChange("receiver_distance", e.target.value)}
                    placeholder="Enter distance in meters"
                  />
                </div>
              )}

              {formData.environment_approach === "user_supplied_background_level" && (
                <div className="space-y-2">
                  <Label htmlFor="user_background_level">Background Level (dB)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={formData.user_background_level}
                    onChange={(e) => handleInputChange("user_background_level", e.target.value)}
                    placeholder="Enter background level"
                  />
                </div>
              )}
            </div>

            <Separator />

            <Button type="submit" className="w-full" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Calculate Noise Level & Requirements
            </Button>
          </form>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {result && <ComprehensiveResults result={result} />}
    </div>
  );
}
