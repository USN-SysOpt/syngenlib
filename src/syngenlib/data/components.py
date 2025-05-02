from dataclasses import dataclass
from typing import Optional
from math import sqrt, pi
from .data_types import GeneratorOperatingPoint

@dataclass
class GeneratorDataclass:
    """
    A dataclass for storing generator model parameters.

    Attributes:
        S_n_mva (float): Rated apparent power of the generator [MVA]
        V_nom_kV (float): Rated nominal voltage of the generator [kV]
        nominal_operating_point (GeneratorOperatingPoint): Nominal operating point of the generator
        X_d_u (float): Unsaturated d-axis reactance of the generator [pu]
        X_q_u (float): Unsaturated q-axis reactance of the generator [pu]
        R_a (float): Resistance at nominal operating point (e.g., 75 deg. C) [pu]
    """
    S_n_mva: float
    V_nom_kV: float
    nominal_operating_point: GeneratorOperatingPoint
    X_d_u: float
    X_q_u: float
    R_a: float


@dataclass 
class GeneratorLossDataclass: 
    """
    A dataclass for storing generator loss model parameters.

    Attributes:
        P_loss_nom_stator_pu (float): Stator power losses at nominal operating point [pu]
        P_loss_nom_rotor_pu (float): Rotor power losses at nominal operating point [pu]
        P_loss_nom_core_pu (float): Core power losses at nominal operating point [pu]
        P_loss_nom_const_pu (float): Constant power losses, e.g., friction and windage [pu]
    """
    P_loss_nom_stator_pu: float
    P_loss_nom_rotor_pu: float
    P_loss_nom_core_pu: float
    P_loss_nom_const_pu: float

    @staticmethod 
    def no_loss() -> 'GeneratorLossDataclass':
        """
        Create a GeneratorLossDataclass instance with no losses.

        Returns:
            GeneratorLossDataclass: Instance with all losses set to zero.
        """
        return GeneratorLossDataclass(0.0, 0.0, 0.0, 0.0)


@dataclass 
class CapabilityModelDataclass: 
    """
    A dataclass for storing generator capability parameters.

    Attributes: 
        P_min_pu (float): Minimum active power [pu]
        P_max_pu (float): Maximum active power [pu]
        I_a_min_pu (float): Minimum armature current [pu]
        I_a_max_pu (float): Maximum armature current [pu]
        E_q_min (float): Minimum internal voltage [pu]
        E_q_max (float): Maximum internal voltage [pu]
        V_g_min (float): Minimum generator terminal voltage [pu]
        V_g_max (float): Maximum generator terminal voltage [pu]
        rotor_angle_max_rad (float): Maximum rotor angle [rad]
    """
    P_min_pu: float 
    P_max_pu: float
    I_a_min_pu: float 
    I_a_max_pu: float 
    E_q_min: float
    E_q_max: float
    V_g_min: float
    V_g_max: float
    rotor_angle_max_rad: float

    @staticmethod
    def default_limits(nom_op: GeneratorOperatingPoint, gen_data: GeneratorDataclass) -> 'CapabilityModelDataclass':
        """
        Create a CapabilityModelDataClass instance with default limits.

        Returns:
            CapabilityModelDataClass: Instance with default limits.
        """
        V = nom_op.V_pu
        P = nom_op.P_mw / gen_data.S_n_mva
        Q = nom_op.Q_mvar / gen_data.S_n_mva
        E_q_min = 0.1 
        E_q_square = V**2 * ((1.0 + gen_data.X_d_u * Q / (V**2))**2 + (gen_data.X_d_u * P / (V**2))**2)
        E_q_max = sqrt(E_q_square)
        return CapabilityModelDataclass(0.0, 1.0, 0.0, 1.0, E_q_min, E_q_max, 0.9, 1.1, 30.0*pi/180.0)


