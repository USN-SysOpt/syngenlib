from abc import ABC

class OperatingPoint(ABC): 
    """An abstract base class for storing operating points. 
    
    Attributes: 
        P_mw (float): Active power [MW]
        Q_mvar (float): Reactive power [Mvar]
        V_pu (float): Voltage magnitude [per-unit]"""

    def __init__(self, P_mw: float, Q_mvar: float, V_pu: float): 
        self.P_mw = P_mw
        self.Q_mvar = Q_mvar
        self.V_pu = V_pu

    def get_PQV_pu(self, S_base_mva: float) -> tuple[float, float, float]: 
        """Get the active power, reactive power, and voltage magnitude in per-unit.
        
        Returns: 
            Tuple[float, float, float]: 
            (P_pu, Q_pu, V_pu)
        """
        return (self.P_mw / S_base_mva, self.Q_mvar / S_base_mva, self.V_pu)
    
    def get_PQV_electrical_units(self): 
        """Get the active power and reactive power in electrical units, and the voltage in per-unit.
        
        Returns: 
            Tuple[float, float, float]: 
            (P_mw, Q_mvar, V_pu)
        """
        return (self.P_mw, self.Q_mvar, self.V_pu)
    

class GeneratorOperatingPoint(OperatingPoint): 
    def __init__(self, P_mw: float, Q_mvar: float, V_pu: float): 
        super().__init__(P_mw, Q_mvar, V_pu)


class BranchOperatingPoint(OperatingPoint):
    def __init__(self, P_mw: float, Q_mvar: float, V_pu: float): 
        super().__init__(P_mw, Q_mvar, V_pu) 


class PlantOperatingPoint: 
    """Generator active power (P_mw), generator voltage (V_g), and grid voltage (V_n). """
    def __init__(self, P_mw: float, V_g: float, V_n: float): 
        self.P_mw = P_mw
        self.V_g = V_g
        self.V_n = V_n

