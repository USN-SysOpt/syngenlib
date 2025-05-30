from syngenlib import GeneratorDataclass, TransformerDataclass, LinearSaturationModel, GeneratorLossDataclass, CapabilityModelDataclass 
from syngenlib import GeneratorOperatingPoint, BranchCalculationModel
from math import sqrt

nom_op = GeneratorOperatingPoint(P_mw=30.0*0.9, Q_mvar=sqrt(1-0.9**2)*30.0, V_kv=9.5)
gen_data = GeneratorDataclass(S_n_mva=30.0, V_nom_kV=9.5, cos_phi=0.9, 
                              X_d_u=1.106711061, X_q_u=0.771661668, R_a=0.003279488)

sat_model = LinearSaturationModel(gen_data) 

trafo_data = TransformerDataclass(30.0, 9.5, 23.0, 0.1, 0.0, 0.0, 0.0, 1.0, 0.5)

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