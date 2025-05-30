import unittest
from syngenlib.data import GeneratorDataclass, GeneratorLossDataclass, PowerLossResult
from syngenlib.models import BranchCalculationModel, LinearSaturationModel, NonLinearSaturationModel1
from syngenlib.data import GeneratorOperatingPoint, GeneratorBranchResults
import numpy as np 


"""Generator data from 103 MVA generator in the paper:
Loss Modeling of Large Hydrogenerators for Cost Estimation of Reactive Power Services and Identification of Optimal Operation 
"""



gen_data = GeneratorDataclass(S_n_mva=103.0, V_nom_kV=11.0, cos_phi=0.9, 
                              X_d_u=1.059, X_q_u=0.676, R_a=0.00182) 

P_l_stator_nom = (187.46 + 89.16) / 103000 # Stator losses in pu
P_l_rotor_nom = (175.78 + 15.88) / 103000 # Rotor losses in pu 
P_l_core_nom = 211.92 / 103000 # Core losses in pu
P_l_const_nom = (240.9 + 172.92) / 103000 # Constant losses in pu


pl_data = GeneratorLossDataclass(P_loss_nom_stator_pu=P_l_stator_nom, 
                                 P_loss_nom_rotor_pu=P_l_rotor_nom, 
                                 P_loss_nom_core_pu=P_l_core_nom, 
                                 P_loss_nom_const_pu=P_l_const_nom)

# sat_model = LinearSaturationModel(gen_data)
sat_model = NonLinearSaturationModel1(gen_data, b_v=1.0, k=1.0308, C_m=0.16, n=7, X_p=0.141)

gen_model = BranchCalculationModel(gen_data, power_loss_data=pl_data, saturation_model=sat_model)  

Q_from_P_cos_phi = lambda P_mw, cos_phi: P_mw * np.tan(np.arccos(cos_phi))

op1 = GeneratorOperatingPoint(P_mw=0.9*103, Q_mvar=Q_from_P_cos_phi(0.9*103, 0.9), V_kv=1.0 * gen_data.V_nom_kV)
op2 = GeneratorOperatingPoint(P_mw=0.675*103, Q_mvar=Q_from_P_cos_phi(0.675*103, 0.9), V_kv=1.0 * gen_data.V_nom_kV)
op3 = GeneratorOperatingPoint(P_mw=0.45*103, Q_mvar=Q_from_P_cos_phi(0.45*103, 0.9), V_kv=1.0 * gen_data.V_nom_kV)
op4 = GeneratorOperatingPoint(P_mw=0.225*103, Q_mvar=Q_from_P_cos_phi(0.225*103, 0.9), V_kv=1.0 * gen_data.V_nom_kV)
op5 = GeneratorOperatingPoint(P_mw=1.0*103, Q_mvar=0.0, V_kv=1.0 * gen_data.V_nom_kV)
op6 = GeneratorOperatingPoint(P_mw=0.75*103, Q_mvar=0.0, V_kv=1.0 * gen_data.V_nom_kV)
op7 = GeneratorOperatingPoint(P_mw=0.5*103, Q_mvar=0.0, V_kv=1.0 * gen_data.V_nom_kV)
op8 = GeneratorOperatingPoint(P_mw=0.25*103, Q_mvar=0.0, V_kv=1.0 * gen_data.V_nom_kV)

res_1 = gen_model.get_branch_losses(op1)
res_2 = gen_model.get_branch_losses(op2)
res_3 = gen_model.get_branch_losses(op3)
res_4 = gen_model.get_branch_losses(op4)
res_5 = gen_model.get_branch_losses(op5)
res_6 = gen_model.get_branch_losses(op6)
res_7 = gen_model.get_branch_losses(op7)
res_8 = gen_model.get_branch_losses(op8)

res_1_from_paper = PowerLossResult(P_loss_stator_mw=(89.16+187.46)/1000,
                                   P_loss_rotor_mw=(175.78 + 15.88)/1000, 
                                   P_loss_core_mw=211.92/1000, 
                                   P_loss_const_mw=(240.9+172.92)/1000,
                                   trafo_loss_mw=0.0)

