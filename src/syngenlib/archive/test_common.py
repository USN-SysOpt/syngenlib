# import unittest
# from syngenlib.common import *
# from copy import deepcopy 

# class TestGeneratorLossResult(unittest.TestCase):
#     def test_get_losses_pu(self):
#         # Create an instance of GeneratorLossResult with known values
#         gen_loss_result = GeneratorLossResult(
#             P_g_pu=1.0, 
#             Q_g_pu=0.5, 
#             I_f_pu=0.3, 
#             V_g_pu=1.05, 
#             P_loss_stator_pu=0.01, 
#             P_loss_rotor_pu=0.02, 
#             P_loss_core_pu=0.03, 
#             P_loss_const_pu=0.04
#         )

#         # Calculate the total losses
#         S_base = 100.0
#         expected_total_losses = 0.01 + 0.02 + 0.03 + 0.04
#         actual_total_losses = gen_loss_result.get_losses_pu()
#         expected_total_losses_mw = expected_total_losses * S_base 
#         actual_total_losses_mw = gen_loss_result.get_losses_mw(S_base) 
#         # Assert that the calculated losses match the expected losses
#         self.assertAlmostEqual(expected_total_losses, actual_total_losses, places=5)
#         self.assertAlmostEqual(expected_total_losses_mw, actual_total_losses_mw, places=5) 
    
#     def test_get_losses_mw(self): 
#         gen_loss_result = GeneratorLossResult(
#             P_g_pu=1.0, 
#             Q_g_pu=0.5, 
#             I_f_pu=0.3, 
#             V_g_pu=1.05, 
#             P_loss_stator_pu=0.01, 
#             P_loss_rotor_pu=0.02, 
#             P_loss_core_pu=0.03, 
#             P_loss_const_pu=0.04
#         )

#         # Calculate the total losses
#         S_base = 100.0
#         expected_total_losses_mw = (0.01 + 0.02 + 0.03 + 0.04) * S_base 
#         actual_total_losses_mw = gen_loss_result.get_losses_mw(S_base) 
#         self.assertAlmostEqual(expected_total_losses_mw, actual_total_losses_mw, places=5) 

# class TestGeneratorDataClass(unittest.TestCase): 
#     def base_case(self): 
#         gen = GeneratorDataClass(S_n_mva=100, V_nom_kV=11, cos_phi_nom=0.9, 
#                                  X_d_u=1.0, delta_max=0.2, P_g_min_pu=0.1, 
#                                  P_g_max_pu=0.9, P_loss_nom_stator_pu=0.1,
#                                  P_loss_nom_rotor=0.1, P_loss_nom_core_pu=0.15, 
#                                  P_loss_nom_const_pu=0.2)
#         self.assertEqual(gen.X_d_u, gen.X_q_u)
#         self.assertEqual(gen.E_q_max, gen.E_q_nom) 


# test_trafo_data = TransformerDataClass(S_n_mva=100, V_nom_kV=10, V_SCH=0.1, P_Cu=0.1,
#                                        I_E=0.05, P_Fe=0.02)

# class TestTransformerDataClass(unittest.TestCase): 
#     def test_post_init(self): 
#         R_T = test_trafo_data.P_Cu 
#         Z_T = test_trafo_data.V_SCH 
#         X_T = sqrt(Z_T**2 - R_T**2)
#         G_Fe = test_trafo_data.P_Fe 
#         B_mu = sqrt(test_trafo_data.I_E**2 - G_Fe**2)
#         Y_M = abs(G_Fe - 1j*B_mu) 

#         self.assertAlmostEqual(R_T, test_trafo_data.R_T, places=5)
#         self.assertAlmostEqual(X_T, test_trafo_data.X_T, places=5)
#         self.assertAlmostEqual(Z_T, abs(test_trafo_data.Z_T), places=5)
#         self.assertAlmostEqual(G_Fe, test_trafo_data.G_Fe, places=5)
#         self.assertAlmostEqual(B_mu, test_trafo_data.B_mu, places=5)
#         self.assertAlmostEqual(Y_M, abs(test_trafo_data.Y_M), places=5)

#     def test_change_base_inplace(self): 
#         S_new = 200 
#         V_new = 5 
#         Z_b_old = test_trafo_data.V_nom_kV**2/test_trafo_data.S_n_mva 
#         Z_b_new = V_new**2/S_new 
#         trafo_copy = deepcopy(test_trafo_data)
#         R_T = Z_b_old/Z_b_new * trafo_copy.R_T
#         X_T = Z_b_old/Z_b_new * trafo_copy.X_T
#         Z_T = Z_b_old/Z_b_new * trafo_copy.Z_T
#         G_T = Z_b_new/Z_b_old * trafo_copy.G_Fe
#         B_mu = Z_b_new/Z_b_old * trafo_copy.B_mu
#         Y_M = Z_b_new/Z_b_old * trafo_copy.Y_M
#         trafo_copy.change_base(S_new, V_new, inplace=True)

#         self.assertAlmostEqual(R_T, trafo_copy.R_T, places=5)
#         self.assertAlmostEqual(X_T, trafo_copy.X_T, places=5)
#         self.assertAlmostEqual(abs(Z_T), abs(trafo_copy.Z_T), places=5)
#         self.assertAlmostEqual(G_T, trafo_copy.G_Fe, places=5)
#         self.assertAlmostEqual(B_mu, trafo_copy.B_mu, places=5)
#         self.assertAlmostEqual(abs(Y_M), abs(trafo_copy.Y_M), places=5)

#     def test_change_base(self): 
#         S_new = 200 
#         V_new = 5 
#         Z_b_old = test_trafo_data.V_nom_kV**2/test_trafo_data.S_n_mva 
#         Z_b_new = V_new**2/S_new 
#         trafo_copy = deepcopy(test_trafo_data)
#         R_T = Z_b_old/Z_b_new * trafo_copy.R_T
#         X_T = Z_b_old/Z_b_new * trafo_copy.X_T
#         Z_T = Z_b_old/Z_b_new * trafo_copy.Z_T
#         G_T = Z_b_new/Z_b_old * trafo_copy.G_Fe
#         B_mu = Z_b_new/Z_b_old * trafo_copy.B_mu
#         Y_M = Z_b_new/Z_b_old * trafo_copy.Y_M
#         trafo_copy = test_trafo_data.change_base(S_new, V_new, inplace=False)

#         self.assertAlmostEqual(R_T, trafo_copy.R_T, places=5)
#         self.assertAlmostEqual(X_T, trafo_copy.X_T, places=5)
#         self.assertAlmostEqual(abs(Z_T), abs(trafo_copy.Z_T), places=5)
#         self.assertAlmostEqual(G_T, trafo_copy.G_Fe, places=5)
#         self.assertAlmostEqual(B_mu, trafo_copy.B_mu, places=5)
#         self.assertAlmostEqual(abs(Y_M), abs(trafo_copy.Y_M), places=5)


# if __name__ == '__main__':
#     unittest.main()
