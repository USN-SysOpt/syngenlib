import unittest
from syngenlib.data import GeneratorDataclass, TransformerDataclass, CapabilityModelDataclass
from syngenlib.models import BranchCalculationModel, LinearSaturationModel
from syngenlib.data import PlantOperatingPoint, GeneratorBranchResults

"""
List of transformer properties: 
T1: 30 MVA, 9.5 - 23 kV, tap 1.0, no magnetizing branch, 
T2: 30 MVA, 9.5 - 23 kV, tap 1.0, with magnetizing branch
T3: 30 MVA, 9.5 - 23 kV, tap 0.9, with magnetizing branch,
T4: 30 MVA, 9.5 - 23 kV, tap 1.1, with magnetizing branch
T5: 50 MVA, 9.5 - 23 kV, tap 1.0, with magnetizing branch
T6: 50 MVA, 9.5 - 23 kV, tap 1.1, with magnetizing branch
T7: 30 MVA, 10.0 - 23 kV, tap 1.0, with magnetizing branch
T8: 30 MVA, 9.5 - 25 kV, tap 1.0, with magnetizing branch
T9: 30 MVA, 9.5 - 25 kV, tap 0.9, with magnetizing branch
"""

class TestGeneratorBranchResults(unittest.TestCase):
    def setUp(self):
        self.gen_data = GeneratorDataclass(S_n_mva=30.0, V_nom_kV=9.5, cos_phi=0.9, X_d_u=1.1, X_q_u=0.8, R_a=0.003)
        self.sat_model = LinearSaturationModel(self.gen_data)
        self.capability_data = CapabilityModelDataclass.default_limits(self.gen_data)

        V_g_nom = self.gen_data.V_nom_kV
        
        self.T1 = TransformerDataclass(30.0, 9.5, 23.0, 0.1, 0.01, 0.0, 0.0, 1.0, 0.5)
        self.T2 = TransformerDataclass(30.0, 9.5, 23.0, 0.1, 0.01, 0.003, 0.001, 1.0, 0.5)
        self.T3 = TransformerDataclass(30.0, 9.5, 23.0, 0.1, 0.01, 0.003, 0.001, 0.9, 0.5)
        self.T4 = TransformerDataclass(30.0, 9.5, 23.0, 0.1, 0.01, 0.003, 0.001, 1.1, 0.5)
        self.T5 = TransformerDataclass(50.0, 9.5, 23.0, 0.1, 0.01, 0.003, 0.001, 1.0, 0.5)
        self.T6 = TransformerDataclass(50.0, 9.5, 23.0, 0.1, 0.01, 0.003, 0.001, 1.1, 0.5)
        self.T7 = TransformerDataclass(30.0, 10.0, 23.0, 0.1, 0.01, 0.003, 0.001, 1.0, 0.5)
        self.T8 = TransformerDataclass(30.0, 9.5, 25.0, 0.1, 0.01, 0.003, 0.001, 1.0, 0.5)
        self.T9 = TransformerDataclass(30.0, 9.5, 25.0, 0.1, 0.01, 0.003, 0.001, 0.9, 0.5)
        
        self.op1 = PlantOperatingPoint(P_mw=25.0, V_g_kv=1.004882855*V_g_nom, V_n_kv=1.0*self.T1.V_nom_hv_kV)
        self.op2 = PlantOperatingPoint(P_mw=25.0, V_g_kv=1.004738249*V_g_nom, V_n_kv=1.0*self.T2.V_nom_hv_kV)
        self.op3 = PlantOperatingPoint(P_mw=25.0, V_g_kv=1.115930630*V_g_nom, V_n_kv=1.0*self.T3.V_nom_hv_kV)
        self.op4 = PlantOperatingPoint(P_mw=25.0, V_g_kv=0.913539313*V_g_nom, V_n_kv=1.0*self.T4.V_nom_hv_kV)
        self.op5 = PlantOperatingPoint(P_mw=25.0, V_g_kv=1.003607484*V_g_nom, V_n_kv=1.0*self.T5.V_nom_hv_kV)
        self.op6 = PlantOperatingPoint(P_mw=25.0, V_g_kv=0.912801473*V_g_nom, V_n_kv=1.0*self.T6.V_nom_hv_kV)
        self.op7 = PlantOperatingPoint(P_mw=25.0, V_g_kv=1.057619209*V_g_nom, V_n_kv=1.0*self.T7.V_nom_hv_kV)
        self.op8 = PlantOperatingPoint(P_mw=25.0, V_g_kv=0.924498765*V_g_nom, V_n_kv=0.92*self.T8.V_nom_hv_kV)
        self.op9 = PlantOperatingPoint(P_mw=25.0, V_g_kv=1.026995313*V_g_nom, V_n_kv=0.92*self.T9.V_nom_hv_kV)
        
        self.sol_1 = GeneratorBranchResults(25.0, 0.0, 24.793686423, -2.052793948, 1.004882855*V_g_nom, 1.0*self.T1.V_nom_hv_kV)
        self.sol_2 = GeneratorBranchResults(25.0, 0.0, 24.763759045, -2.136307742, 1.004738249*V_g_nom, 1.0*self.T2.V_nom_hv_kV)
        self.sol_3 = GeneratorBranchResults(25.0, 0.0, 24.795781611, -1.76737924,  1.115930630*V_g_nom, 1.0*self.T3.V_nom_hv_kV)
        self.sol_4 = GeneratorBranchResults(25.0, 0.0, 24.725730924, -2.551981580, 0.913539313*V_g_nom, 1.0*self.T4.V_nom_hv_kV)
        self.sol_5 = GeneratorBranchResults(25.0, 0.0, 24.825984243, -1.374348229, 1.003607484*V_g_nom, 1.0*self.T5.V_nom_hv_kV)
        self.sol_6 = GeneratorBranchResults(25.0, 0.0, 24.808756171, -1.607683499, 0.912801473*V_g_nom, 1.0*self.T6.V_nom_hv_kV)
        self.sol_7 = GeneratorBranchResults(25.0, 0.0, 24.763759044, -2.136307742, 1.057619209*V_g_nom, 1.0*self.T7.V_nom_hv_kV)
        self.sol_8 = GeneratorBranchResults(25.0, 0.0, 24.731010813, -2.495154196, 0.924498765*V_g_nom, 0.92*self.T8.V_nom_hv_kV)
        self.sol_9 = GeneratorBranchResults(25.0, 0.0, 24.771259162, -2.052037273, 1.026995313*V_g_nom, 0.92*self.T9.V_nom_hv_kV)
        
        self.gm_1 = BranchCalculationModel(self.gen_data, self.T1, None, self.sat_model, self.capability_data)
        self.gm_2 = BranchCalculationModel(self.gen_data, self.T2, None, self.sat_model, self.capability_data)
        self.gm_3 = BranchCalculationModel(self.gen_data, self.T3, None, self.sat_model, self.capability_data)
        self.gm_4 = BranchCalculationModel(self.gen_data, self.T4, None, self.sat_model, self.capability_data)
        self.gm_5 = BranchCalculationModel(self.gen_data, self.T5, None, self.sat_model, self.capability_data)
        self.gm_6 = BranchCalculationModel(self.gen_data, self.T6, None, self.sat_model, self.capability_data)
        self.gm_7 = BranchCalculationModel(self.gen_data, self.T7, None, self.sat_model, self.capability_data)
        self.gm_8 = BranchCalculationModel(self.gen_data, self.T8, None, self.sat_model, self.capability_data)
        self.gm_9 = BranchCalculationModel(self.gen_data, self.T9, None, self.sat_model, self.capability_data)
    
    def _assert_branch_results_equal(self, expected: GeneratorBranchResults, actual: GeneratorBranchResults, scenario_num):
        """Helper method to assert that two GeneratorBranchResults objects are equal"""
        places = 3
        self.assertAlmostEqual(expected.P_branch_mw, actual.P_branch_mw, places=places, 
                               msg=f"Scenario {scenario_num}: P_branch_mw mismatch")
        self.assertAlmostEqual(expected.Q_branch_mvar, actual.Q_branch_mvar, places=places, 
                               msg=f"Scenario {scenario_num}: Q_branch_mvar mismatch")
        self.assertAlmostEqual(expected.P_g_mw, actual.P_g_mw, places=places, 
                               msg=f"Scenario {scenario_num}: P_gen_mw mismatch")
        self.assertAlmostEqual(expected.Q_g_mvar, actual.Q_g_mvar, places=places, 
                               msg=f"Scenario {scenario_num}: Q_gen_mvar mismatch")
        self.assertAlmostEqual(expected.V_g_kv, actual.V_g_kv, places=places, 
                               msg=f"Scenario {scenario_num}: V_gen_pu mismatch")
        self.assertAlmostEqual(expected.V_grid_kv, actual.V_grid_kv, places=places, 
                               msg=f"Scenario {scenario_num}: V_grid_pu mismatch")
    
    def test_scenario_1(self):
        """Test calculation for transformer T1"""
        calculated = self.gm_1._calculate_branch_results_from_plant_op(self.op1)
        self._assert_branch_results_equal(self.sol_1, calculated, 1)
    
    def test_scenario_2(self):
        """Test calculation for transformer T2"""
        calculated = self.gm_2._calculate_branch_results_from_plant_op(self.op2)
        self._assert_branch_results_equal(self.sol_2, calculated, 2)
    
    def test_scenario_3(self):
        """Test calculation for transformer T3"""
        calculated = self.gm_3._calculate_branch_results_from_plant_op(self.op3)
        self._assert_branch_results_equal(self.sol_3, calculated, 3)
    
    def test_scenario_4(self):
        """Test calculation for transformer T4"""
        calculated = self.gm_4._calculate_branch_results_from_plant_op(self.op4)
        self._assert_branch_results_equal(self.sol_4, calculated, 4)
    
    def test_scenario_5(self):
        """Test calculation for transformer T5"""
        calculated = self.gm_5._calculate_branch_results_from_plant_op(self.op5)
        self._assert_branch_results_equal(self.sol_5, calculated, 5)
    
    def test_scenario_6(self):
        """Test calculation for transformer T6"""
        calculated = self.gm_6._calculate_branch_results_from_plant_op(self.op6)
        self._assert_branch_results_equal(self.sol_6, calculated, 6)
    
    def test_scenario_7(self):
        """Test calculation for transformer T7"""
        calculated = self.gm_7._calculate_branch_results_from_plant_op(self.op7)
        self._assert_branch_results_equal(self.sol_7, calculated, 7)
    
    def test_scenario_8(self):
        """Test calculation for transformer T8"""
        calculated = self.gm_8._calculate_branch_results_from_plant_op(self.op8)
        self._assert_branch_results_equal(self.sol_8, calculated, 8)
    
    def test_scenario_9(self):
        """Test calculation for transformer T9"""
        calculated = self.gm_9._calculate_branch_results_from_plant_op(self.op9)
        self._assert_branch_results_equal(self.sol_9, calculated, 9)
    

if __name__ == '__main__':
    unittest.main()