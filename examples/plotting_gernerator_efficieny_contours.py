from syngenlib import GeneratorLossModel, GeneratorOperatingPoint 
from sample_generators import gen_103_mva
import matplotlib.pyplot as plt
import numpy as np

V_g = 1.0 
P_g_vals_pu = np.linspace(0.0, 1.0, 40)
Q_g_vals_pu = np.linspace(-0.5, 0.6, 50)

Q_mesh, P_mesh = np.meshgrid(Q_g_vals_pu, P_g_vals_pu)
power_losses = np.zeros_like(Q_mesh)

gen_loss_model = GeneratorLossModel(gen_103_mva)

for i, P_g in enumerate(P_g_vals_pu):
    for j, Q_g in enumerate(Q_g_vals_pu):
        op = GeneratorOperatingPoint(P_g*gen_103_mva.S_n_mva, Q_g*gen_103_mva.S_n_mva, V_g)
        loss_res = gen_loss_model.calculate_generator_power_losses(op)
        power_losses[i, j] = loss_res.get_total_losses_mw()

plt.contourf(Q_mesh, P_mesh, power_losses, 20, cmap='RdGy_r')
plt.colorbar(label='Power losses (MW)')
plt.contour(Q_mesh, P_mesh, power_losses, 20, colors='black', linewidths=0.5)
plt.xlabel('Q_g (pu)')
plt.ylabel('P_g (pu)')
plt.title('Generator power losses (MW)')
plt.grid()
plt.show()
