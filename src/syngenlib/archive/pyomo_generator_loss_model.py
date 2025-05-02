from enum import Enum
import pyomo.environ as pyo
from ..data import GeneratorDataClass, GeneratorOperatingPoint
import numpy as np

class GenOptimizationType(Enum):
    PQV = 1
    PQ = 2
    Q = 3
    NONE = 4

def create_pyomo_gen_model(gen_data: GeneratorDataClass, model_opt_type: GenOptimizationType, op: GeneratorOperatingPoint):
    """
    TODO: Create documentation for this function. 
    TODO: If I choose to add this into the library, I must add pyomo to the requirements.
    Notes: GenOptimizationType may be moved to the data module."""
    gen_model = pyo.ConcreteModel()
    gen_model.P_g_pu = pyo.Var(within=pyo.Reals, bounds=(-10, 10))
    gen_model.Q_g_pu = pyo.Var(within=pyo.Reals, bounds=(-10, 10))
    gen_model.V_g_pu = pyo.Var(within=pyo.NonNegativeReals, bounds=(0.5, 1.5))
    gen_model.E_q_2_pu = pyo.Var(within=pyo.NonNegativeReals, bounds=(0, 10))
    gen_model.I_a_2_pu = pyo.Var(within=pyo.NonNegativeReals, bounds=(0, 10))
    gen_model.P_loss_stator_mva = pyo.Var(within=pyo.NonNegativeReals, bounds=(0, gen_data.S_n_mva))
    gen_model.P_loss_rotor_mva = pyo.Var(within=pyo.NonNegativeReals, bounds=(0, gen_data.S_n_mva))
    gen_model.P_loss_core_mva = pyo.Var(within=pyo.NonNegativeReals, bounds=(0, gen_data.S_n_mva))
    gen_model.P_loss_const_mva = pyo.Var(within=pyo.NonNegativeReals, bounds=(0, gen_data.S_n_mva))
    gen_model.P_loss_total_mva = pyo.Var(within=pyo.NonNegativeReals, bounds=(0, gen_data.S_n_mva))

    gen_model.P_s_star_pu = pyo.Param(initialize=gen_data.P_loss_nom_stator_pu)
    gen_model.P_r_star_pu = pyo.Param(initialize=gen_data.P_loss_nom_rotor_pu)
    gen_model.P_c_star_pu = pyo.Param(initialize=gen_data.P_loss_nom_core_pu)
    gen_model.P_f_pu = pyo.Param(initialize=gen_data.P_loss_nom_const_pu)
    gen_model.S_rated_mva = pyo.Param(initialize=gen_data.S_n_mva)

    gen_model.x_d = pyo.Param(initialize=gen_data.X_d_u)
    gen_model.E_q_nom = pyo.Param(initialize=gen_data.E_q_nom)
    gen_model.E_q_max = pyo.Param(initialize=gen_data.E_q_max)
    gen_model.arc_tan_delta = pyo.Param(initialize=float(np.arctan(gen_data.delta_max)))

    P_set_pu, Q_set_pu, V_g_set = op.get_PQV_pu(gen_data.S_n_mva)
    gen_model.P_g_set = pyo.Param(initialize=P_set_pu)
    gen_model.Q_g_set = pyo.Param(initialize=Q_set_pu)
    gen_model.V_g_set = pyo.Param(initialize=V_g_set)

    def I_a_2_constraint_rule(m):
        I_a_2_calc = (m.P_g_pu**2 + m.Q_g_pu**2)/m.V_g_pu**2
        return m.I_a_2_pu == I_a_2_calc

    def E_q_2_constraint_rule(m):
        E_q_2_calc = m.V_g_pu**2*((1 + m.x_d*m.Q_g_pu/m.V_g_pu**2)**2 + (m.x_d*m.P_g_pu/m.V_g_pu**2)**2)
        return m.E_q_2_pu == E_q_2_calc

    def P_g_pu_constraint(m): 
        return m.P_g_pu == m.P_g_set
    
    def Q_g_pu_constraint(m):
        return m.Q_g_pu == m.Q_g_set

    def V_g_pu_constraint(m):
        return m.V_g_pu == m.V_g_set

    def stator_constraint(m): 
        return m.P_g_pu**2 + m.Q_g_pu**2 <= m.V_g_pu**2*m.I_a_2_pu 

    def exciter_constraint(m): 
        return (m.Q_g_pu + m.V_g_pu**2/m.x_d)**2 + m.P_g_pu - (m.E_q_max*m.V_g_pu/m.x_d)**2 <= 0 

    def stab_constraint(m): 
        return m.arc_tan_delta * m.P_g_pu - m.V_g_pu**2/m.x_d - m.Q_g_pu <= 0 

    gen_model.P_stator_loss_eq = pyo.Constraint(expr=gen_model.P_loss_stator_mva == gen_model.P_s_star_pu*gen_model.I_a_2_pu*gen_model.S_rated_mva)
    gen_model.P_rotor_loss_eq = pyo.Constraint(expr=gen_model.P_loss_rotor_mva == gen_model.P_r_star_pu*gen_model.E_q_2_pu/gen_model.E_q_nom**2*gen_model.S_rated_mva)
    gen_model.P_core_loss_eq = pyo.Constraint(expr=gen_model.P_loss_core_mva == gen_model.P_c_star_pu*gen_model.V_g_pu**2*gen_model.S_rated_mva)
    gen_model.P_const_loss_eq = pyo.Constraint(expr=gen_model.P_loss_const_mva == gen_model.P_f_pu*gen_model.S_rated_mva)
    gen_model.P_total_loss_eq = pyo.Constraint(expr=gen_model.P_loss_total_mva == 
                                               gen_model.P_loss_stator_mva + 
                                               gen_model.P_loss_rotor_mva + 
                                               gen_model.P_loss_core_mva + 
                                               gen_model.P_loss_const_mva) 

    def objective_rule(m): 
            return m.P_loss_stator_mva + m.P_loss_rotor_mva + m.P_loss_core_mva + m.P_loss_const_mva

    gen_model.I_a_2_constraint = pyo.Constraint(rule=I_a_2_constraint_rule)
    gen_model.E_q_2_constraint = pyo.Constraint(rule=E_q_2_constraint_rule)
    gen_model.stator_constraint = pyo.Constraint(rule=stator_constraint)
    gen_model.exciter_constraint = pyo.Constraint(rule=exciter_constraint)
    gen_model.stab_constraint = pyo.Constraint(rule=stab_constraint)    

    # Control constraints, depending on OptimizationType
    match model_opt_type: 
        case GenOptimizationType.PQV: 
            pass # No constraints on PQV 
        case GenOptimizationType.PQ:
            gen_model.V_g_pu_constraint = pyo.Constraint(rule=V_g_pu_constraint)
        case GenOptimizationType.Q:
            gen_model.P_g_pu_constraint = pyo.Constraint(rule=P_g_pu_constraint)
            gen_model.V_g_pu_constraint = pyo.Constraint(rule=V_g_pu_constraint)
        case _: 
            gen_model.P_g_pu_constraint = pyo.Constraint(rule=P_g_pu_constraint)
            gen_model.Q_g_pu_constraint = pyo.Constraint(rule=Q_g_pu_constraint)
            gen_model.V_g_pu_constraint = pyo.Constraint(rule=V_g_pu_constraint)

    gen_model.obj = pyo.Objective(rule=objective_rule, sense=pyo.minimize)
    return gen_model