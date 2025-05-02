import gen_model_30_mva as g_30_mva  
from syngenlib import GeneratorOperatingPoint
import matplotlib.pyplot as plt 
import numpy as np

V_g = 1.0
P_g_vals_pu = np.linspace(0.0, 1.0, 100) * g_30_mva.gen_data.S_n_mva
Q_g_min_pu = np.zeros_like(P_g_vals_pu)
Q_g_max_pu = np.zeros_like(P_g_vals_pu)

gen_model = g_30_mva.gen_model 

branch_results = gen_model.calculate_branch_results(g_30_mva.nom_op) 
q_lim_results = gen_model.calculate_Q_capability(g_30_mva.nom_op) 

for i, P_g in enumerate(P_g_vals_pu):
    op = GeneratorOperatingPoint(P_g, 0.0, V_g)
    cap_diag_res = gen_model.calculate_Q_capability(op)
    Q_g_min_pu[i] = cap_diag_res.Q_min_tot_pu
    Q_g_max_pu[i] = cap_diag_res.Q_max_tot_pu

plt.plot(Q_g_min_pu, P_g_vals_pu, label='Q_min')
plt.plot(Q_g_max_pu, P_g_vals_pu, label='Q_max')
plt.xlabel('Q_g (pu)')
plt.ylabel('P_g (pu)')
plt.legend()
plt.grid()
plt.show()
