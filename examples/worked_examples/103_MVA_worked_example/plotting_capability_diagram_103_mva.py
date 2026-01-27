"""
Capability Diagram and Efficiency Contours for 103 MVA Hydrogenerator
======================================================================

This script plots the capability diagram with power loss contours for the 
103 MVA hydrogenerator. Generator data is loaded from the JSON configuration file.

"""

import json
from pathlib import Path
from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import time

from syngenlib import (
    GeneratorDataclass,
    TransformerDataclass,
    GeneratorLossDataclass,
    CapabilityModelDataclass,
    GeneratorOperatingPoint,
    BranchCalculationModel
)
from syngenlib.models import NonLinearSaturationModel1, LinearSaturationModel

# ==============================================================================
# Load Generator Configuration from JSON
# ==============================================================================
def load_generator_config(config_path: Path) -> dict:
    """Load generator configuration from JSON file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Resolve path to config files (same directory)
script_dir = Path(__file__).parent
config_path = script_dir / "config_103_mva_generator.json"

print(f"Loading configuration from: {config_path.name}")
gen_config = load_generator_config(config_path)

# ==============================================================================
# Create Generator Model from Configuration
# ==============================================================================
# Nameplate data
nameplate = gen_config['nameplate_data']
S_n = nameplate['S_n_mva']
V_n = nameplate['V_n_kv']
cos_phi = nameplate['cos_phi']

# Electrical parameters
elec_params = gen_config['electrical_parameters']
X_d = elec_params['X_d_pu']
X_q = elec_params['X_q_pu']
R_a = elec_params['R_a_pu']

# Create generator dataclass
gen_data = GeneratorDataclass(
    S_n_mva=S_n,
    V_nom_kV=V_n,
    cos_phi=cos_phi,
    X_d_u=X_d,
    X_q_u=X_q,
    R_a=R_a
)

print(f"Generator: {gen_config['name']}")
print(f"  S_n = {S_n} MVA, V_n = {V_n} kV, cos_phi = {cos_phi}")

# ==============================================================================
# Create Loss Dataclass
# ==============================================================================
loss_cfg = gen_config['loss_components_kw']
P_l_stator_pu = loss_cfg['stator_copper'] / (S_n * 1000)
P_l_rotor_pu = loss_cfg['rotor_copper'] / (S_n * 1000)
P_l_core_pu = loss_cfg['core'] / (S_n * 1000)
P_l_const_pu = loss_cfg['mechanical'] / (S_n * 1000)

power_loss_data = GeneratorLossDataclass(
    P_loss_nom_stator_pu=P_l_stator_pu,
    P_loss_nom_rotor_pu=P_l_rotor_pu,
    P_loss_nom_core_pu=P_l_core_pu,
    P_loss_nom_const_pu=P_l_const_pu
)

# ==============================================================================
# Create Saturation Model
# ==============================================================================
sat_cfg = gen_config['saturation_model']
sat_type = sat_cfg['type']
sat_params = sat_cfg['parameters']

if sat_type == "NonLinearSaturationModel1":
    sat_model = NonLinearSaturationModel1(
        gen_data,
        b_v=sat_params['b_v'],
        k=sat_params['k'],
        C_m=sat_params['C_m'],
        n=sat_params['n'],
        X_p=sat_params['X_p_pu']
    )
    print(f"  Saturation model: {sat_type}")
else:
    sat_model = LinearSaturationModel(gen_data)
    print("  Saturation model: LinearSaturationModel")

# ==============================================================================
# Create Transformer Dataclass
# ==============================================================================
# Step-up transformer with series reactance of 0.129 pu (on 103 MVA base)
# Assuming HV side is 132 kV (typical for this size generator)
V_hv = 132.0  # kV (assumed HV voltage)
X_trafo_pu = 0.129  # Series reactance in pu

trafo_data = TransformerDataclass(
    S_n_mva=S_n,
    V_nom_lv_kV=V_n,
    V_nom_hv_kV=V_hv,
    V_SCH=X_trafo_pu,  # Short-circuit voltage (≈ series reactance for X >> R)
    P_Cu=0.0,          # Copper losses (neglected for capability diagram)
    I_E=0.0,           # Excitation current (neglected)
    P_Fe=0.0,          # Iron losses (neglected)
    tap_ratio=1.0,
    Z_lv_ratio=0.5
)

print(f"  Transformer: X = {X_trafo_pu} pu, {V_n}/{V_hv} kV")

# ==============================================================================
# Create Capability Model
# ==============================================================================
capability_data = CapabilityModelDataclass.default_limits(gen_data)

# ==============================================================================
# Create Branch Calculation Model
# ==============================================================================
gen_model = BranchCalculationModel(
    gen_data,
    saturation_model=sat_model,
    power_loss_data=power_loss_data,
    capability_model_data=capability_data,
    trafo_data=trafo_data
)

print(f"  Model created successfully")
print()

# ==============================================================================
# Calculate Capability Limits and Power Losses
# ==============================================================================
V_g = 1.0 * gen_data.V_nom_kV
P_g_vals = np.linspace(0.0, 1 - 1e-6, 100) * gen_data.S_n_mva

Q_g_min = np.zeros_like(P_g_vals)
Q_g_max = np.zeros_like(P_g_vals)
Q_lim_stator_min = np.zeros_like(P_g_vals)
Q_lim_stator_max = np.zeros_like(P_g_vals)
Q_lim_rotor_max = np.zeros_like(P_g_vals)
Q_lim_stab_min = np.zeros_like(P_g_vals)
Q_lim_v_min = np.zeros_like(P_g_vals)
Q_lim_v_max = np.zeros_like(P_g_vals)

P_contour_plot = []
Q_contour_plot = []
p_loss_plot = []

print("Calculating capability limits and power losses...")
t1 = time.time()

for i, P_g in enumerate(P_g_vals):
    q_lim_res = gen_model.get_capability_limits(GeneratorOperatingPoint(P_g, 0.0, V_g))
    Q_min = q_lim_res.Q_min_tot
    Q_max = q_lim_res.Q_max_tot
    Q_g_vals = np.linspace(Q_min, Q_max, 100)

    Q_g_min[i] = Q_min
    Q_g_max[i] = Q_max
    Q_lim_stator_min[i] = q_lim_res.Q_stator_min
    Q_lim_stator_max[i] = q_lim_res.Q_stator_max
    Q_lim_rotor_max[i] = q_lim_res.Q_rotor_max
    Q_lim_stab_min[i] = q_lim_res.Q_stab_min
    Q_lim_v_min[i] = q_lim_res.Q_v_min
    Q_lim_v_max[i] = q_lim_res.Q_v_max

    for j, Q_g in enumerate(Q_g_vals):
        op = GeneratorOperatingPoint(P_g, Q_g, V_g)
        loss_res = gen_model.get_branch_losses(op)
        P_contour_plot.append(P_g)
        Q_contour_plot.append(Q_g)
        p_loss_plot.append(loss_res.P_loss_branch_mw)

t2 = time.time()
print(f"Elapsed time: {((t2-t1)*1000):.2f} ms for {len(P_g_vals)*100} points")

# ==============================================================================
# Plot Capability Diagram with Power Loss Contours
# ==============================================================================
plt.figure(figsize=(8, 8))

# Plot capability limits
plt.plot(Q_g_min, P_g_vals, label='Full Q-Capability', color='black', linewidth=4)
plt.plot(Q_g_max, P_g_vals, color='black', linewidth=4)
plt.plot(Q_lim_stator_min, P_g_vals, label='Stator Q-Limit', color='red')
plt.plot(Q_lim_stator_max, P_g_vals, color='red')
plt.plot(Q_lim_rotor_max, P_g_vals, label='Rotor Q-Limit', color='blue')
plt.plot(Q_lim_stab_min, P_g_vals, label='Stability Q-Limit', color='green')
plt.plot(Q_lim_v_min, P_g_vals, label='Voltage Q-Limit', color='grey', linestyle='--')
plt.plot(Q_lim_v_max, P_g_vals, color='grey', linestyle='--')
plt.fill_betweenx(P_g_vals, Q_g_min, Q_g_max, color='grey', alpha=0.2)

# Create mesh for contour plot
Q_mesh = np.linspace(min(Q_contour_plot), max(Q_contour_plot), 1000)
P_mesh = np.linspace(min(P_contour_plot), max(P_contour_plot), 1000)
Q_mesh, P_mesh = np.meshgrid(Q_mesh, P_mesh)

power_losses_mesh = griddata(
    (Q_contour_plot, P_contour_plot), 
    p_loss_plot, 
    (Q_mesh, P_mesh), 
    method="linear"
)

# Plot power loss contours
contourf = plt.contourf(Q_mesh, P_mesh, power_losses_mesh, 20, cmap='RdGy_r')
plt.colorbar(contourf, label='Power losses (MW)')
plt.contour(Q_mesh, P_mesh, power_losses_mesh, 20, colors='black', linewidths=0.5)

plt.xlabel('$Q_n$ (Mvar)')
plt.ylabel('$P_n$ (MW)')
plt.title(f'{gen_config["name"]} - Capability Diagram with Power Losses')
plt.grid(True, alpha=0.3)
plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1.03), ncol=2, frameon=True)

# Save figure
output_path = script_dir / "capability_diagram_103_mva.pdf"
plt.savefig(output_path, bbox_inches='tight', dpi=300)
print(f"Figure saved to: {output_path.name}")

plt.show()
