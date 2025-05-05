import unittest 
from syngenlib.data import GeneratorOperatingPoint, TransformerOperatingPoint, GeneratorDataClass, TransformerDataClass
from math import sqrt

gen_test_data = GeneratorDataClass(S_n_mva=100.0, V_nom_kV=50.0, cos_phi_nom=0.9, 
                                   X_d_u=1.1, X_q_u=1.0, delta_max=0.7, P_g_min_pu=0.1, 
                                   P_g_max_pu=0.9, P_loss_nom_stator_pu=0.01, P_loss_nom_rotor_pu=0.01, 
                                   P_loss_nom_core_pu=0.01, P_loss_nom_const_pu=0.01, R_a=0.1, 
                                   E_q_max=1.2, E_q_min=0.1, V_g_min=0.9, V_g_max=1.1, I_g_max=1.0)

class TestDataClasses(unittest.TestCase):
        
    def test_GeneratorOperatingPoint(self):
        gen_op = GeneratorOperatingPoint(P=100, Q=50, V_pu=1.0)
        self.assertEqual(gen_op.get_PQV_pu(100), (1.0, 0.5, 1.0))
        self.assertEqual(gen_op.get_PQV_electrical_units(), (100, 50, 1.0))

    def test_TransformerOperatingPoint(self):
        trafo_op = TransformerOperatingPoint(S_n_mva=100, V_in_kV=110, V_out_kV=10, P_in_mw=100, P_out_mw=90, Q_in_mvar=50, Q_out_mvar=40)
        # No tests needed for now

    def test_GeneratorDataClass(self):
        P_nom = 0.9
        Q_nom = sqrt(1 - P_nom**2)
    
        E_q_nom = sqrt((1 + gen_test_data.X_d_u*Q_nom)**2 + (gen_test_data.X_d_u*P_nom)**2)
        k_If = E_q_nom**(-1)
        self.assertEqual(E_q_nom, gen_test_data.E_q_nom)
        self.assertEqual(k_If, gen_test_data.k_If)

    def test_TransformerDataClass(self):
        #TODO 
        pass 


if __name__ == "__main__":
    unittest.main()
