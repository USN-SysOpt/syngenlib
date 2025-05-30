from syngenlib.data import GeneratorDataClass, GeneratorOperatingPoint, GeneratorLossResult
from math import tan, acos, sqrt


class GeneratorLossModel:
    """
    A class to model and calculate generator losses.

    This class provides methods to calculate various aspects of generator losses
    based on input parameters such as power, voltage, and currents.

    Attributes:
        md (GeneratorDataClass): Model data containing generator parameters.
        E_q_nom (float): Nominal internal voltage of the generator.
    """

    def __init__(self, model_data: GeneratorDataClass):
        self.md = model_data
        P_nom = self.md.cos_phi_nom 
        Q_nom = P_nom * tan(acos(P_nom))
        op_nom = GeneratorOperatingPoint(P_nom*model_data.S_n_mva, Q_nom*model_data.S_n_mva, 1.0)
        _, _, self.E_q_nom = self.calculate_generator_quantities(op_nom)
    
    def calculate_generator_quantities(self, op: GeneratorOperatingPoint) -> tuple[float, float]:
        """
        Calculate the stator and rotor currents based on given inputs.

        Args:
            op (GeneratorOperatingPoint): The operating point of the generator.

        Returns:
            tuple: A tuple containing (I_a, I_f, E_q), where:
                I_a (float): Stator current.
                I_f (float): Rotor current.
                E_q (float): Internal voltage of the generator.
        """
        P, Q, V = op.get_PQV_pu(self.md.S_n_mva)
        I_a = sqrt(P**2 + Q**2) / V
        E_q_square = V**2 * ((1.0 + self.md.X_d_u * Q / (V**2))**2 + (self.md.X_d_u * P / (V**2))**2)
        E_q = sqrt(E_q_square)
        I_f = E_q * self.md.k_If
        return (I_a, I_f, E_q) 

    def calculate_generator_power_losses(self, op: GeneratorOperatingPoint) -> GeneratorLossResult:
        """
        Calculate generator power losses based on the operating point.

        Args:
            op (GeneratorOperatingPoint): The operating point of the generator.
            I_a (float): Stator current.
            I_f (float): Rotor current.

        Returns:
            GeneratorLossResult: A dataclass containing the calculated power losses.
        """
        P, Q, V = op.get_PQV_pu(self.md.S_n_mva)
        I_a, I_f, E_q = self.calculate_generator_quantities(op)
        P_loss_stator = self.md.P_loss_nom_stator_pu * I_a**2 * self.md.S_n_mva
        P_loss_rotor = self.md.P_loss_nom_rotor_pu * (E_q/self.E_q_nom)**2 * self.md.S_n_mva
        P_loss_core = self.md.P_loss_nom_core_pu * V**2 * self.md.S_n_mva
        P_loss_const = self.md.P_loss_nom_const_pu*self.md.S_n_mva
        return GeneratorLossResult(op, I_f, E_q, P_loss_stator, P_loss_rotor, P_loss_core, P_loss_const)
    
    def get_P_loss_grad_pu(self, op: GeneratorOperatingPoint) -> tuple[float, float, float]:
        """
        Calculate and return the power loss gradient with respect to P_g, Q_g, and V_g.

        Args:
            op (GeneratorOperatingPoint): The operating point of the generator.

        Returns:
            tuple: A tuple containing (dP_L_dP_g, dP_L_dQ_g, dP_L_dV_g), where:
                dP_L_dP_g (float): Partial derivative of power loss with respect to P_g.
                dP_L_dQ_g (float): Partial derivative of power loss with respect to Q_g.
                dP_L_dV_g (float): Partial derivative of power loss with respect to V_g.
        """
        P_g_pu, Q_g_pu, V_g = op.get_PQV_pu(self.md.S_n_mva)
        # Stator loss gradients
        dP_s_dP_g = 2 * self.md.P_loss_nom_stator_pu * P_g_pu / V_g**2  
        dP_s_dQ_g = 2 * self.md.P_loss_nom_stator_pu * Q_g_pu / V_g**2 
        dP_s_dV_g = -(2 * self.md.P_loss_nom_stator_pu * (P_g_pu**2 + Q_g_pu**2)) / (V_g**3)

        # Rotor loss gradients
        dP_r_dP_g = (2 * self.md.P_loss_nom_rotor_pu * P_g_pu * self.md.X_d_u**2 * self.md.k_If**2) / (V_g**2)
        dP_r_dQ_g = 2 * self.md.P_loss_nom_rotor_pu * self.md.X_d_u * self.md.k_If**2 * (Q_g_pu * self.md.X_d_u / V_g**2 + 1)
        dP_r_dV_g = (2 * self.md.P_loss_nom_rotor_pu * self.md.k_If**2 * (-P_g_pu**2 * self.md.X_d_u**2 - Q_g_pu**2 * self.md.X_d_u**2 + V_g**4)) / (V_g**3)

        # Core loss gradients
        dP_c_dP_g = 0.0
        dP_c_dQ_g = 0.0
        dP_c_dV_g = 2 * self.md.P_loss_nom_core_pu * V_g 

        # Total loss gradients
        dP_L_dP_g = dP_s_dP_g + dP_r_dP_g + dP_c_dP_g 
        dP_L_dQ_g = dP_s_dQ_g + dP_r_dQ_g + dP_c_dQ_g
        dP_L_dV_g = dP_s_dV_g + dP_r_dV_g + dP_c_dV_g

        return (dP_L_dP_g, dP_L_dQ_g, dP_L_dV_g)