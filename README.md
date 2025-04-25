
# IndCalc

**IndCalc** designs solenoid inductors via quadratic programming
(OSQP). As of v0.2 it supports arbitrary magnetic cores.

```bash
python -m indcalc -L 10 --awg 24 --core iron
```

## Installation

```bash
git clone https://github.com/your-user/IndCalc.git
cd IndCalc
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## requirements.txt

* numpy
* scipy
* osqp

## Resources

Test Test
