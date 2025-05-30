from syngenlib import GeneratorDataclass, TransformerDataclass, LinearSaturationModel, GeneratorLossDataclass, CapabilityModelDataclass 
from syngenlib import BranchCalculationModel

cos_phi = 0.86
S_rated_gen = 80.0 # MVA
V_rated_g = 9.5 # kV 

S_rated_trafo = 80.0 # MVA
V_T_lv = 9.5 # kV
V_T_hv = 23.0 # kV

gen_data = GeneratorDataclass(S_n_mva=S_rated_gen, V_nom_kV=V_rated_g, cos_phi=cos_phi, 
                              X_d_u=1.205889203, X_q_u=0.661362922, R_a=0.002773253)

sat_model = LinearSaturationModel(gen_data)

trafo_data = TransformerDataclass(S_rated_trafo, V_T_lv, V_T_hv, 0.04, 0.003, 0.003, 0.001, 1.0, 0.5)

power_loss_data = GeneratorLossDataclass(P_loss_nom_stator_pu=2.6856e-3,
                                         P_loss_nom_rotor_pu=1.86078e-3, 
                                         P_loss_nom_core_pu=2.057476e-3, 
                                         P_loss_nom_const_pu=4.01767e-3)

capability_data = CapabilityModelDataclass.default_limits(gen_data)

gen_model = BranchCalculationModel(gen_data, 
                                   saturation_model=sat_model, 
                                   power_loss_data=power_loss_data, 
                                   capability_model_data=capability_data, 
                                   trafo_data=trafo_data)
