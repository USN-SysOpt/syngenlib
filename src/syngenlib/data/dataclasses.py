from dataclasses import dataclass
from typing import Optional
from math import sqrt

@dataclass 
class GeneratorOperatingPoint: 
    """A dataclass for storing a generator operating point. The units of P and Q should be MW and Mvar respectively. V should be in per-unit.
    
    Attributes: 
        P (float): Active power [MW]
        Q (float): Reactive power [Mvar]
        V_pu (float): Voltage magnitude in per-unit
    """
    
    P: float 
    Q: float 
    V_pu: float

    def get_PQV_pu(self, S_base_mva: float) -> tuple[float, float, float]: 
        """Get the active power, reactive power, and voltage magnitude in per-unit.
        
        Returns: 
            Tuple[float, float, float]: 
            (P_pu, Q_pu, V_pu)
        """
        return (self.P / S_base_mva, self.Q / S_base_mva, self.V_pu)
    
    def get_PQV_electrical_units(self): 
        """Get the active power and reactive power in electrical units, and the voltage in per-unit.
        
        Returns: 
            Tuple[float, float, float]: 
            (P_mw, Q_mvar, V_pu)
        """
        return (self.P, self.Q, self.V_pu * self.V_pu)
    

@dataclass
class TransformerOperatingPoint:
    """
    A dataclass for storing a transformer operating point.

    Attributes: 
    S_n_mva (float): Rated power of the transformer [MVA]
    V_in_kV (float): Input voltage [kV]
    V_out_kV (float): Output voltage [kV]
    P_in_mw (float): Input active power [MW]
    P_out_mw (float): Output active power [MW]
    Q_in_mvar (float): Input reactive power [Mvar]
    Q_out_mvar (float): Output reactive power [Mvar]
    """
    S_n_mva: float
    V_in_kV: float
    V_out_kV: float
    P_in_mw: float
    P_out_mw: float
    Q_in_mvar: float
    Q_out_mvar: float


@dataclass
class GeneratorDataClass:
    """
    A dataclass for storing generator model parameters.

    Attributes:
        S_n_mva (float): Rated apparent power of the generator [MVA]
        V_nom_kV (float): Rated nominal voltage of the generator [kV]
        cos_phi_nom (float): Power factor at nominal operating condition [dimensionless]
        X_d_u (float): Unsaturated d-axis reactance of the generator [pu]
        delta_max (float): Rotor angle at stability limit [rad]
        P_g_min_pu (float): Minimum active power [pu]
        P_g_max_pu (float): Maximum active power [pu]
        P_loss_nom_stator_pu (float): Stator power losses at nominal operating point [pu]
        P_loss_nom_rotor_pu (float): Rotor power losses at nominal operating point [pu]
        P_loss_nom_core_pu (float): Core power losses at nominal operating point [pu]
        P_loss_nom_const_pu (float): Constant power losses, e.g., friction and windage [pu]
        X_q_u (Optional[float]): Unsaturated q-axis reactance of the generator [pu] (default: None)
        E_q_max (Optional[float]): Internal voltage related to the rotor heating limit [pu] (default: None)
        E_q_min (Optional[float]): Minimum internal voltage supported by the excitation system [pu] (default: 0.1)
        V_g_min (Optional[float]): Minimum allowed generator terminal voltage [pu] (default: 0.95)
        V_g_max (Optional[float]): Maximum allowed generator terminal voltage [pu] (default: 1.05)
        I_g_max (Optional[float]): Maximum steady-state stator current without overloading the generator [pu] (default: 1.0)
        R_a (Optional[float]): Resistance at nominal operating point (e.g., 75 deg. C) [pu] (default: 0.0)

    Note:
        All attributes with units [pu] are in per-unit system.
    """

    S_n_mva: float
    V_nom_kV: float
    cos_phi_nom: float
    X_d_u: float
    delta_max: float
    P_g_min_pu: float
    P_g_max_pu: float
    P_loss_nom_stator_pu: float
    P_loss_nom_rotor_pu: float
    P_loss_nom_core_pu: float
    P_loss_nom_const_pu: float
    X_q_u: Optional[float] = None
    E_q_max: Optional[float] = None
    E_q_min: Optional[float] = 0.1
    V_g_min: Optional[float] = 0.95
    V_g_max: Optional[float] = 1.05
    I_g_max: Optional[float] = 1.0
    R_a: Optional[float] = 0.0

    def __post_init__(self):
        """
        Perform post-initialization calculations.

        This method calculates derived attributes based on the initialized values.
        """
        P_nom = self.cos_phi_nom
        Q_nom = sqrt(1 - P_nom**2)
        V_nom = 1.0
        self.E_q_nom = V_nom * sqrt((1.0 + self.X_d_u * Q_nom / V_nom**2)**2 + (self.X_d_u * P_nom / V_nom**2)**2)
        if self.E_q_max is None:
            self.E_q_max = self.E_q_nom
        self.k_If = self.E_q_nom**(-1)
        if self.X_q_u is None:
            self.X_q_u = self.X_d_u


@dataclass
class TransformerDataClass:
    """
    A dataclass for storing transformer model parameters.

    Attributes:
        S_n_mva (float): Rated apparent power of the transformer [MVA]
        V_nom_kV (float): Rated nominal voltage of the LV side of the transformer [kV]
        V_SCH (float): Short-circuit voltage [pu]
        P_Cu (float): Copper losses during nominal operation [pu]
        I_E (float): Excitation current to shunt [pu]
        P_Fe (float): Iron losses (shunt power losses) [pu]
        tap_ratio (Optional[float]): Transformer winding ratio between primary and secondary (default: 1.0)
        Z_lv_ratio (Optional[float]): Proportion of series impedance located at the LV side (generator side) (default: 0.5)
    """

    S_n_mva: float
    V_nom_kV: float
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

    def _calc_pi_parameters(self):
        """
        Calculate the π-equivalent model parameters for the transformer.
        """
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
        Z_b_old = self.V_nom_kV**2 / self.S_n_mva
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
            return TransformerDataClass(S_new_mva, V_new_kV, V_SCH_new, P_Cu_new,
                                        I_E_new, P_Fe_new, self.tap_ratio, self.Z_lv_ratio)

    def change_tap_ratio(self, new_tap_ratio: float):
        """
        Change the tap ratio of the transformer.

        Args:
            new_tap_ratio (float): New tap ratio value.
        """
        self.tap_ratio = new_tap_ratio
        self.__post_init__()
