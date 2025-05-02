from typing import Optional, Sequence
from syngenlib.data import GeneratorDataClass, TransformerDataClass, CapabilityResult
from syngenlib.data import GeneratorOperatingPoint
from math import atan, sqrt, nan, inf

class CapabilityDiagram:
    """
    Constructs a capability diagram for a generator, optionally including a transformer.

    This class creates the generator and transformer capability diagram, which illustrates
    the operational limits of the system in terms of power (P-Q) capability. The diagram 
    shows the feasible operating region considering various constraints such as stator 
    current, rotor heating, stability, and voltage limits.

    The capability diagram can represent:
    - A standalone generator capability diagram if no transformer data is supplied.
    - A combined generator and transformer capability diagram when both data models are provided.

    Voltage references:
    - If no transformer model is supplied, the terminal voltage is the generator voltage.
    - If a transformer model is supplied, the terminal voltage refers to the upstream 
      transformer voltage.

    Attributes:
        gen_data (GeneratorDataClass): The generator data containing its electrical and 
            operational parameters.
        trafo_data (TransformerDataClass): The transformer data containing its electrical 
            parameters. If not provided, a default transformer model with negligible parameters 
            is used to represent the absence of a transformer.
        no_trafo (bool): Flag indicating whether a transformer is considered in the model.
        _m (float): Internal calculation variable representing the slope associated with 
            the rotor angle limit (`delta_max`).
        x_tot_pu (float): Total reactance of the system, considering both the generator and 
            transformer reactances.

    Args:
        gen_data (GeneratorDataClass): An instance of `GeneratorDataClass` representing 
            the generator's electrical parameters and limits.
        trafo_data (Optional[TransformerDataClass], optional): An optional instance of 
            `TransformerDataClass` representing the transformer's parameters. Defaults to None,
            which implies no transformer is considered in the capability diagram.
    """

    def __init__(self, gen_data: GeneratorDataClass, trafo_data: Optional[TransformerDataClass] = None):
        self.gen_data = gen_data    
        if trafo_data is None:
            # Default transformer data indicating the absence of an actual transformer.
            self.trafo_data = TransformerDataClass(
                S_n_mva=self.gen_data.S_n_mva, 
                V_nom_kV=self.gen_data.V_nom_kV, 
                V_SCH=1e-12, I_E=0.0, P_Cu=0.0, P_Fe=0.0
            )
            self.no_trafo = True  # Flag indicating no transformer is present
        else:
            self.trafo_data = trafo_data
            self.no_trafo = False
        
        self._m = atan(self.gen_data.delta_max)
        self.x_tot_pu = self.trafo_data.X_T + self.gen_data.X_d_u


    def get_stator_limits_pu(self, op: GeneratorOperatingPoint) -> tuple[float, float, bool]:
        """Calculates the minimum and maximum reactive power limits based on stator current.
        
        Returns: 
            tuple: A tuple containing (Q_min_pu, Q_max_pu, valid_stator), where:
                Q_min_pu (float): Minimum reactive power limit. [pu] 
                Q_max_pu (float): Maximum reactive power limit. [pu]
                valid_stator (bool): Flag indicating the stator current limits are feasible. 
            """
        P, Q, V = op.get_PQV_pu(self.gen_data.S_n_mva)
        valid_stator = P**2 <= (V*self.gen_data.I_g_max/self.trafo_data.tap_ratio)**2
        if valid_stator: 
            Q_max = sqrt((V*self.gen_data.I_g_max/self.trafo_data.tap_ratio)**2 - P**2)
            Q_min = -Q_max
        else: 
            Q_min = nan
            Q_max = nan
        return (Q_min, Q_max, valid_stator)

    def get_stator_limits_mvar(self, op: GeneratorOperatingPoint) -> tuple[float, float, bool]:
        """Calculates the minimum and maximum reactive power limits based on stator current.
        
        Returns: 
            tuple: A tuple containing (Q_min_mvar, Q_max_mvar, valid_stator), where:
                Q_min_mvar (float): Minimum reactive power limit. [Mvar] 
                Q_max_mvar (float): Maximum reactive power limit. [Mvar]
                valid_stator (bool): Flag indicating the stator current limits are feasible. 
        """
        Q_min_pu, Q_max_pu, valid_stator = self.get_stator_limits_pu(op)
        return (Q_min_pu*self.gen_data.S_n_mva, Q_max_pu*self.gen_data.S_n_mva, valid_stator)
    
    def get_rotor_limits_pu(self, op: GeneratorOperatingPoint) -> tuple[float, float]: 
        """Calculates the minimum and maximum reactive power limits based on rotor current. 
        
        Returns:
            tuple: A tuple containing (Q_min_pu, Q_max_pu, valid), where:
                Q_min_pu (float): Minimum reactive power limit. [pu]
                Q_max_pu (float): Maximum reactive power limit. [pu]
                valid (bool): Flag indicating the rotor current limits are feasible.
        """
        P, Q, V = op.get_PQV_pu(self.gen_data.S_n_mva)
        r_f_max = self.gen_data.E_q_max*V/(self.trafo_data.tap_ratio*self.x_tot_pu)
        r_f_min = self.gen_data.E_q_min*V/(self.trafo_data.tap_ratio*self.x_tot_pu)
        q_f = -V**2/(self.trafo_data.tap_ratio**2*self.x_tot_pu)
        below_min = P < r_f_min
        valid = P <= r_f_max
        valid_and_below_min = below_min and valid

        if valid_and_below_min: 
            Q_g_min = sqrt(r_f_min**2 - P**2) + q_f
            Q_g_max = sqrt(r_f_max**2 - P**2) + q_f
        elif valid: 
            Q_g_max = sqrt(r_f_max**2 - P**2) + q_f
            Q_g_min = nan
        else:
            Q_g_min = nan
            Q_g_max = nan
        return (Q_g_min, Q_g_max, valid)
    
    def get_rotor_limits_mvar(self, op: GeneratorOperatingPoint) -> tuple[float, float]: 
        """Calculates the minimum and maximum reactive power limits based on rotor current.
        
        Returns:
            tuple: A tuple containing (Q_min_mvar, Q_max_mvar, valid), where:
                Q_min_mvar (float): Minimum reactive power limit. [Mvar]
                Q_max_mvar (float): Maximum reactive power limit. [Mvar]
                valid (bool): Flag indicating the rotor current limits are feasible.
        """
        Q_min_pu, Q_max_pu, valid_rotor = self.get_rotor_limits_pu(op)
        return (Q_min_pu*self.gen_data.S_n_mva, Q_max_pu*self.gen_data.S_n_mva, valid_rotor)
    
    def get_stability_limit_pu(self, op: GeneratorOperatingPoint) -> tuple[float, float]:
        """Calculates the minimum reactive power limit based on maximum rotor angle.
        
        Returns:
            float: Minimum reactive power limit in per-unit [pu].
        """
        P, Q, V = op.get_PQV_pu(self.gen_data.S_n_mva) 
        c = -V**2/(self.trafo_data.tap_ratio**2*self.x_tot_pu)
        Q_min = self._m * P + c
        return Q_min
    
    def get_stability_limit_mvar(self, op: GeneratorOperatingPoint) -> tuple[float, float]:
        """Calculates the minimum reactive power limit based on maximum rotor angle.
        
        Returns:
            float: Minimum reactive power limit in Mvar [Mvar].
        """
        Q_min_pu = self.get_stability_limit_pu(op)
        return Q_min_pu*self.gen_data.S_n_mva

    def get_voltage_limits_pu(self, op: GeneratorOperatingPoint) -> tuple[float, float, bool]:
        """Calculates the minimum and maximum reactive power limits based on voltage constraints.
        
        Returns:
            tuple: A tuple containing (Q_min_pu, Q_max_pu, valid), where:
                Q_min_pu (float): Minimum reactive power limit. [pu]
                Q_max_pu (float): Maximum reactive power limit. [pu]
                valid (bool): Flag indicating the voltage limits are feasible.
        """
        P, Q, V = op.get_PQV_pu(self.gen_data.S_n_mva)        
        k1 = V/self.trafo_data.tap_ratio/self.trafo_data.X_T 
        k2_min = (self.gen_data.V_g_min*k1)
        k2_max = (self.gen_data.V_g_max*k1)
        valid = k2_min >= P 

        if self.trafo_data.X_T <= 0: 
            return (-inf, inf, valid)
        
        valid_voltage = self.gen_data.V_g_min <= V <= self.gen_data.V_g_max

        if valid:
            Q_min = sqrt(k2_min**2 - P**2) - k1*V/self.trafo_data.tap_ratio
            Q_max = sqrt(k2_max**2 - P**2) - k1*V/self.trafo_data.tap_ratio
        else:
            Q_min = nan
            Q_max = nan
        return (Q_min, Q_max, valid_voltage)
    
    def get_voltage_limits_mvar(self, op: GeneratorOperatingPoint) -> tuple[float, float, bool]:
        """Calculates the minimum and maximum reactive power limits based on voltage constraints.
        
        Returns:
            tuple: A tuple containing (Q_min_mvar, Q_max_mvar, valid), where:
                Q_min_mvar (float): Minimum reactive power limit. [Mvar]
                Q_max_mvar (float): Maximum reactive power limit. [Mvar]
                valid (bool): Flag indicating the voltage limits are feasible.
        """
        Q_min_pu, Q_max_pu, valid_voltage = self.get_voltage_limits_pu(op)
        return (Q_min_pu*self.gen_data.S_n_mva, Q_max_pu*self.gen_data.S_n_mva, valid_voltage)
    
    def get_generator_limits(self, op: GeneratorOperatingPoint) -> CapabilityResult: 
        """Calculates the reactive power limits based on the generator's operational constraints.
        
        Args:
            op (GeneratorOperatingPoint): The generator operating point. 
            
        Returns:
            CapabilityResult: A dataclass containing the reactive power limits and validation checks.
        """
        P, Q, V = op.get_PQV_pu(self.gen_data.S_n_mva)
        is_valid_power = self.gen_data.P_g_min_pu <= P <= self.gen_data.P_g_max_pu 
        Q_min_1, Q_max_1, valid_stator = self.get_stator_limits_pu(op) 
        Q_min_2, Q_max_2, valid_rotor = self.get_rotor_limits_pu(op)
        Q_min_3 = self.get_stability_limit_pu(op)
        Q_max_3 = inf # just for consistency with the comparisons. 
        Q_min_4, Q_max_4, valid_voltage = self.get_voltage_limits_pu(op)

        Q_min_vals = [Q_min_1, Q_min_2, Q_min_3, Q_min_4]
        Q_max_vals = [Q_max_1, Q_max_2, Q_max_3, Q_max_4]
        Q_min = max(Q_min_vals)
        Q_max = min(Q_max_vals)

        # The following code classifies which limiter is the most restrictive for the reactive power limits.
        limit_min = Q_min_vals.index(Q_min)
        limit_max = Q_max_vals.index(Q_max)

        cd_res = CapabilityResult(op, Q_min, Q_max, Q_min_1, Q_max_1, Q_min_2, Q_max_2, Q_min_3, Q_min_4, Q_max_4,
                                  valid_stator, valid_rotor, is_valid_power, valid_voltage, limit_min, limit_max)
        return cd_res
      
