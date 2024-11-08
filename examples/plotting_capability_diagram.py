from sample_generators import gen_103_mva 
from syngenlib import CapabilityDiagram, GeneratorOperatingPoint
import matplotlib.pyplot as plt 
import numpy as np

V_g = 1.0
P_g_vals_pu = np.linspace(0.0, 1.0, 100)
Q_g_min_pu = np.zeros_like(P_g_vals_pu)
Q_g_max_pu = np.zeros_like(P_g_vals_pu)

cap_diag = CapabilityDiagram(gen_103_mva) 

for i, P_g in enumerate(P_g_vals_pu):
    op = GeneratorOperatingPoint(P_g*gen_103_mva.S_n_mva, 0.0, V_g)
    cap_diag_res = cap_diag.get_generator_limits(op)
    Q_g_min_pu[i] = cap_diag_res.Q_min_tot_pu
    Q_g_max_pu[i] = cap_diag_res.Q_max_tot_pu

plt.plot(Q_g_min_pu, P_g_vals_pu, label='Q_min')
plt.plot(Q_g_max_pu, P_g_vals_pu, label='Q_max')
plt.xlabel('Q_g (pu)')
plt.ylabel('P_g (pu)')
plt.legend()
plt.grid()
plt.show()
