
"""Predefined magnetic core materials"""
from dataclasses import dataclass

@dataclass(frozen=True)
class CoreMaterial:
    name: str
    mu_r: float  # relative permeability

MATERIALS = {
    "air":        CoreMaterial("air",        1.0),
    "powder-iron":CoreMaterial("powder-iron",90.0),
    "iron":       CoreMaterial("iron",       1000.0),
    "ferrite":    CoreMaterial("ferrite",    2000.0),
}
