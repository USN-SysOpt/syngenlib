from syngenlib import GeneratorDataclass, TransformerDataclass, LinearSaturationModel, GeneratorLossDataclass, CapabilityModelDataclass 
from syngenlib import GeneratorOperatingPoint, GeneratorCalculationModel
from math import sqrt

cos_phi = 0.95
S_nom = 160.0 
nom_op = GeneratorOperatingPoint(P_mw=S_nom*cos_phi, Q_mvar=sqrt(1-cos_phi**2)*S_nom, V_pu=1.0)
gen_data = GeneratorDataclass(S_n_mva=S_nom, V_nom_kV=11.0, nominal_operating_point=nom_op, 
                              X_d_u=0.8, X_q_u=0.6, R_a=0.003233)

sat_model = LinearSaturationModel(gen_data, nom_operating_point=nom_op)

trafo_data = TransformerDataclass(S_nom, 15.0, 132.0, 0.04, 0.003, 0.003, 0.001, 1.0, 0.5)

power_loss_data = GeneratorLossDataclass(P_loss_nom_stator_pu=0.0035258,
                                         P_loss_nom_rotor_pu=0.00319856,
                                         P_loss_nom_core_pu=0.003374188,
                                         P_loss_nom_const_pu=0.0054165)

capability_data = CapabilityModelDataclass.default_limits(nom_op, gen_data)

gen_model = GeneratorCalculationModel(gen_data, 
                                      saturation_model=sat_model, 
                                      power_loss_data=power_loss_data, 
                                      capability_model_data=capability_data, 
                                      trafo_data=trafo_data)
