from dataclasses import dataclass
from typing import Optional
from math import sqrt, pi
import numpy as np
from .data_types import GeneratorOperatingPoint

@dataclass
class GeneratorDataclass:
    """
    A dataclass for storing generator model parameters.

    Attributes:
        S_n_mva (float): Rated apparent power of the generator [MVA]
        V_nom_kV (float): Rated nominal voltage of the generator [kV]
        cos_phi (float): The inductuve power factor at nominal operating point
        X_d_u (float): Unsaturated d-axis reactance of the generator [pu]
        X_q_u (float): Unsaturated q-axis reactance of the generator [pu]
        R_a (float): Resistance at nominal operating point (e.g., 75 deg. C) [pu]
    """
    S_n_mva: float
    V_nom_kV: float
    cos_phi: float
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
    def default_limits(gen_data: GeneratorDataclass) -> 'CapabilityModelDataclass':
        """
        Create a CapabilityModelDataClass instance with default limits.

        Returns:
            CapabilityModelDataClass: Instance with default limits.
        """

        V = 1.0
        P = gen_data.cos_phi 
        Q = sqrt(1.0 - P**2)
        I_a = (P -1j*Q)/V
        E_q_min = 0.1 
        E_q_square = V**2 * ((1.0 + gen_data.X_d_u * Q / (V**2))**2 + (gen_data.X_d_u * P / (V**2))**2)
        E_q_max = sqrt(E_q_square)
        # E_q_max = abs(V  + (gen_data.R_a + 1j*gen_data.X_q_u)*I_a)
        V_g_min = 0.95 
        V_g_max = 1.05
        return CapabilityModelDataclass(0.0, 1.0, 0.0, 1.0, E_q_min, E_q_max, V_g_min, V_g_max, 30.0*pi/180.0)


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
    tap_ratio: float = 1.0
    Z_lv_ratio: float = 0.5

    def __post_init__(self):
        """
        Perform post-initialization calculations.

        This method calculates derived attributes based on the initialized values.
        """
        x_sch = sqrt(self.V_SCH**2 - self.P_Cu**2) 
        self.Z_hv = (1.0 - self.Z_lv_ratio)*(self.P_Cu + 1j*x_sch)
        self.Z_lv = self.Z_lv_ratio*(self.P_Cu + 1j*x_sch) 
        if self.I_E < 1e-7: 
            self.Y_m = 0.0
        else: 
            G_M = self.P_Fe 
            B_M = sqrt(self.I_E**2 - G_M**2)
            self.Y_m = G_M - 1j * B_M

        self.A = 1.0 + self.Y_m * self.Z_lv 
        self.B = self.Z_lv + self.Z_hv + self.Y_m * self.Z_lv * self.Z_hv 
        self.C = self.Y_m 
        self.D = 1.0 + self.Y_m * self.Z_hv

        self.M = np.array([[self.A, self.B], [self.C, self.D]]) 

        Y = 1/self.B 
        Y1 = (self.D - 1.0) / self.B 
        Y2 = (self.A - 1.0) / self.B 

        self.Y_bus = np.array([[Y + Y1, -Y], [-Y, Y + Y2]])
        self.G_bus = self.Y_bus.real
        self.B_bus = self.Y_bus.imag

    def change_tap_ratio(self, new_tap_ratio: float):
        """
        Change the tap ratio of the transformer.

        Args:
            new_tap_ratio (float): New tap ratio value.
        """
        self.tap_ratio = new_tap_ratio
        self.__post_init__()

    @staticmethod
    def default_transformer(S_n_mva: float, V_nom: float) -> 'TransformerDataclass':
        """
        Create a default transformer dataclass instance.

        Args:
            S_n_mva (float): Rated apparent power of the transformer [MVA]
            V_nom (float): Rated nominal voltage of the transformer [kV]

        Returns:
            TransformerDataclass: Instance with default transformer parameters.
        """
        return TransformerDataclass(S_n_mva, V_nom, V_nom, 1e-8, 0.0, 0.0, 0.0)




