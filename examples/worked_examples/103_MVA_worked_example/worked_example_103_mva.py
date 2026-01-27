"""
Worked Example: Hydrogenerator Power Loss Estimation
=====================================================

This worked example demonstrates SynGenLib's power loss estimation workflow.
Configuration data is loaded from external JSON files for flexibility.

Usage:
    python worked_example_103_mva.py [--config CONFIG_FILE] [--operating-points OP_FILE]

Default files:
    - config_103_mva_generator.json
    - operating_points_103_mva.json

"""

from math import sqrt
import logging
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# ==============================================================================
# Argument Parser
# ==============================================================================
def parse_arguments():
    """Parse command-line arguments for configuration files."""
    parser = argparse.ArgumentParser(
        description="SynGenLib Worked Example: Hydrogenerator Power Loss Estimation"
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="config_103_mva_generator.json",
        help="Generator configuration JSON file (default: config_103_mva_generator.json)"
    )
    parser.add_argument(
        "--operating-points", "-o",
        type=str,
        default="operating_points_103_mva.json",
        help="Operating points JSON file (default: operating_points_103_mva.json)"
    )
    return parser.parse_args()

# ==============================================================================
# Configuration Loader Functions
# ==============================================================================
def load_generator_config(config_path: Path) -> dict:
    """Load generator configuration from JSON file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_operating_points(op_path: Path) -> dict:
    """Load operating points from JSON file."""
    with open(op_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ==============================================================================
# Configure Logging: Output to both console and file
# ==============================================================================
def setup_logging(script_dir: Path, config_name: str) -> Path:
    """Setup logging to console and file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = Path(config_name).stem
    log_file = script_dir / f"worked_example_{base_name}_output_{timestamp}.txt"

    logger = logging.getLogger("WorkedExample")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(message)s")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return log_file

# Global logger
logger = logging.getLogger("WorkedExample")

def log(message=""):
    """Print to both console and log file."""
    logger.info(message)

# ==============================================================================
# Result Formatting Functions
# ==============================================================================
def log_branch_results(result, indent="  "):
    """Log GeneratorBranchResults dataclass fields."""
    log(f"{indent}GeneratorBranchResults:")
    log(f"{indent}  P_g_mw:       {result.P_g_mw:>12.4f} MW")
    log(f"{indent}  Q_g_mvar:     {result.Q_g_mvar:>12.4f} Mvar")
    log(f"{indent}  V_g_kv:       {result.V_g_kv:>12.4f} kV")
    log(f"{indent}  P_branch_mw:  {result.P_branch_mw:>12.4f} MW")
    log(f"{indent}  Q_branch_mvar:{result.Q_branch_mvar:>12.4f} Mvar")
    log(f"{indent}  V_grid_kv:    {result.V_grid_kv:>12.4f} kV")

def log_loss_results(result, indent="  "):
    """Log PowerLossResult dataclass fields."""
    log(f"{indent}PowerLossResult:")
    log(f"{indent}  P_loss_stator_mw: {result.P_loss_stator_mw*1000:>10.4f} kW")
    log(f"{indent}  P_loss_rotor_mw:  {result.P_loss_rotor_mw*1000:>10.4f} kW")
    log(f"{indent}  P_loss_core_mw:   {result.P_loss_core_mw*1000:>10.4f} kW")
    log(f"{indent}  P_loss_const_mw:  {result.P_loss_const_mw*1000:>10.4f} kW")
    log(f"{indent}  trafo_loss_mw:    {result.trafo_loss_mw*1000:>10.4f} kW")
    log(f"{indent}  ────────────────────────────")
    log(f"{indent}  P_loss_gen_mw:    {result.P_loss_gen_mw*1000:>10.4f} kW (total generator)")
    log(f"{indent}  P_loss_branch_mw: {result.P_loss_branch_mw*1000:>10.4f} kW (total branch)")

