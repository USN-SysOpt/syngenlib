import gen_model_30_mva as g_30_mva  
from syngenlib import GeneratorOperatingPoint, BranchOperatingPoint
import matplotlib.pyplot as plt 
import numpy as np
import time 

V = 1.0 
P_g_vals = np.linspace(0.0, 1-1e-7, 10000) * g_30_mva.gen_data.S_n_mva

Q_g_min = np.zeros_like(P_g_vals)
Q_g_max = np.zeros_like(P_g_vals)
Q_lim_stator_min = np.zeros_like(P_g_vals)
Q_lim_stator_max = np.zeros_like(P_g_vals)
Q_lim_rotor_max = np.zeros_like(P_g_vals)
Q_lim_stab_min = np.zeros_like(P_g_vals)
Q_lim_v_min = np.zeros_like(P_g_vals)
Q_lim_v_max = np.zeros_like(P_g_vals)

gen_model = g_30_mva.gen_model 

t1 = time.time()
for i, P_g in enumerate(P_g_vals):
    op = BranchOperatingPoint(P_g, 0.0, V * g_30_mva.trafo_data.V_nom_hv_kV)
    cap_diag_res = gen_model.get_capability_limits(op)
    Q_g_min[i] = cap_diag_res.Q_min_tot
    Q_g_max[i] = cap_diag_res.Q_max_tot
    Q_lim_stator_min[i] = cap_diag_res.Q_stator_min 
    Q_lim_stator_max[i] = cap_diag_res.Q_stator_max
    Q_lim_rotor_max[i] = cap_diag_res.Q_rotor_max
    Q_lim_stab_min[i] = cap_diag_res.Q_stab_min
    Q_lim_v_min[i] = cap_diag_res.Q_v_min
    Q_lim_v_max[i] = cap_diag_res.Q_v_max

t2 = time.time()
print(f'Elapsed time: {((t2-t1)*1000):.2f} ms for {len(P_g_vals)} points')

plt.plot(Q_g_min, P_g_vals, label='Full Q-Capability', color='black', linewidth=3)
plt.plot(Q_g_max, P_g_vals, color='black', linewidth=3)
plt.plot(Q_lim_stator_min, P_g_vals, label='Stator Q-Limit', color='red')
plt.plot(Q_lim_stator_max, P_g_vals, color='red')
plt.plot(Q_lim_rotor_max, P_g_vals, label='Rotor Q-Limit', color='blue')
plt.plot(Q_lim_stab_min, P_g_vals, label='Stability Q-Limit', color='green')
plt.plot(Q_lim_v_min, P_g_vals, label='Voltage Q-Limit', color='grey', linestyle='--')
plt.plot(Q_lim_v_max, P_g_vals, color='grey', linestyle='--')
plt.fill_betweenx(P_g_vals, Q_g_min, Q_g_max, color='grey', alpha=0.2)

plt.title(f'Capability Diagram of a {g_30_mva.gen_data.S_n_mva} MVA Generator')
plt.xlabel('$Q_n$ (Mvar)')
plt.ylabel('$P_n$ (MW)')
plt.legend()
plt.grid()
plt.show()
