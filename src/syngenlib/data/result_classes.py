from .dataclasses import GeneratorOperatingPoint, TransformerOperatingPoint
from dataclasses import dataclass
from typing import Sequence

@dataclass
class GeneratorLossResult:
    """
    A dataclass for storing generator loss results and efficiency calculations.

    Attributes:
        op: (GeneratorOperatingPoint): Generator operating point
        I_f_pu (float): Field current [pu]
        E_q_pu (float): Internal generator voltage [pu]
        P_loss_stator_pu (float): Stator power losses [pu]
        P_loss_rotor_pu (float): Rotor power losses [pu]
        P_loss_core_pu (float): Core power losses [pu]
        P_loss_const_pu (float): Constant power losses (e.g., friction, windage) [pu]
    """
    op: GeneratorOperatingPoint
    I_f_pu: float
    E_q_pu: float
    P_loss_stator_mw: float
    P_loss_rotor_mw: float
    P_loss_core_mw: float
    P_loss_const_mw: float

    def __post_init__(self):
        """
        Perform post-initialization calculations.

        This method calculates the total power losses and efficiency based on the initialized values.
        """
        self.P_loss_tot_mw = self.P_loss_stator_mw + self.P_loss_rotor_mw + self.P_loss_core_mw + self.P_loss_const_mw
        P_mw, _, _ = self.op.get_PQV_electrical_units()
        self.eff = P_mw / (P_mw + self.P_loss_tot_mw)

    def get_total_losses_pu(self, S_base_mva: float) -> float:
        """
        Get the total power losses in per-unit.

        Args:
            S_base_mva (float): Base power [MVA]

        Returns:
            float: Total power losses [pu]
        """
        return self.P_loss_tot_mw/S_base_mva

    def get_total_losses_mw(self) -> float:
        """
        Get the total power losses in MW.

        Returns:
            float: Total power losses [MW]
        """
        return self.P_loss_tot_mw

    def get_component_losses_pu(self, S_base_mva: float) -> tuple[float, float, float, float, float]:
        """
        Get all generator losses in per-unit.

        Args:
            S_base_mva (float): Base power [MVA]

        Returns:
            tuple: A tuple containing five elements:
                - P_loss_tot_mw (float): Total losses in per-unit.
                - P_loss_stator_mw (float): Stator losses in per-unit.
                - P_loss_rotor_mw (float): Rotor losses in per-unit.
                - P_loss_core_mw (float): Core losses in per-unit.
                - P_loss_const_mw (float): Constant losses in per-unit.
        """
        return tuple([loss / S_base_mva for loss in self.get_component_losses_mw()])

    def get_component_losses_mw(self) -> tuple[float, float, float, float, float]:
        """
        Get all generator losses in MW.

        Returns:
            tuple: A tuple containing five elements:
                - P_loss_tot_mw (float): Total losses in MW.
                - P_loss_stator_mw (float): Stator losses in MW.
                - P_loss_rotor_mw (float): Rotor losses in MW.
                - P_loss_core_mw (float): Core losses in MW.
                - P_loss_const_mw (float): Constant losses in MW.
        """
        return (self.P_loss_tot_mw, self.P_loss_stator_mw, self.P_loss_rotor_mw, self.P_loss_core_mw, self.P_loss_const_mw)
        

@dataclass
class TransformerLossResult:
    """
    A dataclass for storing transformer loss results and efficiency calculations.

    Attributes:
        operating_point (TransformerOperatingPoint): Transformer operating point
    """
    op: TransformerOperatingPoint

    def __post_init__(self):
        """
        Perform post-initialization calculations.

        This method calculates the total power losses and efficiency based on the input and output power sequences.
        """
        self.P_loss_mw = abs(self.op.P_in_mw - self.op.P_out_mw)
        self.eff = min(self.op.P_out_mw, self.op.P_in_mw) / max(self.op.P_out_mw, self.op.P_in_mw)

    def get_losses_pu(self) -> Sequence[float]:
        """
        Get the total power losses in per-unit.

        Returns:
            Sequence[float]: Total power losses [pu]
        """
        return self.P_loss_mw / self.op.S_n_mva

    def get_losses_mw(self) -> Sequence[float]:
        """
        Get the total power losses in MW.

        Returns:
            Sequence[float]: Total power losses [MW]
        """
        return self.P_loss_mw
    

@dataclass
class CapabilityResult:
    """
    A dataclass for storing capability results of a generator operating at an operating point, including various reactive power limits and validation checks.

    Attributes:
        op: (GeneratorOperatingPoint): Generator operating point
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

    op: GeneratorOperatingPoint
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