def log_capability_results(result, indent="  "):
    """Log CapabilityResults dataclass fields."""
    log(f"{indent}CapabilityResults:")
    log(f"{indent}  Q_min_tot:     {result.Q_min_tot:>10.4f} Mvar (effective minimum)")
    log(f"{indent}  Q_max_tot:     {result.Q_max_tot:>10.4f} Mvar (effective maximum)")
    log(f"{indent}  ────────────────────────────")
    log(f"{indent}  Q_stator_min:  {result.Q_stator_min:>10.4f} Mvar")
    log(f"{indent}  Q_stator_max:  {result.Q_stator_max:>10.4f} Mvar")
    log(f"{indent}  Q_rotor_max:   {result.Q_rotor_max:>10.4f} Mvar")
    log(f"{indent}  Q_stab_min:    {result.Q_stab_min:>10.4f} Mvar")
    log(f"{indent}  Q_v_min:       {result.Q_v_min:>10.4f} Mvar")
    log(f"{indent}  Q_v_max:       {result.Q_v_max:>10.4f} Mvar")

def log_operating_point(op, indent="  "):
    """Log GeneratorOperatingPoint fields."""
    log(f"{indent}GeneratorOperatingPoint:")
    log(f"{indent}  P_mw:   {op.P_mw:>10.4f} MW")
    log(f"{indent}  Q_mvar: {op.Q_mvar:>10.4f} Mvar")
    log(f"{indent}  V_kv:   {op.V_kv:>10.4f} kV")

