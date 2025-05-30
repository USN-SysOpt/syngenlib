from syngenlib import GeneratorDataClass, CapabilityDiagram, GeneratorOperatingPoint

import unittest
from math import sqrt 

gen_test_data = GeneratorDataClass(S_n_mva=100.0, V_nom_kV=50.0, cos_phi_nom=0.9, 
                                   X_d_u=1.1, X_q_u=1.0, delta_max=0.7, P_g_min_pu=0.1, 
                                   P_g_max_pu=0.9, P_loss_nom_stator_pu=0.01, P_loss_nom_rotor_pu=0.01, 
                                   P_loss_nom_core_pu=0.01, P_loss_nom_const_pu=0.01, R_a=0.1)

class TestCapabilityDiagramModel(unittest.TestCase):
    def test_NominalOperatingPoint(self):
        gen_op_nom = GeneratorOperatingPoint(P=90, Q=100*sqrt(1-0.9**2), V_pu=1.0)
        cap_diag = CapabilityDiagram(gen_test_data)
        lims = cap_diag.get_generator_limits(gen_op_nom) 
        self.assertAlmostEqual(lims.Q_max_tot_pu*100, 100*sqrt(1-0.9**2), 6)


if __name__ == "__main__":
    unittest.main()