"""
Main CLI interface for the noise estimator system.
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

import click
import rich
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt, Choice
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.dataset import DatasetManager
from ..core.calculator import NoiseCalculator
from ..extract.dataset_extractor import DatasetExtractor
from ..models.schemas import (
    EstimationRequest,
    AssessmentType,
    CalculationMode,
    EnvironmentApproach,
    TimePeriod,
    PropagationType,
    OutputPack,
)

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('noise_estimator.log')
        ]
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, verbose):
    """Noise Estimator Automation System CLI."""
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@cli.command()
@click.option('--workbook', '-w', required=True, help='Path to Excel workbook file')
@click.option('--out', '-o', default='datasets', help='Output directory for datasets')
@click.pass_context
def extract_dataset(ctx, workbook: str, out: str):
    """Extract dataset from Excel workbook."""
    console.print(f"[bold green]Extracting dataset from: {workbook}[/bold green]")
    
    try:
        extractor = DatasetExtractor()
        version = extractor.extract_dataset(workbook, out)
        
        console.print(f"[bold green]✓[/bold green] Dataset extracted successfully!")
        console.print(f"Version: {version}")
        console.print(f"Output directory: {out}/{version}")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Extraction failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', type=click.Path(exists=True), help='Input JSON file')
@click.option('--output', '-o', type=click.Path(), help='Output JSON file')
@click.option('--dataset-dir', '-d', default='datasets', help='Dataset directory')
@click.pass_context
def run(ctx, input: Optional[str], output: Optional[str], dataset_dir: str):
    """Run noise estimation calculation."""
    try:
        # Initialize components
        dataset_manager = DatasetManager(dataset_dir)
        calculator = NoiseCalculator(dataset_manager)
        
        if input:
            # Non-interactive mode
            run_non_interactive(calculator, input, output)
        else:
            # Interactive mode
            run_interactive(calculator, output)
            
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Calculation failed: {e}")
        if ctx.obj['verbose']:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


def run_non_interactive(calculator: NoiseCalculator, input_file: str, output_file: Optional[str]):
    """Run calculation in non-interactive mode."""
    console.print(f"[bold blue]Running non-interactive calculation...[/bold blue]")
    
    # Load request from file
    with open(input_file, 'r') as f:
        request_data = json.load(f)
    
    request = EstimationRequest(**request_data)
    
    # Perform calculation
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Calculating noise levels...", total=None)
        result = calculator.calculate(request)
        progress.update(task, completed=True)
    
    # Save result
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result.dict(), f, indent=2, default=str)
        console.print(f"[bold green]✓[/bold green] Results saved to: {output_file}")
    else:
        console.print_json(json.dumps(result.dict(), indent=2, default=str))
    
    # Print summary
    print_result_summary(result)


def run_interactive(calculator: NoiseCalculator, output_file: Optional[str]):
    """Run calculation in interactive mode."""
    console.print(Panel.fit(
        "[bold blue]Noise Estimator Interactive Mode[/bold blue]\n"
        "Follow the prompts to configure your noise assessment.",
        title="Welcome"
    ))
    
    # Load available data
    try:
        dataset = calculator.dataset_manager.get_current_dataset()
        if not dataset:
            console.print("[bold red]✗[/bold red] No dataset loaded. Please extract a dataset first.")
            return
        
        categories = calculator.dataset_manager.get_noise_categories()
        scenarios = calculator.dataset_manager.get_scenarios()
        plants = calculator.dataset_manager.get_plants()
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Failed to load dataset: {e}")
        return
    
    # Collect user input
    request_data = collect_user_input(categories, scenarios, plants)
    
    # Show preview
    console.print("\n[bold yellow]Request Preview:[/bold yellow]")
    console.print_json(json.dumps(request_data, indent=2))
    
    if not Confirm.ask("Proceed with calculation?"):
        console.print("Calculation cancelled.")
        return
    
    # Perform calculation
    request = EstimationRequest(**request_data)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Calculating noise levels...", total=None)
        result = calculator.calculate(request)
        progress.update(task, completed=True)
    
    # Display results
    display_interactive_results(result)
    
    # Save if requested
    if output_file or Confirm.ask("Save results to file?"):
        if not output_file:
            output_file = Prompt.ask("Enter output filename", default="noise_result.json")
        
        with open(output_file, 'w') as f:
            json.dump(result.dict(), f, indent=2, default=str)
        console.print(f"[bold green]✓[/bold green] Results saved to: {output_file}")


def collect_user_input(categories: Dict, scenarios: Dict, plants: Dict) -> Dict[str, Any]:
    """Collect input from user interactively."""
    request_data = {}
    
    # Assessment type
    assessment_choices = [
        ("Distance Based", AssessmentType.DISTANCE_BASED.value),
        ("Full Estimator", AssessmentType.FULL_ESTIMATOR.value)
    ]
    assessment_choice = Choice([choice[0] for choice in assessment_choices])
    assessment_display = Prompt.ask(
        "Assessment type",
        choices=assessment_choices,
        default=assessment_choices[0][0]
    )
    request_data['assessment_type'] = next(
        choice[1] for choice in assessment_choices if choice[0] == assessment_display
    )
    
    # Calculation mode
    if request_data['assessment_type'] == AssessmentType.FULL_ESTIMATOR.value:
        mode_choices = [
            ("Scenario", CalculationMode.SCENARIO.value),
            ("Individual Plant", CalculationMode.INDIVIDUAL_PLANT.value)
        ]
    else:  # DISTANCE_BASED
        mode_choices = [
            ("Scenario", CalculationMode.SCENARIO.value),
            ("Noisiest Plant", CalculationMode.NOISIEST_PLANT.value)
        ]
    
    mode_display = Prompt.ask(
        "Calculation mode",
        choices=[choice[0] for choice in mode_choices],
        default=mode_choices[0][0]
    )
    request_data['calculation_mode'] = next(
        choice[1] for choice in mode_choices if choice[0] == mode_display
    )
    
    # Environment approach
    env_choices = [
        ("Representative Noise Environment", EnvironmentApproach.REPRESENTATIVE_NOISE_ENVIRONMENT.value),
        ("User Supplied Background Level", EnvironmentApproach.USER_SUPPLIED_BACKGROUND_LEVEL.value)
    ]
    env_display = Prompt.ask(
        "Environment approach",
        choices=[choice[0] for choice in env_choices],
        default=env_choices[0][0]
    )
    request_data['environment_approach'] = next(
        choice[1] for choice in env_choices if choice[0] == env_display
    )
    
    # Time period
    period_choices = [
        ("Day", TimePeriod.DAY.value),
        ("Evening", TimePeriod.EVENING.value),
        ("Night", TimePeriod.NIGHT.value)
    ]
    period_display = Prompt.ask(
        "Time period",
        choices=[choice[0] for choice in period_choices],
        default=period_choices[0][0]
    )
    request_data['time_period'] = next(
        choice[1] for choice in period_choices if choice[0] == period_display
    )
    
    # Propagation type
    prop_choices = [
        ("Rural", PropagationType.RURAL.value),
        ("Urban", PropagationType.URBAN.value),
        ("Hard Ground", PropagationType.HARD_GROUND.value),
        ("Soft Ground", PropagationType.SOFT_GROUND.value),
        ("Mixed", PropagationType.MIXED.value)
    ]
    prop_display = Prompt.ask(
        "Propagation type",
        choices=[choice[0] for choice in prop_choices],
        default=prop_choices[0][0]
    )
    request_data['propagation_type'] = next(
        choice[1] for choice in prop_choices if choice[0] == prop_display
    )
    
    # Noise category
    if categories:
        category_table = Table(title="Available Noise Categories")
        category_table.add_column("ID", style="cyan")
        category_table.add_column("Name", style="white")
        category_table.add_column("Description", style="dim")
        
        for cat_id, category in categories.items():
            category_table.add_row(
                cat_id,
                category.name,
                category.description or ""
            )
        
        console.print(category_table)
        
        category_id = Prompt.ask(
            "Select noise category ID",
            choices=list(categories.keys()),
            default=list(categories.keys())[0]
        )
        request_data['noise_category_id'] = category_id
    else:
        console.print("[bold yellow]Warning:[/bold yellow] No noise categories available")
        request_data['noise_category_id'] = Prompt.ask("Enter noise category ID")
    
    # Scenario or plant selection
    if request_data['calculation_mode'] in [CalculationMode.SCENARIO.value, CalculationMode.NOISIEST_PLANT.value]:
        if scenarios:
            scenario_table = Table(title="Available Scenarios")
            scenario_table.add_column("ID", style="cyan")
            scenario_table.add_column("Name", style="white")
            scenario_table.add_column("Description", style="dim")
            
            for scen_id, scenario in scenarios.items():
                scenario_table.add_row(
                    scen_id,
                    scenario.name,
                    scenario.description or ""
                )
            
            console.print(scenario_table)
            
            scenario_id = Prompt.ask(
                "Select scenario ID",
                choices=list(scenarios.keys()),
                default=list(scenarios.keys())[0]
            )
            request_data['scenario_id'] = scenario_id
        else:
            console.print("[bold yellow]Warning:[/bold yellow] No scenarios available")
            request_data['scenario_id'] = Prompt.ask("Enter scenario ID")
    
    elif request_data['calculation_mode'] == CalculationMode.INDIVIDUAL_PLANT.value:
        if plants:
            plant_table = Table(title="Available Plants")
            plant_table.add_column("ID", style="cyan")
            plant_table.add_column("Name", style="white")
            plant_table.add_column("SWL (dB)", style="yellow")
            plant_table.add_column("Category", style="dim")
            
            for plant_id, plant in plants.items():
                plant_table.add_row(
                    plant_id,
                    plant.name,
                    str(plant.sound_power_level),
                    plant.category or ""
                )
            
            console.print(plant_table)
            
            selected_plants = []
            while True:
                plant_id = Prompt.ask(
                    "Select plant ID (or press Enter to finish)",
                    choices=list(plants.keys()) + [""],
                    default=""
                )
                if not plant_id:
                    break
                if plant_id not in selected_plants:
                    selected_plants.append(plant_id)
                    console.print(f"  Added: {plant_id}")
                else:
                    console.print(f"  Already selected: {plant_id}")
            
            if not selected_plants:
                console.print("[bold red]At least one plant must be selected[/bold red]")
                return collect_user_input(categories, scenarios, plants)
            
            request_data['plant_ids'] = selected_plants
        else:
            console.print("[bold yellow]Warning:[/bold yellow] No plants available")
            plant_ids_str = Prompt.ask("Enter plant IDs (comma-separated)")
            request_data['plant_ids'] = [pid.strip() for pid in plant_ids_str.split(',')]
    
    # User background level (if required)
    if request_data['environment_approach'] == EnvironmentApproach.USER_SUPPLIED_BACKGROUND_LEVEL.value:
        request_data['user_background_level'] = FloatPrompt.ask(
            "Enter background noise level (dB)",
            default=45.0
        )
    
    # Receiver distance (for full estimator)
    if request_data['assessment_type'] == AssessmentType.FULL_ESTIMATOR.value:
        request_data['receiver_distance'] = FloatPrompt.ask(
            "Enter receiver distance (m)",
            default=50.0
        )
    
    # Output options
    output_choices = [
        ("JSON Only", OutputPack.NONE.value),
        ("Step 2 Memo", OutputPack.STEP2.value),
        ("REF Section", OutputPack.REF.value),
        ("Both Memo Packs", OutputPack.BOTH.value)
    ]
    output_display = Prompt.ask(
        "Output format",
        choices=[choice[0] for choice in output_choices],
        default=output_choices[0][0]
    )
    request_data['output_pack'] = next(
        choice[1] for choice in output_choices if choice[0] == output_display
    )
    
    # Include trace
    request_data['include_trace'] = Confirm.ask("Include calculation trace?", default=False)
    
    return request_data


def display_interactive_results(result):
    """Display results in interactive mode."""
    console.print("\n[bold green]Calculation Results:[/bold green]")
    
    # Results table
    results_table = Table(title="Noise Assessment Results")
    results_table.add_column("Parameter", style="cyan")
    results_table.add_column("Value", style="white")
    
    results_table.add_row("Predicted Level", f"{result.predicted_level_db} dB")
    results_table.add_row("Background Level", f"{result.background_db} dB")
    results_table.add_row("NML Level", f"{result.nml_db} dB")
    results_table.add_row("Exceedance Above Background", f"{result.exceed_background_db} dB")
    results_table.add_row("Exceedance Above NML", f"{result.exceed_nml_db} dB")
    results_table.add_row("Impact Band", result.impact_band.value.replace('_', ' ').title())
    
    console.print(results_table)
    
    # Distance results (if available)
    if result.distances:
        distance_table = Table(title="Distance Analysis")
        distance_table.add_column("Metric", style="cyan")
        distance_table.add_column("Distance (m)", style="white")
        
        if result.distances.distance_to_exceed_background:
            distance_table.add_row("To Exceed Background", f"{result.distances.distance_to_exceed_background}")
        if result.distances.distance_to_nml:
            distance_table.add_row("To NML", f"{result.distances.distance_to_nml}")
        if result.distances.distance_to_highly_affected:
            distance_table.add_row("To Highly Affected", f"{result.distances.distance_to_highly_affected}")
        
        console.print(distance_table)
    
    # Mitigation measures
    if result.standard_measures:
        console.print("\n[bold yellow]Standard Mitigation Measures:[/bold yellow]")
        for measure in result.standard_measures:
            console.print(f"• {measure.title}: {measure.text}")
    
    if result.additional_measures:
        console.print("\n[bold yellow]Additional Mitigation Measures:[/bold yellow]")
        for measure in result.additional_measures:
            console.print(f"• {measure.title}: {measure.text}")
    
    # Narrative packs (if available)
    if result.step2_memo_pack:
        console.print("\n[bold blue]Step 2 Memo Pack:[/bold blue]")
        console.print(Panel(result.step2_memo_pack, title="Step 2 Memo"))
    
    if result.ref_noise_pack:
        console.print("\n[bold blue]REF Noise Section:[/bold blue]")
        console.print(Panel(result.ref_noise_pack[:500] + "..." if len(result.ref_noise_pack) > 500 else result.ref_noise_pack, 
                           title="REF Section (Preview)"))


def print_result_summary(result):
    """Print a brief result summary."""
    console.print(f"\n[bold green]Calculation Summary:[/bold green]")
    console.print(f"Predicted Level: {result.predicted_level_db} dB")
    console.print(f"Background: {result.background_db} dB (exceeds by {result.exceed_background_db} dB)")
    console.print(f"NML: {result.nml_db} dB (exceeds by {result.exceed_nml_db} dB)")
    console.print(f"Impact Band: {result.impact_band.value.replace('_', ' ').title()}")
    
    if result.distances:
        console.print(f"Distance to exceed background: {result.distances.distance_to_exceed_background} m")


@cli.command()
@click.option('--dataset-dir', '-d', default='datasets', help='Dataset directory')
@click.pass_context
def list_scenarios(ctx, dataset_dir: str):
    """List available scenarios."""
    try:
        dataset_manager = DatasetManager(dataset_dir)
        dataset = dataset_manager.load_dataset()
        scenarios = dataset_manager.get_scenarios(dataset)
        
        if not scenarios:
            console.print("[bold yellow]No scenarios found in dataset[/bold yellow]")
            return
        
        table = Table(title="Available Scenarios")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Description", style="dim")
        table.add_column("Propagation Type", style="green")
        
        for scen_id, scenario in scenarios.items():
            table.add_row(
                scen_id,
                scenario.name,
                scenario.description or "",
                scenario.propagation_type.value
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Failed to list scenarios: {e}")


@cli.command()
@click.option('--dataset-dir', '-d', default='datasets', help='Dataset directory')
@click.pass_context
def list_plants(ctx, dataset_dir: str):
    """List available plants."""
    try:
        dataset_manager = DatasetManager(dataset_dir)
        dataset = dataset_manager.load_dataset()
        plants = dataset_manager.get_plants(dataset)
        
        if not plants:
            console.print("[bold yellow]No plants found in dataset[/bold yellow]")
            return
        
        table = Table(title="Available Plants")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("SWL (dB)", style="yellow")
        table.add_column("Category", style="dim")
        table.add_column("Duty Cycle", style="green")
        
        for plant_id, plant in plants.items():
            table.add_row(
                plant_id,
                plant.name,
                str(plant.sound_power_level),
                plant.category or "",
                str(plant.duty_cycle)
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Failed to list plants: {e}")


@cli.command()
@click.option('--dataset-dir', '-d', default='datasets', help='Dataset directory')
@click.pass_context
def list_categories(ctx, dataset_dir: str):
    """List available noise categories."""
    try:
        dataset_manager = DatasetManager(dataset_dir)
        dataset = dataset_manager.load_dataset()
        categories = dataset_manager.get_noise_categories(dataset)
        
        if not categories:
            console.print("[bold yellow]No noise categories found in dataset[/bold yellow]")
            return
        
        table = Table(title="Available Noise Categories")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Description", style="dim")
        table.add_column("Day NML", style="green")
        table.add_column("Night NML", style="blue")
        
        for cat_id, category in categories.items():
            day_nml = category.nml_values.get("day", "N/A")
            night_nml = category.nml_values.get("night", "N/A")
            
            table.add_row(
                cat_id,
                category.name,
                category.description or "",
                str(day_nml),
                str(night_nml)
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Failed to list categories: {e}")


@cli.command()
@click.option('--dataset-dir', '-d', default='datasets', help='Dataset directory')
@click.pass_context
def validate(ctx, dataset_dir: str):
    """Validate calculations against worked examples."""
    try:
        dataset_manager = DatasetManager(dataset_dir)
        dataset = dataset_manager.load_dataset()
        calculator = NoiseCalculator(dataset_manager)
        
        # Get worked examples
        worked_examples = dataset.tables.get("worked_examples", [])
        
        if not worked_examples:
            console.print("[bold yellow]No worked examples found in dataset[/bold yellow]")
            return
        
        console.print(f"[bold blue]Validating {len(worked_examples)} worked examples...[/bold blue]")
        
        passed = 0
        failed = 0
        tolerance_db = 0.2
        tolerance_distance = 1.0
        
        with Progress(console=console) as progress:
            task = progress.add_task("Validating examples...", total=len(worked_examples))
            
            for example in worked_examples:
                try:
                    # Create request from example inputs
                    inputs = example["inputs"]
                    request = EstimationRequest(**inputs)
                    
                    # Calculate result
                    result = calculator.calculate(request)
                    
                    # Get expected outputs
                    expected = example["expected_outputs"]
                    
                    # Validate
                    example_passed = True
                    
                    for field, expected_value in expected.items():
                        if field.endswith("_db"):
                            actual_value = getattr(result, field, None)
                            if actual_value is None or abs(actual_value - expected_value) > tolerance_db:
                                example_passed = False
                                break
                        elif field.startswith("distance_to_"):
                            if result.distances is None:
                                example_passed = False
                                break
                            actual_value = getattr(result.distances, field, None)
                            if actual_value is None or abs(actual_value - expected_value) > tolerance_distance:
                                example_passed = False
                                break
                        elif field == "impact_band":
                            if result.impact_band.value != expected_value:
                                example_passed = False
                                break
                    
                    if example_passed:
                        passed += 1
                    else:
                        failed += 1
                        console.print(f"[bold red]✗[/bold red] {example.get('id', 'Unknown')} failed")
                
                except Exception as e:
                    failed += 1
                    console.print(f"[bold red]✗[/bold red] {example.get('id', 'Unknown')} error: {e}")
                
                progress.advance(task)
        
        # Summary
        console.print(f"\n[bold green]Validation Summary:[/bold green]")
        console.print(f"Passed: {passed}")
        console.print(f"Failed: {failed}")
        console.print(f"Total: {len(worked_examples)}")
        
        if failed == 0:
            console.print("[bold green]✓[/bold green] All worked examples passed!")
        else:
            console.print(f"[bold red]✗[/bold red] {failed} examples failed validation")
            sys.exit(1)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Validation failed: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    cli()
