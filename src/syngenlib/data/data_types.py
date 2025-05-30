from abc import ABC

class OperatingPoint(ABC): 
    """An abstract base class for storing operating points. 
    
    Attributes: 
        P_mw (float): Active power [MW]
        Q_mvar (float): Reactive power [Mvar]
        V_kv (float): Voltage magnitude [kV]"""

    def __init__(self, P_mw: float, Q_mvar: float, V_kv: float): 
        self.P_mw = P_mw
        self.Q_mvar = Q_mvar
        self.V_kv = V_kv

    def get_PQV_pu(self, S_base_mva: float, V_base_kv: float) -> tuple[float, float, float]: 
        """Get the active power, reactive power, and voltage magnitude in per-unit.
        
        Returns: 
            Tuple[float, float, float]: 
            (P_pu, Q_pu, V_pu)
        """
        return (self.P_mw / S_base_mva, self.Q_mvar / S_base_mva, self.V_kv / V_base_kv)
    
    def get_PQV_electrical_units(self): 
        """Get the active power and reactive power in electrical units, and the voltage in kV.
        
        Returns: 
            Tuple[float, float, float]: 
            (P_mw, Q_mvar, V_kv)
        """
        return (self.P_mw, self.Q_mvar, self.V_kv)
    

class GeneratorOperatingPoint(OperatingPoint): 
    def __init__(self, P_mw: float, Q_mvar: float, V_kv: float): 
        super().__init__(P_mw, Q_mvar, V_kv)


class BranchOperatingPoint(OperatingPoint):
    def __init__(self, P_mw: float, Q_mvar: float, V_kv: float): 
        super().__init__(P_mw, Q_mvar, V_kv) 


class PlantOperatingPoint: 
    """Generator active power (P_mw), generator voltage (V_g), and grid voltage (V_n). """
    def __init__(self, P_mw: float, V_g_kv: float, V_n_kv: float): 
        self.P_mw = P_mw
        self.V_g_kv = V_g_kv
        self.V_n_kv = V_n_kv


