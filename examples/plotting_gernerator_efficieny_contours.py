import gen_model_30_mva as g_30_mva  
from syngenlib import GeneratorOperatingPoint
import matplotlib.pyplot as plt 
import numpy as np

V_g = 1.0 
P_g_vals_pu = np.linspace(0.0, 1.0, 40)*g_30_mva.gen_data.S_n_mva
Q_g_vals_pu = np.linspace(-0.5, 0.6, 50)*g_30_mva.gen_data.S_n_mva

Q_mesh, P_mesh = np.meshgrid(Q_g_vals_pu, P_g_vals_pu)
power_losses = np.zeros_like(Q_mesh)

for i, P_g in enumerate(P_g_vals_pu):
    for j, Q_g in enumerate(Q_g_vals_pu):
        op = GeneratorOperatingPoint(P_g, Q_g, V_g)
        loss_res = g_30_mva.gen_model.get_branch_losses(op)
        power_losses[i, j] = loss_res.P_loss_branch_mw

plt.contourf(Q_mesh, P_mesh, power_losses, 20, cmap='RdGy_r')
plt.colorbar(label='Power losses (MW)')
plt.contour(Q_mesh, P_mesh, power_losses, 20, colors='black', linewidths=0.5)
plt.xlabel('Q_g (pu)')
plt.ylabel('P_g (pu)')
plt.title('Generator power losses (MW)')
plt.grid()
plt.show()
