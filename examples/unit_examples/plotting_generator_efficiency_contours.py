import gen_model_30_mva as g_30_mva  
from syngenlib import GeneratorOperatingPoint
import matplotlib.pyplot as plt 
import numpy as np
import time
from scipy.interpolate import griddata

V_g = 1.0 * g_30_mva.gen_data.V_nom_kV
P_g_vals = np.linspace(0.0, 1-1e-6, 100)*g_30_mva.gen_data.S_n_mva
Q_g_min = np.zeros_like(P_g_vals)
Q_g_max = np.zeros_like(P_g_vals)
Q_lim_stator_min = np.zeros_like(P_g_vals)
Q_lim_stator_max = np.zeros_like(P_g_vals)
Q_lim_rotor_max = np.zeros_like(P_g_vals)
Q_lim_stab_min = np.zeros_like(P_g_vals)
Q_lim_v_min = np.zeros_like(P_g_vals)
Q_lim_v_max = np.zeros_like(P_g_vals)

P_contour_plot = []
Q_contour_plot = []
p_loss_plot = []

t1 = time.time()

for i, P_g in enumerate(P_g_vals):
    q_lim_res = g_30_mva.gen_model.get_capability_limits(GeneratorOperatingPoint(P_g, 0.0, V_g))
    Q_min = q_lim_res.Q_min_tot
    Q_max = q_lim_res.Q_max_tot
    Q_g_vals = np.linspace(Q_min, Q_max, 100)

    Q_g_min[i] = Q_min
    Q_g_max[i] = Q_max
    Q_lim_stator_min[i] = q_lim_res.Q_stator_min
    Q_lim_stator_max[i] = q_lim_res.Q_stator_max
    Q_lim_rotor_max[i] = q_lim_res.Q_rotor_max
    Q_lim_stab_min[i] = q_lim_res.Q_stab_min
    Q_lim_v_min[i] = q_lim_res.Q_v_min
    Q_lim_v_max[i] = q_lim_res.Q_v_max

    for j, Q_g in enumerate(Q_g_vals):
        op = GeneratorOperatingPoint(P_g, Q_g, V_g)
        loss_res = g_30_mva.gen_model.get_branch_losses(op)
        P_contour_plot.append(P_g)
        Q_contour_plot.append(Q_g)
        p_loss_plot.append(loss_res.P_loss_branch_mw)

t2 = time.time()
print(f'Elapsed time: {((t2-t1)*1000):.2f} ms for {len(P_g_vals)*len(Q_g_vals)} points')

plt.figure(figsize=(5, 5))
plt.plot(Q_g_min, P_g_vals, label='Full Q-Capability', color='black', linewidth=4)
plt.plot(Q_g_max, P_g_vals, color='black', linewidth=4)
plt.plot(Q_lim_stator_min, P_g_vals, label='Stator Q-Limit', color='red')
plt.plot(Q_lim_stator_max, P_g_vals, color='red')
plt.plot(Q_lim_rotor_max, P_g_vals, label='Rotor Q-Limit', color='blue')
plt.plot(Q_lim_stab_min, P_g_vals, label='Stability Q-Limit', color='green')
plt.plot(Q_lim_v_min, P_g_vals, label='Voltage Q-Limit', color='grey', linestyle='--')
plt.plot(Q_lim_v_max, P_g_vals, color='grey', linestyle='--')
plt.fill_betweenx(P_g_vals, Q_g_min, Q_g_max, color='grey', alpha=0.2)

Q_mesh = np.linspace(min(Q_contour_plot), max(Q_contour_plot), 1000) 
P_mesh = np.linspace(min(P_contour_plot), max(P_contour_plot), 1000)
Q_mesh, P_mesh = np.meshgrid(Q_mesh, P_mesh)

power_losses_mesh = griddata((Q_contour_plot, P_contour_plot), p_loss_plot, (Q_mesh, P_mesh), method="linear")

plt.contourf(Q_mesh, P_mesh, power_losses_mesh, 20, cmap='RdGy_r')
plt.colorbar(label='Power losses (MW)')
plt.contour(Q_mesh, P_mesh, power_losses_mesh, 20, colors='black', linewidths=0.5)
plt.xlabel('$Q_n$ (Mvar)')
plt.ylabel('$P_n$ (MW)')
plt.title('Generator power losses (MW)')
plt.grid()
# plt.legend()
plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1.05), ncol=2, frameon=True)

plt.savefig("figures//illustrative_example.pdf", bbox_inches='tight', dpi=300)
plt.show()
