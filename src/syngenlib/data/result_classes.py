from dataclasses import dataclass
from math import sqrt, atan2

@dataclass 
class GeneratorBranchResults: 
    P_g_pu: float 
    Q_g_pu: float
    P_branch_pu: float
    Q_branch_pu: float
    V_g_pu: float
    V_grid_pu: float
    E_q_pu: float
    I_f_pu: float

    def __post_init__(self): 
        self.I_g = sqrt(self.P_g_pu**2 + self.Q_g_pu**2)/self.V_g_pu
        self.I_branch = sqrt(self.P_branch_pu**2 + self.Q_branch_pu**2)/self.V_grid_pu
        self.phi_g = atan2(self.Q_g_pu, self.P_g_pu)
        self.phi_branch = atan2(self.Q_branch_pu, self.P_branch_pu) 


@dataclass
class PowerLossResult:
    """
    A dataclass for storing generator loss results and efficiency calculations.

    Attributes:
        P_loss_stator_pu (float): Stator power losses [pu]
        P_loss_rotor_pu (float): Rotor power losses [pu]
        P_loss_core_pu (float): Core power losses [pu]
        P_loss_const_pu (float): Constant power losses (e.g., friction, windage) [pu]
    """
    P_loss_stator_mw: float
    P_loss_rotor_mw: float
    P_loss_core_mw: float
    P_loss_const_mw: float
    trafo_loss_mw: float

    def __post_init__(self):
        """
        Perform post-initialization calculations.

        This method calculates the total power losses and efficiency based on the initialized values.
        """
        self.P_loss_branch_mw = self.P_loss_stator_mw + self.P_loss_rotor_mw + self.P_loss_core_mw + self.P_loss_const_mw + self.trafo_loss_mw
        self.P_loss_gen_mw = self.P_loss_stator_mw + self.P_loss_rotor_mw + self.P_loss_core_mw + self.P_loss_const_mw

    
@dataclass
class CapabilityResults:
    """
    A dataclass for storing capability results of a generator operating at an operating point, including various reactive power limits and validation checks.

    Attributes:
        Q_min_tot_pu (float): The effective minimum reactive power limit [pu]
        Q_max_tot_pu (float): The effective maximum reactive power limit [pu]
        Q_stator_min_pu (float): Minimum reactive power limited by stator current [pu]
        Q_stator_max_pu (float): Maximum reactive power limited by stator current [pu]
        Q_rotor_min_pu (float): Minimum reactive power limited by rotor current [pu]
        Q_rotor_max_pu (float): Maximum reactive power limited by rotor current [pu]
        Q_stab_min_pu (float): Minimum reactive power limited by stability [pu]
        Q_v_min_pu (float): Minimum reactive power limited by voltage constraints [pu]
        Q_v_max_pu (float): Maximum reactive power limited by voltage constraints [pu]
        valid_stator_current (bool): Validation of stator current limits
        valid_rotor_current (bool): Validation of rotor current limits
        valid_active_power (bool): Validation of active power limits
        valid_voltage_level (bool): Validation of voltage level constraints
        limiter_Q_min (int): Identifies the limiting factor for minimum reactive power:
            0 - Stator limit, 1 - Rotor limit, 2 - Stability limit, 3 - Voltage limit
        limiter_Q_max (int): Identifies the limiting factor for maximum reactive power:
            0 - Stator limit, 1 - Rotor limit, 2 - Stability limit, 3 - Voltage limit
    """

    Q_min_tot_pu: float
    Q_max_tot_pu: float
    Q_stator_min_pu: float
    Q_stator_max_pu: float
    Q_rotor_min_pu: float
    Q_rotor_max_pu: float
    Q_stab_min_pu: float
    Q_v_min_pu: float
    Q_v_max_pu: float
    valid_stator_current: bool
    valid_rotor_current: bool
    valid_active_power: bool
    valid_voltage_level: bool
    limiter_Q_min: int
    limiter_Q_max: int
