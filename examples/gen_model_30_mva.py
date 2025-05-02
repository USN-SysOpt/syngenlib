from syngenlib import GeneratorDataclass, TransformerDataclass, LinearSaturationModel, GeneratorLossDataclass, CapabilityModelDataclass 
from syngenlib import GeneratorOperatingPoint, GeneratorCalculationModel
from math import sqrt

nom_op = GeneratorOperatingPoint(P_mw=30.0*0.9, Q_mvar=sqrt(1-0.9**2)*30.0, V_pu=1.0)
gen_data = GeneratorDataclass(S_n_mva=30.0, V_nom_kV=9.5, nominal_operating_point=nom_op, 
                              X_d_u=1.106711061, X_q_u=0.771661668, R_a=0.003279488)

sat_model = LinearSaturationModel(gen_data, nom_operating_point=nom_op)

trafo_data = TransformerDataclass(30.0, 9.5, 23.0, 0.04, 0.003, 0.003, 0.001, 1.0, 0.5)

power_loss_data = GeneratorLossDataclass(P_loss_nom_stator_pu=2.6856e-3,
                                       P_loss_nom_rotor_pu=1.86078e-3, 
                                       P_loss_nom_core_pu=2.057476e-3, 
                                       P_loss_nom_const_pu=4.01767e-3)

capability_data = CapabilityModelDataclass.default_limits(nom_op, gen_data)

gen_model = GeneratorCalculationModel(gen_data, 
                                      saturation_model=sat_model, 
                                      power_loss_data=power_loss_data, 
                                      capability_model_data=capability_data, 
                                      trafo_data=trafo_data)