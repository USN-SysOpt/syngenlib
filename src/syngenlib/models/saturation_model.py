from abc import ABC, abstractmethod
from math import sqrt, atan2, cos, sin
from ..data.components import GeneratorDataclass
from ..data.result_classes import GeneratorBranchResults 

class SaturationBaseClass(ABC):
    """
    Abstract base class for saturation models.
    """

    def __init__(self, *args, **kwargs):
        pass # Initialize any common attributes or methods here

    @abstractmethod
    def get_field_current(self, branch_res: GeneratorBranchResults, E_q_pu: float) -> float:
        """ 
        Returns the per-unit field current based on the generator's active power, reactive power, and voltage."""
        return 0.0
    

class LinearSaturationModel(SaturationBaseClass): 
    """
    Linear saturation model for synchronous generators.

    This model assumes a linear relation between the internal voltage E_q and the field current I_f. 
    The calculation of the field current is I_f = k_f * E_q, where k_f is a constant. 

    Attributes:
        k_f (float): Field current constant [pu]
    """

    def __init__(self, gen_data: GeneratorDataclass): 
        super().__init__()
        P_g_pu = gen_data.cos_phi 
        Q_g_pu = sqrt(1.0 - P_g_pu**2)
        V_g_pu = 1.0 
        # I_a = (P_g_pu - 1.0j*Q_g_pu) / V_g_pu
        # self.E_q_nom = abs(V_g_pu  + (gen_data.R_a + 1j*gen_data.X_q_u)*I_a)
        E_q_square = V_g_pu**2 * ((1.0 + gen_data.X_d_u * Q_g_pu / (V_g_pu**2))**2 + (gen_data.X_d_u * P_g_pu / (V_g_pu**2))**2)
        self.E_q_nom = sqrt(E_q_square)
        self.k_If = 1.0/self.E_q_nom  

    def get_field_current(self, branch_res: GeneratorBranchResults, E_q_pu: float) -> float:
        I_f_pu = self.k_If * E_q_pu
        return I_f_pu
    

class NonLinearSaturationModel1(SaturationBaseClass): 
    """
    Non-linear saturation model for synchronous generators. Reference: The following paper with title
    "The Energy Transition’s Impact on the Accumulated Average Efficiency of Large Hydrogenerators"
    """
    def __init__(self, gen_data: GeneratorDataclass, b_v: float, k: float, C_m: float, n: int, X_p: float): 
        super().__init__()
        self.S_base = gen_data.S_n_mva 
        self.V_base = gen_data.V_nom_kV
        self.X_d = gen_data.X_d_u
        self.X_q = gen_data.X_q_u
        self.R_a = gen_data.R_a
        self.X_p = X_p
        self.b_v = b_v
        self.k = k
        self.C_m = C_m
        self.n = n

        # Calculating nominal field current: 
        P_g_pu = gen_data.cos_phi
        Q_g_pu = sqrt(1.0 - P_g_pu**2)
        V_g_pu = 1.0
        E_q_nom, E_p_nom = self._calc_internal_voltages(P_g_pu, Q_g_pu, V_g_pu)
        self.I_f_nom = (E_q_nom - E_p_nom)/self.b_v + self.k*(E_p_nom + self.C_m * E_p_nom**self.n)

    def get_field_current(self, branch_res: GeneratorBranchResults, E_q_pu: float) -> float:
        P_g_pu = branch_res.P_g_mw / self.S_base 
        Q_g_pu = branch_res.Q_g_mvar / self.S_base 
        V_g_pu = branch_res.V_g_kv / self.V_base

        E_q, E_p = self._calc_internal_voltages(P_g_pu, Q_g_pu, V_g_pu)
        I_f = (E_q - E_p)/self.b_v + self.k*(E_p + self.C_m * E_p**self.n) 
        return I_f/self.I_f_nom 
    
    def _calc_internal_voltages(self, P_g_pu, Q_g_pu, V_g_pu): 
        I_g = sqrt(P_g_pu**2 + Q_g_pu**2)/V_g_pu
        phi = atan2(Q_g_pu, P_g_pu)

        delta_e_q = atan2(self.X_q*I_g*cos(phi) - self.R_a*I_g*sin(phi), 
                          V_g_pu + self.X_q*I_g*sin(phi) + self.R_a*I_g*cos(phi))
        delta_e_p = atan2(self.X_p*I_g*cos(phi) - self.R_a*I_g*sin(phi), 
                          V_g_pu + self.X_p*I_g*sin(phi) + self.R_a*I_g*cos(phi))
        
        E_q = V_g_pu*cos(delta_e_q) + (self.R_a*I_g*cos(delta_e_q+phi)) + self.X_d*I_g*sin(delta_e_q+phi) 
        E_p = V_g_pu*cos(delta_e_p) + (self.R_a*I_g*cos(delta_e_p+phi)) + self.X_p*I_g*sin(delta_e_p+phi) 
        return E_q, E_p