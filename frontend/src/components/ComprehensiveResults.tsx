"use client";

import { ExtendedEstimationResult, NotificationRequirement, WorkHourRestriction, ComplianceRequirement } from "@/types/estimator";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { 
  Phone, 
  Mail, 
  FileText, 
  Clock, 
  Users, 
  AlertTriangle, 
  CheckCircle, 
  MapPin,
  Calendar,
  Download,
  Info
} from "lucide-react";

interface ComprehensiveResultsProps {
  result: ExtendedEstimationResult;
}

export default function ComprehensiveResults({ result }: ComprehensiveResultsProps) {
  const getImpactBandColor = (band: string) => {
    switch (band) {
      case "HIGHLY_AFFECTED":
        return "destructive";
      case "AFFECTED":
        return "default";
      case "NOT_AFFECTED":
        return "secondary";
      default:
        return "outline";
    }
  };

  const downloadStep2Memo = () => {
    if (result.step2_memo_pack) {
      const blob = new Blob([result.step2_memo_pack], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `step2_memo_${result.request_id}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const downloadRefPack = () => {
    if (result.ref_noise_pack) {
      const blob = new Blob([result.ref_noise_pack], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ref_noise_pack_${result.request_id}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="space-y-6">
      {/* Results Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Calculation Results
            <Badge variant={getImpactBandColor(result.impact_band)}>
              {result.impact_band.replace("_", " ").toUpperCase()}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-2xl font-bold">{result.predicted_level_db.toFixed(1)}</div>
              <div className="text-sm text-muted-foreground">Predicted Level (dB)</div>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-2xl font-bold">{result.background_db.toFixed(1)}</div>
              <div className="text-sm text-muted-foreground">Background (dB)</div>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-2xl font-bold">{result.exceed_background_db.toFixed(1)}</div>
              <div className="text-sm text-muted-foreground">Exceedance (dB)</div>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-2xl font-bold">{result.distances?.affected_distance || 'N/A'}</div>
              <div className="text-sm text-muted-foreground">Affected Distance (m)</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notification Requirements */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Notification Requirements
          </CardTitle>
          <CardDescription>
            Required notifications based on impact level and distance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {result.notification_requirements.map((req, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {req.type === 'phone_call' && <Phone className="h-4 w-4" />}
                    {req.type === 'letter_drop' && <FileText className="h-4 w-4" />}
                    {req.type === 'email' && <Mail className="h-4 w-4" />}
                    <span className="font-medium capitalize">{req.type.replace('_', ' ')}</span>
                  </div>
                  <Badge variant="outline">{req.timing}</Badge>
                </div>
                <p className="text-sm text-muted-foreground mb-2">{req.description}</p>
                {req.distance_threshold && (
                  <p className="text-xs flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    Required within {req.distance_threshold}m of the work site
                  </p>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Stakeholder Requirements */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Stakeholder Communication
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Stakeholder Group</TableHead>
                <TableHead>Notification Methods</TableHead>
                <TableHead>Timing</TableHead>
                <TableHead>Special Requirements</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {result.stakeholder_requirements.map((stakeholder, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium capitalize">
                    {stakeholder.category.replace('_', ' ')}
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {stakeholder.notification_methods.map((method, i) => (
                        <Badge key={i} variant="secondary" className="text-xs">
                          {method}
                        </Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>{stakeholder.contact_timing}</TableCell>
                  <TableCell>
                    <ul className="text-sm list-disc list-inside">
                      {stakeholder.specific_requirements.map((req, i) => (
                        <li key={i}>{req}</li>
                      ))}
                    </ul>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Work Hour Restrictions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Work Hour Restrictions
          </CardTitle>
          <CardDescription>
            Restrictions based on noise impact assessment
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {result.work_hour_restrictions.map((restriction, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium capitalize">{restriction.period.replace('_', ' ')}</span>
                  <Badge variant={restriction.max_consecutive_days > 0 ? "destructive" : "secondary"}>
                    {restriction.max_consecutive_days > 0 ? 'Restricted' : 'No Limit'}
                  </Badge>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p><strong>Max consecutive days:</strong> {restriction.max_consecutive_days || 'No limit'}</p>
                    <p><strong>Separation required:</strong> {restriction.separation_required} days</p>
                    <p><strong>Max per month:</strong> {restriction.max_per_month || 'No limit'}</p>
                  </div>
                  <div>
                    <p className="font-medium mb-1">Restrictions:</p>
                    <ul className="list-disc list-inside text-muted-foreground">
                      {restriction.restrictions.map((r, i) => (
                        <li key={i}>{r}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Respite Periods */}
      {result.respite_periods.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Respite Period Requirements</CardTitle>
            <CardDescription>Required breaks between noisy work periods</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {result.respite_periods.map((respite, index) => (
                <Alert key={index}>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>{respite.id}:</strong> {respite.description}
                    <div className="mt-2 text-sm">
                      <p>{respite.night_restrictions}</p>
                      <p>{respite.evening_restrictions}</p>
                    </div>
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Compliance Requirements */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            Compliance & Approvals
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {result.compliance_requirements.map((compliance, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{compliance.category}</span>
                  {compliance.approval_needed && (
                    <Badge variant="destructive">Approval Required</Badge>
                  )}
                </div>
                <p className="text-sm text-muted-foreground mb-2">
                  <strong>Timeframe:</strong> {compliance.timeframe}
                </p>
                {compliance.reference_numbers.length > 0 && (
                  <p className="text-sm mb-2">
                    <strong>References:</strong> {compliance.reference_numbers.join(', ')}
                  </p>
                )}
                <ul className="text-sm list-disc list-inside">
                  {compliance.requirements.map((req, i) => (
                    <li key={i}>{req}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Mitigation Measures */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Standard Measures</CardTitle>
            <CardDescription>Required standard mitigation measures</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {result.standard_measures.map((measure, index) => (
                <div key={index} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium">{measure.title}</span>
                    <Badge variant="outline">-{measure.reduction_db} dB</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{measure.description}</p>
                  <div className="flex items-center gap-2 mt-2 text-xs">
                    <span>Cost: {measure.cost}</span>
                    <span>•</span>
                    <span>Time: {measure.implementation_time}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Additional Measures</CardTitle>
            <CardDescription>Additional measures for highly affected areas</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {result.additional_measures.map((measure, index) => (
                <div key={index} className={`border rounded-lg p-3 ${!measure.applicable ? 'opacity-50' : ''}`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium">{measure.title}</span>
                    <div className="flex items-center gap-2">
                      <Badge variant={measure.applicable ? "default" : "secondary"}>
                        {measure.applicable ? 'Applicable' : 'Not Applicable'}
                      </Badge>
                      {measure.applicable && (
                        <Badge variant="outline">-{measure.reduction_db} dB</Badge>
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">{measure.description}</p>
                  {!measure.applicable && measure.reason && (
                    <p className="text-xs text-red-600 mt-1">Reason: {measure.reason}</p>
                  )}
                  {measure.applicable && (
                    <div className="flex items-center gap-2 mt-2 text-xs">
                      <span>Cost: {measure.cost}</span>
                      <span>•</span>
                      <span>Time: {measure.implementation_time}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Documentation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Documentation & Reports
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Step 2 Memo Pack</p>
                <p className="text-sm text-muted-foreground">
                  Comprehensive notification and stakeholder communication plan
                </p>
              </div>
              <Button onClick={downloadStep2Memo} disabled={!result.step2_memo_pack}>
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Reference Noise Section Pack</p>
                <p className="text-sm text-muted-foreground">
                  Technical reference documentation for the noise assessment
                </p>
              </div>
              <Button onClick={downloadRefPack} disabled={!result.ref_noise_pack}>
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Checklist */}
      {result.checklist_items.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5" />
              Pre-Work Checklist
            </CardTitle>
            <CardDescription>
              Items to complete before commencing work
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {result.checklist_items.map((item, index) => (
                <label key={index} className="flex items-center space-x-2 cursor-pointer">
                  <input type="checkbox" className="rounded" />
                  <span className="text-sm">{item.text}</span>
                </label>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Trace Information */}
      {result.trace && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Info className="h-5 w-5" />
              Calculation Trace
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="font-medium mb-2">Data Sources Used:</p>
                <div className="flex flex-wrap gap-1">
                  {result.trace.tables_used.map((table, i) => (
                    <Badge key={i} variant="outline" className="text-xs">
                      {table}
                    </Badge>
                  ))}
                </div>
              </div>
              {result.trace.warnings.length > 0 && (
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>Warnings:</strong>
                    <ul className="mt-1 list-disc list-inside">
                      {result.trace.warnings.map((warning, i) => (
                        <li key={i}>{warning}</li>
                      ))}
                    </ul>
                  </AlertDescription>
                </Alert>
              )}
              <div>
                <p className="font-medium mb-2">Assumptions:</p>
                <ul className="text-sm list-disc list-inside text-muted-foreground">
                  {result.trace.assumptions.map((assumption, i) => (
                    <li key={i}>{assumption}</li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
