
import argparse
from .core import optimise_inductor
from .core_materials import MATERIALS

def main():
    parser = argparse.ArgumentParser(description="Solenoid inductor optimiser")
    parser.add_argument("-L", "--inductance", type=float, required=True,
                        help="Target inductance in microhenries")
    parser.add_argument("--awg", type=int, default=24, help="Wire gauge (default 24)")
    parser.add_argument("--core", choices=list(MATERIALS), default="air",
                        help="Core material (default air)")
    parser.add_argument("--Nmin", type=int, default=5)
    parser.add_argument("--Nmax", type=int, default=400)
    args = parser.parse_args()

    design = optimise_inductor(L_target_H=args.inductance*1e-6,
                               awg=args.awg,
                               core=args.core,
                               N_min=args.Nmin,
                               N_max=args.Nmax)
    print("Best design:")
    for k, v in design.as_dict().items():
        print(f"  {k}: {v:.3f}" if isinstance(v, float) else f"  {k}: {v}")

if __name__ == "__main__":
    main()
