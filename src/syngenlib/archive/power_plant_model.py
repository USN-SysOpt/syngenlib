# import numpy as np 
# from typing import Sequence
# import logging as lgn
# from dataclasses import dataclass

# from ..models.generator_loss_model import *
# from ..models.transformer_loss_model import * 
# from ..models.capability_diagram_model import * 
# from ..data.common import GeneratorDataClass, TransformerDataClass, CapabilityResult, PlantOperationalData, PlantLossResult

# class PlantModel: 
#     """ Assumes each generator is connected through a separate transformer to a common busbar. """
#     def __init__(self, 
#                  gen_data: Sequence[GeneratorDataClass], 
#                  trafo_data: Sequence[TransformerDataClass]): 
#         if len(gen_data) != len(trafo_data): 
#             lgn.warning("Different number of transformers and generators!")
#             return 
#         self.gen_data = gen_data
#         self.trafo_data = trafo_data
#         self.__post_init__()

#     def __post_init__(self): 
#         self.gen_models: Sequence[GeneratorLossModel] = []
#         self.trafo_models: Sequence[TransformerLossModel] = []
#         self.cap_diags: Sequence[CapabilityDiagram] = []
#         # Change each trafo base to be the same as each generator base. 
#         for gen, trafo in zip(self.gen_data, self.trafo_data): 
#             trafo = trafo.change_base(gen.S_n_mva, gen.V_nom_kV, inplace=False) 
#             self.gen_models.append(GeneratorLossModel(gen))
#             self.trafo_models.append(TransformerLossModel(trafo))
#             self.cap_diags.append(CapabilityDiagram(gen, trafo)) 

#     def _get_Q_lims(self, operation_data: PlantOperationalData) -> Sequence[CapabilityResult]: 
#         cd_res = []
#         for i, (cd, gen) in enumerate(zip(self.cap_diags, self.gen_data)): 
#             P = operation_data.P_g_hv_data[i] 
#             V_hv = operation_data.V_hv_data[i]
#             cd_res.append(cd.calc_Q_lims(P/gen.S_n_mva, V_hv))
#         return cd_res 
    
#     def get_plant_Q_lims(self, operation_data: PlantOperationalData): 
#         """
#         Returns (Q_min_tot_mvar, Q_max_tot_mvar)
#         """
#         cd_res = self._get_Q_lims(operation_data) 
#         Q_min_tot = 0 
#         Q_max_tot = 0 
#         for cd, gen in zip(cd_res, self.gen_data): 
#             Q_min_tot += cd.Q_min_tot*gen.S_n_mva
#             Q_max_tot += cd.Q_max_tot*gen.S_n_mva
#         return Q_min_tot, Q_max_tot 
    
#     def get_plant_losses(self, operation_data: PlantOperationalData) -> PlantLossResult: 
#         # Calculate the power losses for each unit, sequentially: 
#         V_hv = operation_data.V_hv_data
#         gen_loss_res = []
#         trafo_loss_res = []
#         cap_diag_res = []
#         for i, (gen, trafo, cd) in enumerate(zip(self.gen_models, self.trafo_models, self.cap_diags)): 
#             P = operation_data.P_g_hv_data[i]/gen.md.S_n_mva
#             Q = operation_data.Q_g_hv_data[i]/gen.md.S_n_mva
#             I = (P - 1j*Q)/V_hv 
#             V_g, I_g = trafo._calc_gen_V_I(V_hv, I) 
#             S_g = V_g * I_g.conjugate()
#             P_g = S_g.real
#             Q_g = S_g.imag

#             gen_loss_res.append(gen.get_P_losses(P_g, Q_g, abs(V_g)))
#             trafo_loss_res.append(trafo.get_P_losses(P, Q, V_hv))
#             cap_diag_res.append(cd.calc_Q_lims(P, V_hv))
        
#         return PlantLossResult(gen_loss_res, trafo_loss_res, cap_diag_res) 
    
#     def change_transformer_taps(self, *tap_ratios): 
#         """tap_1_new, tap_2_new, ..., tap_n_new"""
#         for tap_ratio, trafo in zip(tap_ratios, self.trafo_data): 
#             trafo.change_tap_ratio(tap_ratio)
#         self.__post_init__()

# @dataclass
# class PlantOperationalData: 
#     """Usage: 
#     1) Create an instance of this class given N_g and V_hv_data 
#     2) Give the P data sequences for all generators [All  in MW] 
#     3) Give the Q data sequences for all generators [All in Mvar]"""
#     N_g: int 
#     V_hv_data: Sequence[float]

#     def __post_init__(self): 
#         self.P_g_hv_data = np.zeros((self.N_g, len(self.V_hv_data)))
#         self.Q_g_hv_data = np.zeros((self.N_g, len(self.V_hv_data)))

#     def give_P_data(self, *P_g_sequences):
#         """Give all sequences of P_g (on the HV side) here for all generators"""
#         for i, P_g in enumerate(P_g_sequences): 
#             self.P_g_hv_data[i] = P_g 

#     def give_Q_data(self, *Q_g_sequences): 
#         """Give all sequences of Q_g (on the HV side) here for all generators"""
#         for i, Q_g in enumerate(Q_g_sequences): 
#             self.Q_g_hv_data[i] = Q_g 


# @dataclass
# class PlantLossResult: 
#     gen_data_results: Sequence[GeneratorLossResult]
#     trafo_data_results: Sequence[TransformerLossResult]
#     cap_diag_results: Sequence[CapabilityResult]

#     def __post_init__(self): 
#         self.len = len(self.gen_data_results[0].P_g_pu)

#     def get_P_loss_tot_mw(self, S_bases: Sequence[float]) -> Sequence[float]: 
#         """S_bases: [S_base_1, S_base_2, ..., S_base_N]"""
#         P_loss = np.zeros(self.len, dtype=float)
#         for gen_loss, trafo_loss, S_base in zip(self.gen_data_results, self.trafo_data_results, S_bases):
#             P_loss += gen_loss.get_all_losses_mw() + trafo_loss.get_losses_mw(S_base)

#         return P_loss 