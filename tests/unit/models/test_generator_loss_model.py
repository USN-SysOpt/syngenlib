from syngenlib import GeneratorDataClass, GeneratorLossModel, GeneratorOperatingPoint 
from math import pi, sqrt
import numpy as np 

import unittest

gen_103_mva = GeneratorDataClass(S_n_mva=103, V_nom_kV=11, cos_phi_nom=0.9, 
                                 X_d_u=1.087, X_q_u=0.676, R_a=0.00182, delta_max=30*pi/180, 
                                 P_g_min_pu=0.1, P_g_max_pu=1.0, V_g_min=0.95, V_g_max=1.05,
                                 P_loss_nom_stator_pu=2.6856e-3,
                                 P_loss_nom_rotor_pu=1.86078e-3, 
                                 P_loss_nom_core_pu=2.057476e-3, 
                                 P_loss_nom_const_pu=4.01767e-3) 
gen_model = GeneratorLossModel(gen_103_mva)

sample_data_P = np.array([0.9, 0.675, 0.45, 0.225, 1.0, 0.75, 0.5, 0.25])*103
sample_data_Q = np.array([0.436, 0.327, 0.218, 0.109, 0.0, 0.0, 0.0, 0.0])*103
sample_data_If = np.array([1065.0, 939.12, 816.18, 711.38, 873.17, 776.61, 698.70, 646.84])

P_f = np.array([173.65, 133.66, 101.61, 77.19, 116.29, 91.99, 74.48, 63.81])  # kW
P_ex = np.array([15.88, 13.02, 10.72, 8.87, 11.65, 9.92, 8.68, 7.92])        # kW
P_br = np.array([2.13, 1.87, 1.63, 1.42, 1.75, 1.55, 1.40, 1.29])             # kW
P_a = np.array([187.46, 105.45, 46.86, 11.72, 187.46, 105.45, 46.86, 11.72])  # kW
P_s = np.array([89.16, 50.15, 22.30, 5.57, 89.16, 50.15, 22.30, 5.57])        # kW
P_c = np.array([211.92, 211.92, 211.92, 211.92, 211.92, 211.92, 211.92, 211.92]) # kW
P_be = np.array([240.90, 240.90, 240.90, 240.90, 240.90, 240.90, 240.90, 240.90]) # kW
P_wf = np.array([172.92, 172.92, 172.92, 172.92, 172.92, 172.92, 172.92, 172.92]) # kW

P_L_s = P_a + P_s 
P_L_r = P_ex + P_br + P_f
P_L_c = P_c 
P_L_f = P_be + P_wf 

class TestGeneratorLossModel(unittest.TestCase): 
    def test_loss_calculations(self): 
        for i, (P, Q) in enumerate(zip(sample_data_P, sample_data_Q)): 
            gen_op = GeneratorOperatingPoint(P=P, Q=Q, V_pu=1.0)
            gen_loss = gen_model.calculate_generator_power_losses(gen_op)
            P_L_tot_calc, P_L_s_calc, P_L_r_calc, P_L_c_calc, P_L_f_calc = (x*1000 for x in gen_loss.get_component_losses_mw())
            self.assertAlmostEqual(P_L_s_calc, P_L_s[i], places=0, msg="Stator losses not equal")
            self.assertAlmostEqual(P_L_r_calc, P_L_r[i], places=0, msg=f"Rotor losses not equal for P = {P/103} pu and Q = {Q/103} pu")
            self.assertAlmostEqual(P_L_c_calc, P_L_c[i], places=0, msg="Core losses not equal")
            self.assertAlmostEqual(P_L_f_calc, P_L_f[i], places=0, msg="Constant losses not equal")



if __name__ == '__main__': 
    unittest.main()
