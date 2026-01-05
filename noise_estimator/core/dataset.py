"""
Dataset management for the noise estimator system.
Handles loading, versioning, and accessing extracted workbook data.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging

from ..models.schemas import (
    ExtractedDataset,
    DatasetMetadata,
    TableMetadata,
    NoiseCategory,
    Scenario,
    Plant,
    MitigationMeasure,
)

logger = logging.getLogger(__name__)


class DatasetManager:
    """Manages dataset loading, versioning, and access."""
    
    def __init__(self, dataset_dir: Optional[Union[str, Path]] = None):
        """Initialize dataset manager.
        
        Args:
            dataset_dir: Directory containing datasets. Defaults to 'datasets/'.
        """
        self.dataset_dir = Path(dataset_dir) if dataset_dir else Path("datasets")
        self._current_dataset: Optional[ExtractedDataset] = None
        self._dataset_cache: Dict[str, ExtractedDataset] = {}
    
    def list_datasets(self) -> List[str]:
        """List available dataset versions."""
        if not self.dataset_dir.exists():
            return []
        
        datasets = []
        for item in self.dataset_dir.iterdir():
            if item.is_dir() and (item / "dataset.json").exists():
                datasets.append(item.name)
        
        return sorted(datasets, reverse=True)
    
    def load_dataset(self, version: Optional[str] = None) -> ExtractedDataset:
        """Load a specific dataset version.
        
        Args:
            version: Dataset version to load. If None, loads latest.
            
        Returns:
            Loaded dataset.
            
        Raises:
            FileNotFoundError: If dataset not found.
        """
        if version is None:
            versions = self.list_datasets()
            if not versions:
                raise FileNotFoundError("No datasets found")
            version = versions[0]
        
        # Check cache first
        if version in self._dataset_cache:
            return self._dataset_cache[version]
        
        dataset_path = self.dataset_dir / version / "dataset.json"
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset {version} not found at {dataset_path}")
        
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            dataset = ExtractedDataset(**data)
            self._dataset_cache[version] = dataset
            self._current_dataset = dataset
            
            logger.info(f"Loaded dataset {version} with {dataset.metadata.total_tables} tables")
            return dataset
            
        except Exception as e:
            logger.error(f"Failed to load dataset {version}: {e}")
            raise
    
    def get_current_dataset(self) -> Optional[ExtractedDataset]:
        """Get currently loaded dataset."""
        return self._current_dataset
    
    def get_table(self, table_name: str, dataset: Optional[ExtractedDataset] = None) -> Any:
        """Get a specific table from the dataset.
        
        Args:
            table_name: Name of table to retrieve.
            dataset: Dataset to use. If None, uses current.
            
        Returns:
            Table data.
            
        Raises:
            KeyError: If table not found.
        """
        ds = dataset or self._current_dataset
        if not ds:
            raise ValueError("No dataset loaded")
        
        if table_name not in ds.tables:
            raise KeyError(f"Table '{table_name}' not found in dataset")
        
        return ds.tables[table_name]
    
    def get_noise_categories(self, dataset: Optional[ExtractedDataset] = None) -> Dict[str, NoiseCategory]:
        """Get noise categories from dataset."""
        try:
            categories_data = self.get_table("noise_categories", dataset)
            categories = {}
            
            for cat_data in categories_data:
                category = NoiseCategory(**cat_data)
                categories[category.id] = category
            
            return categories
            
        except KeyError:
            logger.warning("No noise_categories table found in dataset")
            return {}
    
    def get_scenarios(self, dataset: Optional[ExtractedDataset] = None) -> Dict[str, Scenario]:
        """Get scenarios from dataset."""
        try:
            scenarios_data = self.get_table("scenarios", dataset)
            scenarios = {}
            
            for scen_data in scenarios_data:
                scenario = Scenario(**scen_data)
                scenarios[scenario.id] = scenario
            
            return scenarios
            
        except KeyError:
            logger.warning("No scenarios table found in dataset")
            return {}
    
    def get_plants(self, dataset: Optional[ExtractedDataset] = None) -> Dict[str, Plant]:
        """Get plants from dataset."""
        try:
            plants_data = self.get_table("plants", dataset)
            plants = {}
            
            for plant_data in plants_data:
                plant = Plant(**plant_data)
                plants[plant.id] = plant
            
            return plants
            
        except KeyError:
            logger.warning("No plants table found in dataset")
            return {}
    
    def get_mitigation_measures(self, dataset: Optional[ExtractedDataset] = None) -> Dict[str, MitigationMeasure]:
        """Get mitigation measures from dataset."""
        try:
            measures_data = self.get_table("mitigation_measures", dataset)
            measures = {}
            
            for measure_data in measures_data:
                measure = MitigationMeasure(**measure_data)
                measures[measure.id] = measure
            
            return measures
            
        except KeyError:
            logger.warning("No mitigation_measures table found in dataset")
            return {}
    
    def get_concawe_data(self, dataset: Optional[Any] = None) -> Dict[str, Any]:
        """Get Concawe propagation attenuation data."""
        if dataset is None:
            dataset = self._current_dataset
        
        # Try to load from separate Concawe file first
        concawe_file = self.dataset_dir / "concawe_propagation.json"
        if concawe_file.exists():
            with open(concawe_file, 'r') as f:
                concawe_dataset = json.load(f)
            return concawe_dataset.get("concawe_attenuation", {})
        
        # Fall back to data in main dataset
        # Handle both ExtractedDataset objects and dictionaries
        if hasattr(dataset, 'tables'):
            # ExtractedDataset object
            return dataset.tables.get("concawe_attenuation", {})
        elif isinstance(dataset, dict):
            # Plain dictionary
            return dataset.get("concawe_attenuation", {})
        else:
            return {}
    
    def get_background_levels(self, dataset: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get background level data."""
        try:
            return self.get_table("background_levels", dataset)
        except KeyError:
            logger.warning("No background_levels table found in dataset")
            return {}
    
    def get_propagation_data(self, dataset: Optional[ExtractedDataset] = None) -> Dict[str, Any]:
        """Get propagation calculation data."""
        try:
            return self.get_table("propagation_data", dataset)
        except KeyError:
            logger.warning("No propagation_data table found in dataset")
            return {}
    
    def get_distance_tables(self, dataset: Optional[ExtractedDataset] = None) -> Dict[str, Any]:
        """Get distance calculation tables."""
        try:
            return self.get_table("distance_tables", dataset)
        except KeyError:
            logger.warning("No distance_tables table found in dataset")
            return {}
    
    def validate_dataset(self, dataset: ExtractedDataset) -> List[str]:
        """Validate dataset completeness.
        
        Args:
            dataset: Dataset to validate.
            
        Returns:
            List of validation warnings/errors.
        """
        issues = []
        required_tables = [
            "noise_categories",
            "scenarios", 
            "plants",
            "mitigation_measures",
            "background_levels",
            "propagation_data"
        ]
        
        for table_name in required_tables:
            if table_name not in dataset.tables:
                issues.append(f"Missing required table: {table_name}")
        
        # Validate data integrity
        try:
            categories = self.get_noise_categories(dataset)
            if not categories:
                issues.append("No noise categories found")
            
            scenarios = self.get_scenarios(dataset)
            if not scenarios:
                issues.append("No scenarios found")
            
            plants = self.get_plants(dataset)
            if not plants:
                issues.append("No plants found")
                
        except Exception as e:
            issues.append(f"Data validation error: {e}")
        
        return issues
    
    def get_dataset_info(self, version: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a dataset version."""
        try:
            dataset = self.load_dataset(version)
            issues = self.validate_dataset(dataset)
            
            return {
                "version": dataset.metadata.version,
                "workbook_name": dataset.metadata.workbook_name,
                "extraction_timestamp": dataset.metadata.extraction_timestamp,
                "workbook_hash": dataset.metadata.workbook_hash,
                "total_tables": dataset.metadata.total_tables,
                "sheet_count": dataset.metadata.sheet_count,
                "validation_issues": issues,
                "table_names": list(dataset.tables.keys())
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "version": version
            }
    
    def clear_cache(self):
        """Clear dataset cache."""
        self._dataset_cache.clear()
        self._current_dataset = None
