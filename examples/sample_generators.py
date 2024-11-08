from syngenlib.data import GeneratorDataClass 
from math import pi

gen_30_mva = GeneratorDataClass(S_n_mva=30, V_nom_kV=9.5, cos_phi_nom=0.8, 
                                X_d_u=1.106711061, X_q_u=0.771661668, R_a=0.003279488, 
                                delta_max=30*pi/180, P_g_min_pu=0.1, P_g_max_pu=0.83333, 
                                V_g_min=0.95, V_g_max=1.05,
                                P_loss_nom_stator_pu=2.6856e-3,
                                P_loss_nom_rotor_pu=1.86078e-3, 
                                P_loss_nom_core_pu=2.057476e-3, 
                                P_loss_nom_const_pu=4.01767e-3) 

gen_60_mva = GeneratorDataClass(S_n_mva=60, V_nom_kV=9.5, cos_phi_nom=0.86, 
                                X_d_u=1.205889203, X_q_u=0.661362922, R_a=0.002773253, 
                                delta_max=30*pi/180, P_g_min_pu=0.1, P_g_max_pu=0.9166667, 
                                V_g_min=0.95, V_g_max=1.05,
                                P_loss_nom_stator_pu=2.6856e-3,
                                P_loss_nom_rotor_pu=1.86078e-3, 
                                P_loss_nom_core_pu=2.057476e-3, 
                                P_loss_nom_const_pu=4.01767e-3) 

gen_80_mva = GeneratorDataClass(S_n_mva=80, V_nom_kV=9.5, cos_phi_nom=0.86, 
                                X_d_u=1.205889203, X_q_u=0.661362922, R_a=0.002773253, 
                                delta_max=30*pi/180, P_g_min_pu=0.1, P_g_max_pu=0.9166667, 
                                V_g_min=0.95, V_g_max=1.05,
                                P_loss_nom_stator_pu=2.6856e-3,
                                P_loss_nom_rotor_pu=1.86078e-3, 
                                P_loss_nom_core_pu=2.057476e-3, 
                                P_loss_nom_const_pu=4.01767e-3) 

gen_103_mva = GeneratorDataClass(S_n_mva=103, V_nom_kV=11, cos_phi_nom=0.9, 
                                 X_d_u=1.087, X_q_u=0.676, R_a=0.00182, delta_max=30*pi/180, 
                                 P_g_min_pu=0.1, P_g_max_pu=1.0, V_g_min=0.95, V_g_max=1.05,
                                 P_loss_nom_stator_pu=2.6856e-3,
                                 P_loss_nom_rotor_pu=1.86078e-3, 
                                 P_loss_nom_core_pu=2.057476e-3, 
                                 P_loss_nom_const_pu=4.01767e-3) 

gen_103_mva = GeneratorDataClass(S_n_mva=103, V_nom_kV=11, cos_phi_nom=0.9, 
                                 X_d_u=1.087, X_q_u=0.676, delta_max=30*pi/180, 
                                 P_g_min_pu=0.1, P_g_max_pu=1.0, V_g_min=0.95, V_g_max=1.05,
                                 P_loss_nom_stator_pu=(187.46+89.16)/103_000, 
                                 P_loss_nom_rotor_pu=(173.65+15.88+2.13)/103_000, 
                                 P_loss_nom_core_pu=211.92/103_000, 
                                 P_loss_nom_const_pu=(240.9+172.92)/103_000) 

gen_120_mva = GeneratorDataClass(S_n_mva=120, V_nom_kV=14.7, cos_phi_nom=0.86, 
                                 X_d_u=1.217065518, X_q_u=0.633719567, R_a=0.001874355, 
                                 delta_max=30*pi/180, P_g_min_pu=0.1, P_g_max_pu=0.9166667, 
                                 V_g_min=0.95, V_g_max=1.05,
                                 P_loss_nom_stator_pu=2.6856e-3,
                                 P_loss_nom_rotor_pu=1.86078e-3, 
                                 P_loss_nom_core_pu=2.057476e-3, 
                                 P_loss_nom_const_pu=4.01767e-3) 

gen_160_mva = GeneratorDataClass(S_n_mva=160, V_nom_kV=15.0, cos_phi_nom=0.95, 
                                 X_d_u=0.8, X_q_u=0.6, R_a=0.003233, 
                                 delta_max=30*pi/180, P_g_min_pu=0.1, P_g_max_pu=0.95, 
                                 V_g_min=0.95, V_g_max=1.05,
                                 P_loss_nom_stator_pu=0.0035258, 
                                 P_loss_nom_rotor_pu=0.00319856, 
                                 P_loss_nom_core_pu=0.003374188, 
                                 P_loss_nom_const_pu=0.0054165) 