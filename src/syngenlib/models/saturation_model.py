from abc import ABC, abstractmethod
from math import sqrt, atan2, cos, sin
from ..data.components import GeneratorDataclass
from ..data.data_types import GeneratorOperatingPoint

class SaturationBaseClass(ABC):
    """
    Abstract base class for saturation models.
    """

    def __init__(self, *args, **kwargs):
        pass # Initialize any common attributes or methods here

    @abstractmethod
    def get_field_current(self, P_g_pu: float, Q_g_pu: float, V_g_pu: float, gen_data: GeneratorDataclass) -> float:
        """ 
        Returns the per-unit field current based on the generator's active power, reactive power, and voltage."""
        return NotImplementedError("This method should be overridden by subclasses")
    

class LinearSaturationModel(SaturationBaseClass): 
    """
    Linear saturation model for synchronous generators.

    This model assumes a linear relation between the internal voltage E_q and the field current I_f. 
    The calculation of the field current is I_f = k_f * E_q, where k_f is a constant. 

    Attributes:
        k_f (float): Field current constant [pu]
    """

    def __init__(self, gen_data: GeneratorDataclass, nom_operating_point: GeneratorOperatingPoint): 
        super().__init__()
        P_g_pu, Q_g_pu, V_g_pu = nom_operating_point.get_PQV_pu(gen_data.S_n_mva)
        E_q = self._get_E_q(P_g_pu, Q_g_pu, V_g_pu, gen_data)
        self.k_If = 1.0/E_q # Assumes nominal operating point has I_f = 1.0 pu. 

    def get_field_current(self, P_g_pu: float, Q_g_pu: float, V_g_pu: float, gen_data: GeneratorDataclass) -> float:
        E_q = self._get_E_q(P_g_pu, Q_g_pu, V_g_pu, gen_data)
        I_f = self.k_If * E_q
        return I_f

    def _get_E_q(self, P_g_pu: float, Q_g_pu: float, V_g_pu: float, gen_data: GeneratorDataclass) -> float:
        I_a = sqrt(P_g_pu**2 + Q_g_pu**2) / V_g_pu
        phi = atan2(Q_g_pu, P_g_pu)
        numerator = gen_data.X_q_u * I_a * cos(phi) - gen_data.R_a*I_a*sin(phi) 
        denum = V_g_pu + gen_data.R_a*I_a*cos(phi) + gen_data.X_q_u*I_a*sin(phi) 
        delta = atan2(numerator, denum) 
        E_q = V_g_pu * cos(delta) + gen_data.R_a*I_a*cos(phi + delta) + gen_data.X_d_u*I_a*sin(phi + delta)
        return E_q