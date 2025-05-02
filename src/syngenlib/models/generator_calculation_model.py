from ..data.data_types import GeneratorOperatingPoint, BranchOperatingPoint 
from ..data.result_classes import GeneratorBranchResults, PowerLossResult, CapabilityResults
from ..data.components import GeneratorDataclass, TransformerDataclass, GeneratorLossDataclass, CapabilityModelDataclass
from .saturation_model import SaturationBaseClass, LinearSaturationModel
from typing import Optional, Union
from math import sqrt, atan, atan2, nan, inf
import numpy as np 
from scipy.optimize import root 

class GeneratorCalculationModel: 
    def __init__(self, gen_data: GeneratorDataclass, 
                 trafo_data: Optional[TransformerDataclass]=None, 
                 power_loss_data: Optional[GeneratorLossDataclass]=None,
                 saturation_model: Optional[SaturationBaseClass] = None, 
                 capability_model_data: Optional[CapabilityModelDataclass] = None):
        self.gen_data = gen_data

        if trafo_data is None: 
            t = TransformerDataclass(gen_data.S_n_mva, gen_data.V_nom_kV, gen_data.V_nom_kV, 
                                     0.0, 0.0, 0.0, 0.0, 1.0, 0.5)
            self.trafo_data = t
        else: 
            self.trafo_data = trafo_data
        
        if power_loss_data is None or not isinstance(power_loss_data, GeneratorLossDataclass): 
            self.power_loss_data = GeneratorLossDataclass.no_loss() 
        else: 
            self.power_loss_data = power_loss_data

        if saturation_model is None:
            P_nom = gen_data.S_n_mva * 0.9 
            Q_nom = gen_data.S_n_mva * sqrt(1.0 - 0.9**2)
            op_nom = GeneratorOperatingPoint(P_nom, Q_nom, 1.0)
            self.saturation_model = LinearSaturationModel(gen_data, op_nom)
        else: 
            self.saturation_model = saturation_model 
        
        if capability_model_data is None:
            self.capability_data = CapabilityModelDataclass.default_limits() 
        else: 
            self.capability_data = capability_model_data

        self._m = atan(self.capability_data.rotor_angle_max_rad)
        self.x_tot_pu = self.trafo_data.X_T + self.gen_data.X_d_u

    def calculate_branch_results(self, operating_point: Union[GeneratorOperatingPoint, BranchOperatingPoint]) -> GeneratorBranchResults: 
        if type(operating_point) == GeneratorOperatingPoint: 
            res = self._calculate_branch_results_from_gen_op(operating_point)
        elif type(operating_point) == BranchOperatingPoint:
            res = self._calculate_branch_results_from_branch_op(operating_point) 
        else: 
            raise TypeError("operating_point must be of type GeneratorOperatingPoint or BranchOperatingPoint")
        return res
        
    def _calculate_branch_results_from_gen_op(self, op: GeneratorOperatingPoint) -> GeneratorBranchResults: 
        obj = self._get_gen_op_branch_objective(op) 
        x0 = np.zeros(6) 
        res = root(obj, x0) 
        I_2_sol = res.x[0] + 1j*res.x[1]
        I_3_sol = res.x[2] + 1j*res.x[3]
        V_n_sol = res.x[4] + 1j*res.x[5]

        P_g_pu, Q_g_pu, V_g_pu = op.get_PQV_pu(self.gen_data.S_n_mva)
        S_branch = I_3_sol.conj() * V_n_sol
        P_branch = S_branch.real
        Q_branch = S_branch.imag
        E_q_square = V_g_pu**2 * ((1.0 + self.gen_data.X_d_u * Q_g_pu / (V_g_pu**2))**2 + (self.gen_data.X_d_u * P_g_pu / (V_g_pu**2))**2)
        E_q = sqrt(E_q_square)
        I_f = self.saturation_model.get_field_current(P_g_pu, Q_g_pu, V_g_pu, self.gen_data)
        return GeneratorBranchResults(P_g_pu, Q_g_pu, P_branch, Q_branch, V_g_pu, abs(V_n_sol), E_q, I_f)

    def _get_gen_op_branch_objective(self, op: GeneratorOperatingPoint): 
        P_g_pu, Q_g_pu, V_g_pu = op.get_PQV_pu(self.gen_data.S_n_mva)
        I_a = sqrt(P_g_pu**2 + Q_g_pu**2) / V_g_pu
        phi = atan2(Q_g_pu, P_g_pu)
        I_1 = I_a * np.exp(-1j*phi)
        Z_1 = self.trafo_data.Z_12
        Z_2 = 1.0/self.trafo_data.Y_lv if abs(self.trafo_data.Y_lv) > 1e-6 else 1e6
        Z_3 = 1.0/self.trafo_data.Y_hv if abs(self.trafo_data.Y_hv) > 1e-6 else 1e6
        
        def obj_real(X_real):
            I_2 = X_real[0] + 1j*X_real[1]
            I_3 = X_real[2] + 1j*X_real[3]
            V_n = X_real[4] + 1j*X_real[5]
            
            f1 = V_g_pu - Z_2*(I_1 - I_2)
            f2 = Z_2*(I_2-I_1) + Z_1*I_2 + Z_3*(I_2 - I_3)
            f3 = V_n - Z_3*(I_2 - I_3)
            
            return np.array([
                f1.real, f1.imag,
                f2.real, f2.imag,
                f3.real, f3.imag
            ])
        
        return obj_real
    
    def _calculate_branch_results_from_branch_op(self, op: BranchOperatingPoint) -> GeneratorBranchResults: 
        P_pu, Q_pu, V_pu = op.get_PQV_pu(self.gen_data.S_n_mva)
        phi = atan2(Q_pu, P_pu)
        I_n = (sqrt(P_pu**2 + Q_pu**2) / V_pu) * np.exp(-1j*phi)
        vec = np.array([V_pu, I_n])
        M = np.array([[self.trafo_data.A, self.trafo_data.B], [self.trafo_data.C, self.trafo_data.D]]) 
        V_g_pu, I_a_pu = np.linalg.solve(M, vec)
        S_g_pu = V_g_pu * I_a_pu.conjugate()
        P_g_pu = S_g_pu.real
        Q_g_pu = S_g_pu.imag
        V_g_abs = abs(V_g_pu)
        E_q_square = V_g_abs**2 * ((1.0 + self.gen_data.X_d_u * Q_g_pu / (V_g_abs**2))**2 + (self.gen_data.X_d_u * P_g_pu / (V_g_abs**2))**2)
        E_q = sqrt(E_q_square)
        I_f = self.saturation_model.get_field_current(P_g_pu, Q_g_pu, V_g_abs, self.gen_data)
        return GeneratorBranchResults(P_g_pu, Q_g_pu, P_pu, Q_pu, V_g_pu, V_pu, E_q, I_f)
    
    def get_branch_losses(self, op: Union[GeneratorOperatingPoint, BranchOperatingPoint]) -> PowerLossResult: 
        if type(op) == GeneratorOperatingPoint: 
            res = self._calculate_branch_results_from_gen_op(op)
        elif type(op) == BranchOperatingPoint:
            res = self._calculate_branch_results_from_branch_op(op) 
        else: 
            raise TypeError("operating_point must be of type GeneratorOperatingPoint or BranchOperatingPoint")
        
        P_stator_loss_mw = self.power_loss_data.P_loss_nom_stator_pu * abs(res.I_g)**2 * self.gen_data.S_n_mva
        P_rotor_loss_mw = self.power_loss_data.P_loss_nom_rotor_pu * abs(res.I_f_pu)**2 * self.gen_data.S_n_mva
        P_core_loss_mw = self.power_loss_data.P_loss_nom_core_pu * abs(res.V_g_pu)**2 * self.gen_data.S_n_mva
        P_const_loss_mw = self.power_loss_data.P_loss_nom_const_pu * self.gen_data.S_n_mva
        trafo_loss_mw = abs(res.P_g_pu - res.P_branch_pu) * self.gen_data.S_n_mva
        return PowerLossResult(P_stator_loss_mw, P_rotor_loss_mw, P_core_loss_mw, P_const_loss_mw, trafo_loss_mw)
    
    def calculate_Q_capability(self, operating_point: Union[GeneratorOperatingPoint, BranchOperatingPoint]) -> CapabilityResults: 
        """Calculates the reactive power limits based on the generator's operational constraints.
        
        Args:
            op (GeneratorOperatingPoint): The generator operating point. 
            
        Returns:
            CapabilityResults: A dataclass containing the reactive power limits and validation checks.
        """
        if type(operating_point) == GeneratorOperatingPoint: 
            res = self._calculate_branch_results_from_gen_op(operating_point)
            P = res.P_branch_pu 
            V = res.V_grid_pu 
        else: 
            P = operating_point.P_mw / self.gen_data.S_n_mva
            V = operating_point.V_pu 

        valid_P = self.capability_data.P_min_pu <= P <= self.capability_data.P_max_pu 
        Q_min_1, Q_max_1, valid_stator = self._get_stator_limits_pu(P, V) 
        Q_min_2, Q_max_2, valid_rotor = self._get_rotor_limits_pu(P, V)
        Q_min_3 = self._get_stability_limit_pu(P, V)
        Q_max_3 = inf # just for consistency with the comparisons. 
        Q_min_4, Q_max_4, valid_voltage = self._get_voltage_limits_pu(P, V)

        Q_min_vals = [Q_min_1, Q_min_2, Q_min_3, Q_min_4]
        Q_max_vals = [Q_max_1, Q_max_2, Q_max_3, Q_max_4]
        Q_min = max(Q_min_vals)
        Q_max = min(Q_max_vals)

        # The following code classifies which limiter is the most restrictive for the reactive power limits.
        limit_min = Q_min_vals.index(Q_min)
        limit_max = Q_max_vals.index(Q_max)

        cd_res = CapabilityResults(Q_min, Q_max, Q_min_1, Q_max_1, Q_min_2, Q_max_2, Q_min_3, Q_min_4, Q_max_4,
                                  valid_stator, valid_rotor, valid_P, valid_voltage, limit_min, limit_max)
        return cd_res
        
    def _get_stator_limits_pu(self, P: float, V: float) -> tuple[float, float, bool]:
        """Calculates the minimum and maximum reactive power limits based on stator current.
        
        Returns: 
            tuple: A tuple containing (Q_min_pu, Q_max_pu, valid_stator), where:
                Q_min_pu (float): Minimum reactive power limit. [pu] 
                Q_max_pu (float): Maximum reactive power limit. [pu]
                valid_stator (bool): Flag indicating the stator current limits are feasible. 
            """
        valid_stator = P**2 <= (V*self.capability_data.I_a_max_pu/self.trafo_data.tap_ratio)**2
        if valid_stator: 
            Q_max = sqrt((V*self.capability_data.I_a_max_pu/self.trafo_data.tap_ratio)**2 - P**2)
            Q_min = -Q_max
        else: 
            Q_min = nan
            Q_max = nan
        return (Q_min, Q_max, valid_stator)
    
    def _get_rotor_limits_pu(self, P: float, V: float) -> tuple[float, float]: 
        """Calculates the minimum and maximum reactive power limits based on rotor current. 
        
        Returns:
            tuple: A tuple containing (Q_min_pu, Q_max_pu, valid), where:
                Q_min_pu (float): Minimum reactive power limit. [pu]
                Q_max_pu (float): Maximum reactive power limit. [pu]
                valid (bool): Flag indicating the rotor current limits are feasible.
        """
        r_f_max = self.capability_data.E_q_max*V/(self.trafo_data.tap_ratio*self.x_tot_pu)
        r_f_min = self.capability_data.E_q_min*V/(self.trafo_data.tap_ratio*self.x_tot_pu)
        q_f = -V**2/(self.trafo_data.tap_ratio**2*self.x_tot_pu)
        below_min = P < r_f_min
        valid = P <= r_f_max
        valid_and_below_min = below_min and valid

        if valid_and_below_min: 
            Q_g_min = sqrt(r_f_min**2 - P**2) + q_f
            Q_g_max = sqrt(r_f_max**2 - P**2) + q_f
        elif valid: 
            Q_g_max = sqrt(r_f_max**2 - P**2) + q_f
            Q_g_min = nan
        else:
            Q_g_min = nan
            Q_g_max = nan
        return (Q_g_min, Q_g_max, valid)
        
    def _get_stability_limit_pu(self, P: float, V: float) -> tuple[float, float]:
        """Calculates the minimum reactive power limit based on maximum rotor angle.
        
        Returns:
            float: Minimum reactive power limit in per-unit [pu].
        """
        c = -V**2/(self.trafo_data.tap_ratio**2*self.x_tot_pu)
        Q_min = self._m * P + c
        return Q_min
    
    def _get_voltage_limits_pu(self, P: float, V: float) -> tuple[float, float, bool]:
        """Calculates the minimum and maximum reactive power limits based on voltage constraints.
        
        Returns:
            tuple: A tuple containing (Q_min_pu, Q_max_pu, valid), where:
                Q_min_pu (float): Minimum reactive power limit. [pu]
                Q_max_pu (float): Maximum reactive power limit. [pu]
                valid (bool): Flag indicating the voltage limits are feasible.
        """
        k1 = V/self.trafo_data.tap_ratio/self.trafo_data.X_T 
        k2_min = (self.capability_data.V_g_min*k1)
        k2_max = (self.capability_data.V_g_max*k1)
        valid = k2_min >= P 

        if self.trafo_data.X_T <= 0: 
            return (-inf, inf, valid)
        
        valid_voltage = self.capability_data.V_g_min <= V <= self.capability_data.V_g_max

        if valid:
            Q_min = sqrt(k2_min**2 - P**2) - k1*V/self.trafo_data.tap_ratio
            Q_max = sqrt(k2_max**2 - P**2) - k1*V/self.trafo_data.tap_ratio
        else:
            Q_min = nan
            Q_max = nan
        return (Q_min, Q_max, valid_voltage)
