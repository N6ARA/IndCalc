
"""
IndCalc Core
============

Optimises simple solenoid inductors with arbitrary magnetic cores via OSQP.
"""
import math
from dataclasses import dataclass
from typing import Dict

import numpy as np
import scipy.sparse as sp
import osqp

from .core_materials import MATERIALS, CoreMaterial

MU0 = 4 * math.pi * 1e-7  # H/m

AWG_DIAMETERS_M: Dict[int, float] = {10: 0.002588, 12: 0.002053, 14: 0.001628, 16: 0.001291, 18: 0.001024, 20: 0.000812, 22: 0.000644, 24: 0.000511, 26: 0.000405, 28: 0.000321, 30: 0.000255}

@dataclass
class InductorDesign:
    turns: int
    diameter_m: float
    length_m: float
    awg: int
    core: CoreMaterial

    @property
    def inductance_H(self) -> float:
        area = math.pi * (self.diameter_m / 2) ** 2
        return self.core.mu_r * MU0 * self.turns ** 2 * area / self.length_m

    def as_dict(self):
        return {
            "N": self.turns,
            "d_mm": self.diameter_m * 1e3,
            "l_mm": self.length_m * 1e3,
            "awg": self.awg,
            "core": self.core.name,
            "L_uH": self.inductance_H * 1e6,
        }

# ----------------------------------------------------------------------
def optimise_inductor(
    L_target_H: float,
    awg: int = 24,
    core: str = "air",
    N_min: int = 5,
    N_max: int = 400,
    axial_clearance_factor: float = 1.05,
    radial_clearance_factor: float = 1.05,
    weight_turns_vs_size: float = 1.0,
) -> InductorDesign:
    """Return a compact inductor design that meets *L_target_H*.

    Parameters
    ----------
    core : str
        One of MATERIALS keys, e.g. 'air', 'iron', 'ferrite'.
    """
    if awg not in AWG_DIAMETERS_M:
        raise ValueError(f"Unsupported AWG: {awg}")
    if core not in MATERIALS:
        raise ValueError(f"Unknown core material '{core}'. Valid: {list(MATERIALS)}")

    d_wire = AWG_DIAMETERS_M[awg]
    core_mat = MATERIALS[core]

    best = None
    best_obj = float("inf")
    Q = sp.csc_matrix((2, 2))  # 0.5 x^T Q x term (zero for linear)

    for N in range(N_min, N_max + 1):
        c = np.array([weight_turns_vs_size, 1.0])  # objective weights
        A_eq = np.array([[core_mat.mu_r * MU0 * math.pi / 4 * N**2, -L_target_H]])
        l_eq = u_eq = np.array([0.0])

        min_z = (N * d_wire * radial_clearance_factor) ** 2
        min_l = N * d_wire * axial_clearance_factor
        A_ineq = np.eye(2)
        l_ineq = np.array([min_z, min_l])
        u_ineq = np.array([np.inf, np.inf])

        A = sp.csc_matrix(np.vstack([A_eq, A_ineq]))
        l_bound = np.hstack([l_eq, l_ineq])
        u_bound = np.hstack([u_eq, u_ineq])

        prob = osqp.OSQP()
        prob.setup(P=Q, q=c, A=A, l=l_bound, u=u_bound, verbose=False)
        res = prob.solve()
        if res.info.status != "solved":
            continue

        z_opt, l_opt = res.x
        d_opt = math.sqrt(z_opt)
        obj = c @ res.x

        if obj < best_obj:
            best_obj = obj
            best = InductorDesign(turns=N, diameter_m=d_opt, length_m=l_opt,
                                  awg=awg, core=core_mat)

    if best is None:
        raise RuntimeError("No feasible design found.")
    return best