@dataclass
class TransformerDataclass:
    """
    A dataclass for storing transformer model parameters.

    Attributes:
        S_n_mva (float): Rated apparent power of the transformer [MVA]
        V_nom_lv_kV (float): Rated nominal voltage of the LV side of the transformer [kV]
        V_nom_hv_kV (float): Rated nominal voltage of the HV side of the transformer [kV]
        V_SCH (float): Short-circuit voltage [pu]
        P_Cu (float): Copper losses during nominal operation [pu]
        I_E (float): Excitation current to shunt [pu]
        P_Fe (float): Iron losses (shunt power losses) [pu]
        tap_ratio (Optional[float]): Transformer winding ratio between primary and secondary (default: 1.0)
        Z_lv_ratio (Optional[float]): Proportion of series impedance located at the LV side (generator side) (default: 0.5)
    """

    S_n_mva: float
    V_nom_lv_kV: float
    V_nom_hv_kV: float
    V_SCH: float
    P_Cu: float
    I_E: float
    P_Fe: float
    tap_ratio: Optional[float] = 1.0
    Z_lv_ratio: Optional[float] = 0.5

    def __post_init__(self):
        """
        Perform post-initialization calculations.

        This method calculates derived attributes based on the initialized values.
        """
        self.R_T = self.P_Cu
        self.X_T = sqrt(self.V_SCH**2 - self.R_T**2)
        self.Z_T = self.R_T + 1j * self.X_T
        self.G_Fe = self.P_Fe
        self.B_mu = sqrt(self.I_E**2 - self.G_Fe**2)
        self.Y_M = self.G_Fe - 1j * self.B_mu

        self._calc_pi_parameters()
        self._calc_power_matrix()
        self.Z_lv = 1.0/self.Y_lv if abs(self.Y_lv)> 1e-6 else 1e6
        self.Z_hv = 1.0/self.Y_hv if abs(self.Y_hv)> 1e-6 else 1e6

    def _calc_pi_parameters(self):
        """
        Calculate the π-equivalent model parameters for the transformer.
        """
        if abs(self.Z_T) < 1e-9: 
            self.Y_hv = 0.0 
            self.Y_lv = 0.0 
            self.Z_12 = 0.0
            return

        Y_lv = 1 / (self.Z_T * self.Z_lv_ratio)
        Y_hv = 1 / (self.Z_T * (1.0 - self.Z_lv_ratio))

        # Account for the tap changer
        Y_hv_12 = Y_hv * self.tap_ratio
        Y_hv_1 = Y_hv * (1 - self.tap_ratio)
        Y_hv_2 = Y_hv * self.tap_ratio * (self.tap_ratio - 1)
        Y_lv_12 = Y_lv * self.tap_ratio**(-2)

        # Collect and transform from star to delta
        Y_1_star = Y_hv_12
        Y_2_star = Y_lv_12
        Y_3_star = Y_hv_2 + self.Y_M

        Y_num = Y_1_star + Y_2_star + Y_3_star
        Y_12 = Y_1_star * Y_2_star / Y_num
        Y_23 = Y_2_star * Y_3_star / Y_num
        Y_31 = Y_3_star * Y_1_star / Y_num
        self.Y_hv = Y_31 + Y_hv_1
        self.Y_lv = Y_23
        self.Z_12 = 1 / Y_12

    def _calc_power_matrix(self):
        """
        Calculate the ABCD parameters matrix used to compute the voltage and current 
        at the sending side given the receiving side values.
        """
        self.A = self.Y_hv * self.Z_12 + 1
        self.B = self.Z_12
        self.C = self.Y_lv * self.Y_hv * self.Z_12 + self.Y_lv + self.Y_hv
        self.D = self.Y_lv * self.Z_12 + 1

    def change_base(self, S_new_mva: float, V_new_kV: float, inplace: Optional[bool] = False):
        """
        Change the transformer's base units to match those of another system.

        Args:
            S_new_mva (float): New base power [MVA]
            V_new_kV (float): New base voltage [kV]
            inplace (Optional[bool]): If True, modifies the current instance. If False, returns a new transformer object.
        """
        Z_b_old = self.V_nom_lv_kV**2 / self.S_n_mva
        Z_b_new = V_new_kV**2 / S_new_mva
        Z_change = Z_b_old / Z_b_new
        Y_change = 1 / Z_change
        V_SCH_new = self.V_SCH * Z_change
        P_Cu_new = self.P_Cu * Z_change
        I_E_new = self.I_E * Y_change
        P_Fe_new = self.P_Fe * Y_change

        if inplace:
            self.V_SCH = V_SCH_new
            self.P_Cu = P_Cu_new
            self.I_E = I_E_new
            self.P_Fe = P_Fe_new
            self.__post_init__()
        else:
            return TransformerDataclass(S_new_mva, V_new_kV, V_SCH_new, P_Cu_new,
                                        I_E_new, P_Fe_new, self.tap_ratio, self.Z_lv_ratio)

    def change_tap_ratio(self, new_tap_ratio: float):
        """
        Change the tap ratio of the transformer.

        Args:
            new_tap_ratio (float): New tap ratio value.
        """
        self.tap_ratio = new_tap_ratio
        self.__post_init__()


