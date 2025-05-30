from dataclasses import dataclass
from math import sqrt, atan2

@dataclass 
class GeneratorBranchResults: 
    P_g_mw: float 
    Q_g_mvar: float
    P_branch_mw: float
    Q_branch_mvar: float
    V_g_kv: float
    V_grid_kv: float


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
        Q_min_tot (float): The effective minimum reactive power limit [Mvar]
        Q_max_tot (float): The effective maximum reactive power limit [Mvar]
        Q_stator_min_pu (float): Minimum reactive power limited by stator current [Mvar]
        Q_stator_max_pu (float): Maximum reactive power limited by stator current [Mvar]
        Q_rotor_max_pu (float): Maximum reactive power limited by rotor current [Mvar]
        Q_stab_min_pu (float): Minimum reactive power limited by stability [Mvar]
        Q_v_min_pu (float): Minimum reactive power limited by voltage constraints [Mvar]
        Q_v_max_pu (float): Maximum reactive power limited by voltage constraints [Mvar]
        valid_stator_current (bool): Validation of stator current limits
        valid_rotor_current (bool): Validation of rotor current limits
        valid_active_power (bool): Validation of active power limits
        valid_voltage_level (bool): Validation of voltage level constraints
        limiter_Q_min (int): Identifies the limiting factor for minimum reactive power:
            0 - Stator limit, 1 - Rotor limit, 2 - Stability limit, 3 - Voltage limit
        limiter_Q_max (int): Identifies the limiting factor for maximum reactive power:
            0 - Stator limit, 1 - Rotor limit, 2 - Stability limit, 3 - Voltage limit
    """

    Q_min_tot: float
    Q_max_tot: float
    Q_stator_min: float
    Q_stator_max: float
    Q_rotor_max: float
    Q_stab_min: float
    Q_v_min: float
    Q_v_max: float
    valid_stator_current: bool
    valid_rotor_current: bool
    valid_active_power: bool
    valid_voltage_level: bool
    limiter_Q_min: int
    limiter_Q_max: int
