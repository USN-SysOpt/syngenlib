from syngenlib.data import TransformerDataClass

trafo_103_mva = TransformerDataClass(S_n_mva=103, V_nom_kV=11, V_SCH=0.1, P_Cu=0.0031, 
                                     I_E=0.003, P_Fe=0.001, tap_ratio=1.0, Z_lv_ratio=0.5)

trafo_60_mva = TransformerDataClass(S_n_mva=60, V_nom_kV=9.5, V_SCH=0.1, P_Cu=0.0031, 
                                    I_E=0.003, P_Fe=0.001, tap_ratio=1.0, Z_lv_ratio=0.5)

trafo_120_mva = TransformerDataClass(S_n_mva=120, V_nom_kV=14.7, V_SCH=0.1, P_Cu=0.0031, 
                                     I_E=0.003, P_Fe=0.001, tap_ratio=1.0, Z_lv_ratio=0.5)
