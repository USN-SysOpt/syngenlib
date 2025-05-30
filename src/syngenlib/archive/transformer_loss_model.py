from syngenlib.data import TransformerDataClass, TransformerLossResult

class TransformerLossModel:
    """
    A class to model and calculate transformer losses.

    This class provides methods to calculate various aspects of transformer losses
    based on input parameters such as voltage, current, and power.

    Attributes:
        md (TransformerDataClass): Model data containing transformer parameters.
    """

    def __init__(self, trafo_data: TransformerDataClass):
        """
        Initialize the TransformerLossModel.

        Args:
            trafo_data (TransformerDataClass): Model data containing transformer parameters.
        """
        self.md = trafo_data

    def _calc_gen_V_I(self, V_r: complex, I_r: complex) -> tuple[complex, complex]:
        """
        Calculate generator-side voltage and current based on receiver-side values.

        Args:
            V_r (complex): Receiver-side voltage.
            I_r (complex): Receiver-side current.

        Returns:
            tuple[complex, complex]: A tuple containing (V_g, I_g), where:
                V_g (complex): Generator-side voltage.
                I_g (complex): Generator-side current.
        """
        V_g = self.md.A * V_r + self.md.B * I_r 
        I_g = self.md.C * V_r + self.md.D * I_r
        return V_g, I_g

    def _calc_P_losses(self, V_r: complex, I_r: complex, V_s: complex, I_s: complex) -> float:
        """
        Calculate power losses in different parts of the transformer.

        Args:
            V_r (complex): Receiver-side voltage.
            I_r (complex): Receiver-side current.
            V_s (complex): Sender-side voltage.
            I_s (complex): Sender-side current.

        Returns:
            float: Total power losses in the transformer.
        """
        I_12 = I_r + V_r * self.md.Y_hv
        P_hv_loss = abs(V_r)**2 * self.md.Y_hv.real
        P_lv_loss = abs(V_s)**2 * self.md.Y_lv.real
        P_12_loss = abs(I_12)**2 * self.md.Z_12.real
        return P_hv_loss + P_lv_loss + P_12_loss

    def get_P_losses(self, P_r_pu: float, Q_r_pu: float, V_r: complex) -> TransformerLossResult:
        """
        Calculate and return transformer losses based on input parameters.

        All input quantities are referred to at the grid-side (receiving side).

        Args:
            P_r_pu (float): Per-unit active power at the receiving end.
            Q_r_pu (float): Per-unit reactive power at the receiving end.
            V_r (complex): Receiving end voltage.

        Returns:
            TransformerLossResult: An instance containing calculated loss results, including:
                - Generator-side active and reactive power
                - Receiver-side active and reactive power
                - Generator-side and receiver-side voltages
        """
        I_grid = (P_r_pu - 1j*Q_r_pu) / V_r
        V_g, I_g = self._calc_gen_V_I(V_r, I_grid)
        S_gen = V_g * I_g.conjugate()
        return TransformerLossResult(S_gen.real, P_r_pu, S_gen.imag, Q_r_pu, V_g, V_r)