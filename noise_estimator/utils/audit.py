"""
Audit and logging utilities for the noise estimator system.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
from contextlib import contextmanager

from ..models.schemas import EstimationRequest, EstimationResult, CalculationTrace


class AuditLogger:
    """Enhanced logging for audit and traceability purposes."""
    
    def __init__(self, log_dir: Optional[Union[str, Path]] = None):
        """Initialize audit logger.
        
        Args:
            log_dir: Directory for audit logs. Defaults to 'logs/'.
        """
        self.log_dir = Path(log_dir) if log_dir else Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup structured logger
        self.logger = logging.getLogger("noise_estimator.audit")
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # File handler for structured logs
        file_handler = logging.FileHandler(self.log_dir / "audit.jsonl")
        file_handler.setLevel(logging.INFO)
        
        # Console handler for important events
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_calculation_request(self, request: EstimationRequest, request_id: str):
        """Log a calculation request."""
        log_entry = {
            "event_type": "calculation_request",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "dataset_version": request.dataset_version,
            "assessment_type": request.assessment_type.value,
            "calculation_mode": request.calculation_mode.value,
            "environment_approach": request.environment_approach.value,
            "time_period": request.time_period.value,
            "propagation_type": request.propagation_type.value,
            "noise_category_id": request.noise_category_id,
            "scenario_id": request.scenario_id,
            "plant_ids": request.plant_ids,
            "receiver_distance": request.receiver_distance,
            "user_background_level": request.user_background_level,
            "include_trace": request.include_trace,
            "output_pack": request.output_pack.value
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def log_calculation_result(self, result: EstimationResult):
        """Log a calculation result."""
        log_entry = {
            "event_type": "calculation_result",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": result.request_id,
            "dataset_version": result.dataset_version,
            "workbook_hash": result.workbook_hash,
            "predicted_level_db": result.predicted_level_db,
            "background_db": result.background_db,
            "nml_db": result.nml_db,
            "exceed_background_db": result.exceed_background_db,
            "exceed_nml_db": result.exceed_nml_db,
            "impact_band": result.impact_band.value,
            "standard_measures_count": len(result.standard_measures),
            "additional_measures_count": len(result.additional_measures),
            "has_trace": result.trace is not None,
            "has_step2_memo": result.step2_memo_pack is not None,
            "has_ref_pack": result.ref_noise_pack is not None
        }
        
        if result.distances:
            log_entry["distances"] = {
                "distance_to_exceed_background": result.distances.distance_to_exceed_background,
                "distance_to_nml": result.distances.distance_to_nml,
                "distance_to_highly_affected": result.distances.distance_to_highly_affected
            }
        
        self.logger.info(json.dumps(log_entry))
    
    def log_calculation_trace(self, request_id: str, trace: CalculationTrace):
        """Log detailed calculation trace."""
        log_entry = {
            "event_type": "calculation_trace",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "tables_used": trace.tables_used,
            "intermediate_values": trace.intermediate_values,
            "warnings": trace.warnings,
            "assumptions": trace.assumptions
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def log_dataset_load(self, dataset_version: str, success: bool, error: Optional[str] = None):
        """Log dataset loading event."""
        log_entry = {
            "event_type": "dataset_load",
            "timestamp": datetime.utcnow().isoformat(),
            "dataset_version": dataset_version,
            "success": success,
            "error": error
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def log_dataset_extraction(self, workbook_path: str, version: str, success: bool, error: Optional[str] = None):
        """Log dataset extraction event."""
        log_entry = {
            "event_type": "dataset_extraction",
            "timestamp": datetime.utcnow().isoformat(),
            "workbook_path": str(workbook_path),
            "version": version,
            "success": success,
            "error": error
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def log_validation_result(self, validation_type: str, total: int, passed: int, failed: int, details: Optional[Dict] = None):
        """Log validation results."""
        log_entry = {
            "event_type": "validation_result",
            "timestamp": datetime.utcnow().isoformat(),
            "validation_type": validation_type,
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": passed / total if total > 0 else 0,
            "details": details
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def log_api_request(self, endpoint: str, method: str, request_id: str, user_agent: Optional[str] = None):
        """Log API request."""
        log_entry = {
            "event_type": "api_request",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "request_id": request_id,
            "user_agent": user_agent
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def log_api_response(self, endpoint: str, request_id: str, status_code: int, duration_ms: Optional[float] = None):
        """Log API response."""
        log_entry = {
            "event_type": "api_response",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": endpoint,
            "request_id": request_id,
            "status_code": status_code,
            "duration_ms": duration_ms
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict] = None):
        """Log error event."""
        log_entry = {
            "event_type": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "context": context
        }
        
        self.logger.error(json.dumps(log_entry))
    
    def log_warning(self, warning_type: str, warning_message: str, context: Optional[Dict] = None):
        """Log warning event."""
        log_entry = {
            "event_type": "warning",
            "timestamp": datetime.utcnow().isoformat(),
            "warning_type": warning_type,
            "warning_message": warning_message,
            "context": context
        }
        
        self.logger.warning(json.dumps(log_entry))


class CalculationReportGenerator:
    """Generate human-readable calculation reports for audit purposes."""
    
    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """Initialize report generator.
        
        Args:
            output_dir: Directory for reports. Defaults to 'reports/'.
        """
        self.output_dir = Path(output_dir) if output_dir else Path("reports")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_report(self, request: EstimationRequest, result: EstimationResult) -> Path:
        """Generate a comprehensive calculation report.
        
        Args:
            request: The estimation request.
            result: The calculation result.
            
        Returns:
            Path to the generated report file.
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"calculation_report_{result.request_id[:8]}_{timestamp}.txt"
        report_path = self.output_dir / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            self._write_report(f, request, result)
        
        return report_path
    
    def _write_report(self, f, request: EstimationRequest, result: EstimationResult):
        """Write the report content to file."""
        f.write("=" * 80 + "\n")
        f.write("NOISE ESTIMATOR CALCULATION REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        # Header information
        f.write("REPORT METADATA\n")
        f.write("-" * 40 + "\n")
        f.write(f"Request ID: {result.request_id}\n")
        f.write(f"Generated: {result.timestamp.isoformat()}\n")
        f.write(f"Dataset Version: {result.dataset_version}\n")
        f.write(f"Workbook Hash: {result.workbook_hash[:16]}...\n\n")
        
        # Input parameters
        f.write("INPUT PARAMETERS\n")
        f.write("-" * 40 + "\n")
        f.write(f"Assessment Type: {request.assessment_type.value.replace('_', ' ').title()}\n")
        f.write(f"Calculation Mode: {request.calculation_mode.value.replace('_', ' ').title()}\n")
        f.write(f"Environment Approach: {request.environment_approach.value.replace('_', ' ').title()}\n")
        f.write(f"Time Period: {request.time_period.value.title()}\n")
        f.write(f"Propagation Type: {request.propagation_type.value.replace('_', ' ').title()}\n")
        f.write(f"Noise Category: {request.noise_category_id}\n")
        
        if request.scenario_id:
            f.write(f"Scenario: {request.scenario_id}\n")
        
        if request.plant_ids:
            f.write(f"Plants: {', '.join(request.plant_ids)}\n")
        
        if request.receiver_distance:
            f.write(f"Receiver Distance: {request.receiver_distance} m\n")
        
        if request.user_background_level:
            f.write(f"User Background Level: {request.user_background_level} dB\n")
        
        f.write("\n")
        
        # Results summary
        f.write("CALCULATION RESULTS\n")
        f.write("-" * 40 + "\n")
        f.write(f"Predicted Level: {result.predicted_level_db} dB LAeq(15min)\n")
        f.write(f"Background Level: {result.background_db} dB\n")
        f.write(f"Noise Management Level: {result.nml_db} dB\n")
        f.write(f"Exceedance Above Background: {result.exceed_background_db} dB\n")
        f.write(f"Exceedance Above NML: {result.exceed_nml_db} dB\n")
        f.write(f"Impact Band: {result.impact_band.value.replace('_', ' ').title()}\n\n")
        
        # Distance results (if applicable)
        if result.distances:
            f.write("DISTANCE ANALYSIS\n")
            f.write("-" * 40 + "\n")
            if result.distances.distance_to_exceed_background:
                f.write(f"Distance to Exceed Background: {result.distances.distance_to_exceed_background} m\n")
            if result.distances.distance_to_nml:
                f.write(f"Distance to NML: {result.distances.distance_to_nml} m\n")
            if result.distances.distance_to_highly_affected:
                f.write(f"Distance to Highly Affected: {result.distances.distance_to_highly_affected} m\n")
            f.write("\n")
        
        # Mitigation measures
        if result.standard_measures:
            f.write("STANDARD MITIGATION MEASURES\n")
            f.write("-" * 40 + "\n")
            for i, measure in enumerate(result.standard_measures, 1):
                f.write(f"{i}. {measure.title}\n")
                f.write(f"   {measure.text}\n")
                if measure.reduction_db:
                    f.write(f"   Estimated reduction: {measure.reduction_db} dB\n")
                f.write("\n")
        
        if result.additional_measures:
            f.write("ADDITIONAL MITIGATION MEASURES\n")
            f.write("-" * 40 + "\n")
            for i, measure in enumerate(result.additional_measures, 1):
                f.write(f"{i}. {measure.title}\n")
                f.write(f"   {measure.text}\n")
                if measure.reduction_db:
                    f.write(f"   Estimated reduction: {measure.reduction_db} dB\n")
                f.write("\n")
        
        # Calculation trace (if available)
        if result.trace:
            f.write("CALCULATION TRACE\n")
            f.write("-" * 40 + "\n")
            
            if result.trace.tables_used:
                f.write("Tables Used:\n")
                for table, info in result.trace.tables_used.items():
                    f.write(f"  - {table}: {info}\n")
                f.write("\n")
            
            if result.trace.intermediate_values:
                f.write("Intermediate Values:\n")
                for name, value in result.trace.intermediate_values.items():
                    f.write(f"  - {name}: {value}\n")
                f.write("\n")
            
            if result.trace.assumptions:
                f.write("Assumptions:\n")
                for i, assumption in enumerate(result.trace.assumptions, 1):
                    f.write(f"  {i}. {assumption}\n")
                f.write("\n")
            
            if result.trace.warnings:
                f.write("Warnings:\n")
                for i, warning in enumerate(result.trace.warnings, 1):
                    f.write(f"  {i}. {warning}\n")
                f.write("\n")
        
        # Results table
        f.write("RESULTS TABLE\n")
        f.write("-" * 40 + "\n")
        if result.results_table_markdown:
            f.write(result.results_table_markdown)
        else:
            f.write("No results table generated.\n")
        f.write("\n")
        
        # Narrative packs (if available)
        if result.step2_memo_pack:
            f.write("STEP 2 MEMO PACK\n")
            f.write("-" * 40 + "\n")
            f.write(result.step2_memo_pack)
            f.write("\n\n")
        
        if result.ref_noise_pack:
            f.write("REF NOISE SECTION PACK\n")
            f.write("-" * 40 + "\n")
            f.write(result.ref_noise_pack)
            f.write("\n\n")
        
        # Footer
        f.write("=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")


@contextmanager
def audit_context(audit_logger: AuditLogger, request: EstimationRequest):
    """Context manager for auditing calculations."""
    request_id = str(uuid.uuid4())
    
    # Log request
    audit_logger.log_calculation_request(request, request_id)
    
    try:
        yield request_id
        
        # Result will be logged separately after calculation
    except Exception as e:
        # Log error
        audit_logger.log_error(
            "calculation_error",
            str(e),
            {"request_id": request_id, "assessment_type": request.assessment_type.value}
        )
        raise


# Import uuid for context manager
import uuid