res_2_from_paper = PowerLossResult(P_loss_stator_mw=(105.45+50.15)/1000,
                                   P_loss_rotor_mw=(133.66+13.02+1.87)/1000, 
                                   P_loss_core_mw=211.92/1000, 
                                   P_loss_const_mw=(240.9+172.92)/1000,
                                   trafo_loss_mw=0.0)

res_3_from_paper = PowerLossResult(P_loss_stator_mw=(46.86+22.30)/1000,
                                   P_loss_rotor_mw=(101.61+10.72+1.63)/1000, 
                                   P_loss_core_mw=211.92/1000, 
                                   P_loss_const_mw=(240.9+172.92)/1000,
                                   trafo_loss_mw=0.0)

res_4_from_paper = PowerLossResult(P_loss_stator_mw=(11.72+5.57)/1000,
                                   P_loss_rotor_mw=(77.19+8.87+1.42)/1000, 
                                   P_loss_core_mw=211.92/1000, 
                                   P_loss_const_mw=(240.9+172.92)/1000,
                                   trafo_loss_mw=0.0)

res_5_from_paper = PowerLossResult(P_loss_stator_mw=(187.46+89.16)/1000,
                                   P_loss_rotor_mw=(116.29+11.65+1.75)/1000, 
                                   P_loss_core_mw=211.92/1000, 
                                   P_loss_const_mw=(240.9+172.92)/1000,
                                   trafo_loss_mw=0.0)

res_6_from_paper = PowerLossResult(P_loss_stator_mw=(105.45+50.15)/1000,
                                   P_loss_rotor_mw=(91.99+9.92+1.55)/1000, 
                                   P_loss_core_mw=211.92/1000, 
                                   P_loss_const_mw=(240.9+172.92)/1000,
                                   trafo_loss_mw=0.0)

res_7_from_paper = PowerLossResult(P_loss_stator_mw=(46.86+22.3)/1000,
                                   P_loss_rotor_mw=(74.48+8.68+1.4)/1000, 
                                   P_loss_core_mw=211.92/1000, 
                                   P_loss_const_mw=(240.9+172.92)/1000,
                                   trafo_loss_mw=0.0)

res_8_from_paper = PowerLossResult(P_loss_stator_mw=(11.72+5.57)/1000,
                                   P_loss_rotor_mw=(63.81+7.92+1.29)/1000, 
                                   P_loss_core_mw=211.92/1000, 
                                   P_loss_const_mw=(240.9+172.92)/1000,
                                   trafo_loss_mw=0.0)

def print_results(case_name: str, res: PowerLossResult, res_from_paper: PowerLossResult): 
    print(f"\nResults for {case_name}:")
    print(f"Stator Losses: {res.P_loss_stator_mw:.4f} MW, Expected: {res_from_paper.P_loss_stator_mw:.4f} MW. % diff: {100 * (res.P_loss_stator_mw - res_from_paper.P_loss_stator_mw) / res_from_paper.P_loss_stator_mw:.2f}%")
    print(f"Rotor Losses: {res.P_loss_rotor_mw:.4f} MW, Expected: {res_from_paper.P_loss_rotor_mw:.4f} MW. % diff: {100 * (res.P_loss_rotor_mw - res_from_paper.P_loss_rotor_mw) / res_from_paper.P_loss_rotor_mw:.2f}%")
    print(f"Core Losses: {res.P_loss_core_mw:.4f} MW, Expected: {res_from_paper.P_loss_core_mw:.4f} MW.")
    print(f"Constant Losses: {res.P_loss_const_mw:.4f} MW, Expected: {res_from_paper.P_loss_const_mw:.4f} MW.") 

print_results("Operating point #1", res_1, res_1_from_paper)
print_results("Operating point #2", res_2, res_2_from_paper)
print_results("Operating point #3", res_3, res_3_from_paper)
print_results("Operating point #4", res_4, res_4_from_paper)
print_results("Operating point #5", res_5, res_5_from_paper)
print_results("Operating point #6", res_6, res_6_from_paper)
print_results("Operating point #7", res_7, res_7_from_paper)
print_results("Operating point #8", res_8, res_8_from_paper)