# ==============================================================================
# Main Worked Example Function
# ==============================================================================
def run_worked_example(config_path: Path, op_path: Path):
    """Run the complete worked example with given configuration files."""
    
    # Load configuration files
    gen_config = load_generator_config(config_path)
    op_config = load_operating_points(op_path)
    
    # Setup logging
    script_dir = Path(__file__).parent
    log_file = setup_logging(script_dir, config_path.name)
    
    log("=" * 80)
    log(f"WORKED EXAMPLE: {gen_config['name'].upper()} POWER LOSS ESTIMATION")
    log("=" * 80)
    log(f"Configuration: {config_path.name}")
    log(f"Operating points: {op_path.name}")
    log(f"Output: {log_file.name}")
    log()
    
    # ==========================================================================
    # Import SynGenLib Components
    # ==========================================================================
    from syngenlib.data import (
        GeneratorDataclass, 
        GeneratorLossDataclass,
        GeneratorOperatingPoint
    )
    from syngenlib.models import (
        BranchCalculationModel, 
        NonLinearSaturationModel1,
        LinearSaturationModel
    )

    # ==========================================================================
    # Section 1: Create Generator Model from Configuration
    # ==========================================================================
    log("SECTION 1: CREATE GENERATOR MODEL FROM CONFIGURATION")
    log("-" * 80)
    
    # Extract configuration
    nameplate = gen_config['nameplate_data']
    S_n = nameplate['S_n_mva']
    V_n = nameplate['V_n_kv']
    cos_phi = nameplate['cos_phi']
    
    elec_params = gen_config['electrical_parameters']
    X_d = elec_params['X_d_pu']
    X_q = elec_params['X_q_pu']
    R_a = elec_params['R_a_pu']
    
    log("Creating GeneratorDataclass...")
    gen_data = GeneratorDataclass(
        S_n_mva=S_n, 
        V_nom_kV=V_n, 
        cos_phi=cos_phi,
        X_d_u=X_d, 
        X_q_u=X_q, 
        R_a=R_a
    )
    log(f"  S_n_mva:  {gen_data.S_n_mva} MVA")
    log(f"  V_nom_kV: {gen_data.V_nom_kV} kV")
    log(f"  cos_phi:  {gen_data.cos_phi}")
    log(f"  X_d_u:    {gen_data.X_d_u} pu")
    log(f"  X_q_u:    {gen_data.X_q_u} pu")
    log(f"  R_a:      {gen_data.R_a} pu")
    log()
    
    # Loss data
    loss_cfg = gen_config['loss_components_kw']
    P_l_stator_pu = loss_cfg['stator_copper'] / (S_n * 1000)
    P_l_rotor_pu = loss_cfg['rotor_copper'] / (S_n * 1000)
    P_l_core_pu = loss_cfg['core'] / (S_n * 1000)
    P_l_const_pu = loss_cfg['mechanical'] / (S_n * 1000)
    
    log("Creating GeneratorLossDataclass...")
    pl_data = GeneratorLossDataclass(
        P_loss_nom_stator_pu=P_l_stator_pu,
        P_loss_nom_rotor_pu=P_l_rotor_pu,
        P_loss_nom_core_pu=P_l_core_pu,
        P_loss_nom_const_pu=P_l_const_pu
    )
    log(f"  P_loss_nom_stator_pu: {pl_data.P_loss_nom_stator_pu:.8f} pu ({loss_cfg['stator_copper']:.2f} kW)")
    log(f"  P_loss_nom_rotor_pu:  {pl_data.P_loss_nom_rotor_pu:.8f} pu ({loss_cfg['rotor_copper']:.2f} kW)")
    log(f"  P_loss_nom_core_pu:   {pl_data.P_loss_nom_core_pu:.8f} pu ({loss_cfg['core']:.2f} kW)")
    log(f"  P_loss_nom_const_pu:  {pl_data.P_loss_nom_const_pu:.8f} pu ({loss_cfg['mechanical']:.2f} kW)")
    log()
    
    # Saturation model
    sat_cfg = gen_config['saturation_model']
    sat_type = sat_cfg['type']
    sat_params = sat_cfg['parameters']
    
    log(f"Creating {sat_type}...")
    if sat_type == "NonLinearSaturationModel1":
        sat_model = NonLinearSaturationModel1(
            gen_data, 
            b_v=sat_params['b_v'], 
            k=sat_params['k'], 
            C_m=sat_params['C_m'], 
            n=sat_params['n'], 
            X_p=sat_params['X_p_pu']
        )
        log(f"  b_v:   {sat_params['b_v']}")
        log(f"  k:     {sat_params['k']}")
        log(f"  C_m:   {sat_params['C_m']}")
        log(f"  n:     {sat_params['n']}")
        log(f"  X_p:   {sat_params['X_p_pu']} pu")
    else:
        sat_model = LinearSaturationModel(gen_data)
        log("  Using default linear saturation model")
    log()
    
    # Create calculation model
    log("Creating BranchCalculationModel...")
    gen_model = BranchCalculationModel(
        gen_data, 
        power_loss_data=pl_data, 
        saturation_model=sat_model
    )
    log(f"  Model initialized successfully")
    log(f"  E_q_nom: {gen_model.E_q_nom:.6f} pu")
    log()

    # ==========================================================================
    # Section 2: Create Operating Points
    # ==========================================================================
    log("SECTION 2: CREATE OPERATING POINTS")
    log("-" * 80)
    
    operating_points = op_config['operating_points']
    log(f"Loading {len(operating_points)} operating points...")
    log()
    
    op_objects = []
    for op_cfg in operating_points:
        P_mw = op_cfg['P_pu'] * S_n
        Q_mvar = op_cfg['Q_pu'] * S_n
        V_kv = op_cfg.get('V_pu', 1.0) * V_n
        
        op = GeneratorOperatingPoint(P_mw=P_mw, Q_mvar=Q_mvar, V_kv=V_kv)
        op_objects.append((op_cfg['name'], op))
        
        log(f"{op_cfg['name']}:")
        log_operating_point(op)
        log()

    # ==========================================================================
    # Section 3: Call SynGenLib Functions for Each Operating Point
    # ==========================================================================
    log("=" * 80)
    log("SECTION 3: SYNGENLIB FUNCTION CALLS AND RESULTS")
    log("=" * 80)
    log()
    
    for op_name, op in op_objects:
        log(f"{'─'*80}")
        log(f"Operating Point: {op_name}")
        log(f"{'─'*80}")
        log()
        
        # --- get_branch_results ---
        log(">>> branch_results = gen_model.get_branch_results(op)")
        branch_results = gen_model.get_branch_results(op)
        log_branch_results(branch_results)
        log()
        
        # --- get_E_q ---
        log(">>> E_q = gen_model.get_E_q(op)")
        E_q = gen_model.get_E_q(op)
        log(f"  E_q: {E_q:.6f} pu")
        log()
        
        # --- get_branch_losses ---
        log(">>> loss_results = gen_model.get_branch_losses(op)")
        loss_results = gen_model.get_branch_losses(op)
        log_loss_results(loss_results)
        log()
        
        # --- get_capability_limits ---
        log(">>> capability = gen_model.get_capability_limits(op)")
        capability = gen_model.get_capability_limits(op)
        log_capability_results(capability)
        log()
        
        # Efficiency calculation
        eta = op.P_mw / (op.P_mw + loss_results.P_loss_gen_mw) * 100
        log(f"  Efficiency: η = {eta:.4f}%")
        log()

    # ==========================================================================
    # Section 4: Summary Table
    # ==========================================================================
    log("=" * 80)
    log("SECTION 4: SUMMARY TABLE")
    log("=" * 80)
    log()
    
    log(f"{'OP':<8} {'P[MW]':>8} {'Q[Mvar]':>9} {'E_q[pu]':>8} {'P_loss[kW]':>11} {'η[%]':>8} {'Q_min':>8} {'Q_max':>8}")
    log("-" * 80)
    
    for op_name, op in op_objects:
        E_q = gen_model.get_E_q(op)
        loss = gen_model.get_branch_losses(op)
        cap = gen_model.get_capability_limits(op)
        eta = op.P_mw / (op.P_mw + loss.P_loss_gen_mw) * 100
        
        log(f"{op_name:<8} {op.P_mw:>8.2f} {op.Q_mvar:>9.2f} {E_q:>8.4f} "
            f"{loss.P_loss_gen_mw*1000:>11.2f} {eta:>8.4f} {cap.Q_min_tot:>8.2f} {cap.Q_max_tot:>8.2f}")
    
    log()

    # ==========================================================================
    # Section 5: Validation (if reference data available)
    # ==========================================================================
    ref_losses_data = op_config.get('reference_losses_kw', None)
    
    if ref_losses_data:
        log("=" * 80)
        log("SECTION 5: VALIDATION AGAINST REFERENCE")
        log("=" * 80)
        log()
        
        log(f"{'OP':<8} {'Component':<12} {'SynGenLib':>12} {'Reference':>12} {'Δ[kW]':>10} {'Δ[%]':>8}")
        log("-" * 70)
        
        for op_name, op in op_objects:
            if op_name not in ref_losses_data:
                continue
            
            loss = gen_model.get_branch_losses(op)
            ref = ref_losses_data[op_name]
            
            components = [
                ("Stator", loss.P_loss_stator_mw * 1000, ref.get("stator", 0)),
                ("Rotor", loss.P_loss_rotor_mw * 1000, ref.get("rotor", 0)),
                ("Core", loss.P_loss_core_mw * 1000, ref.get("core", 0)),
                ("Const", loss.P_loss_const_mw * 1000, ref.get("const", 0)),
            ]
            
            for i, (comp, syngen, reference) in enumerate(components):
                diff = syngen - reference
                pct = diff / reference * 100 if reference > 0 else 0
                prefix = op_name if i == 0 else ""
                log(f"{prefix:<8} {comp:<12} {syngen:>12.2f} {reference:>12.2f} {diff:>10.2f} {pct:>8.2f}")
            
            total_syngen = loss.P_loss_gen_mw * 1000
            total_ref = sum(ref.values())
            diff_total = total_syngen - total_ref
            pct_total = diff_total / total_ref * 100 if total_ref > 0 else 0
            log(f"{'':<8} {'TOTAL':<12} {total_syngen:>12.2f} {total_ref:>12.2f} {diff_total:>10.2f} {pct_total:>8.2f}")
            log("-" * 70)
        
        log()

    # ==========================================================================
    # End
    # ==========================================================================
    log("=" * 80)
    log("END OF WORKED EXAMPLE")
    log("=" * 80)
    log()
    log(f"Results saved to: {log_file.name}")

# ==============================================================================
# Main Entry Point
# ==============================================================================
if __name__ == "__main__":
    args = parse_arguments()
    
    script_dir = Path(__file__).parent
    config_path = script_dir / args.config
    op_path = script_dir / args.operating_points
    
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path.name}")
        sys.exit(1)
    
    if not op_path.exists():
        print(f"Error: Operating points file not found: {op_path.name}")
        sys.exit(1)
    
    run_worked_example(config_path, op_path)
