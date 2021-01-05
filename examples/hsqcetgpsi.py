from pathlib import Path
from pulseplot import pplot

EXAMPLES_DIR = Path(__file__).parent

p = r"""
p1 pl1 ph f1 fck
p2 pl0.2 sp=grad fc=grey f0
d0.5
p1 pl1 f2 fc=k
d1 f2 tx=$\tau$ tdx=0.1
p2 pl0.2 sp=grad fc=grey f0
p2 pl1 f2 w
p2 pl1 f1
p2 pl0.2 f0 sp=grad fc=grey 
d1 f2 tx=$\tau$ tdx-0.1
p1 pl1 ph_y f2 fc=k
p2 pl0.2 f0 sp=grad fc=grey 
p1 pl1 ph_$\phi^{*}$ f1 fc=k

d1.1
p2 pl1 ph f2 w
d0.2 tx=$t_1$ f1
d1.1

d0.6 f1 tx=$\delta_1$ nt1end
p2 pl1 f1
d0.4 f1 tx=$\delta_1$ tdx=0.1

p2 pl0.3 f0 sp=grad fc=lightblue
p1 pl1 f1 ph1 fc=k w
p1 pl1 f2 fc=k
d1 f1 tx=$\tau$ tdx=0.1
p2 pl0.2 sp=grad fc=grey f0
p2 pl1 f2 w
p2 pl1 f1
p2 pl0.2 f0 sp=grad fc=grey 
d1 f1 tx=$\tau$ tdx=-0.1
p1 pl1 f1 fc=k w
p1 pl1 f2 ph_y fc=k
d0.8 f2 tx=$\tau$ tdx=0
p2 pl1 f2 w
p2 pl1 f1
d0.8 tx=$\tau$ f2
p1 pl1 f2 fc=k
d0.5 f2 tx=$\delta_2$
p2 pl1 f2
d0.2 f2 
p2 pl0.1 f0 sp=grad fc=lightblue w
d0.3 f2 tx=$\delta_2$ tdx=-0.1
p1.1 pl0.1 f1 tx=WALTZ-16 w tdy=0.2 h||| tfs13
p1.1 pl1 f2 sp=fid_20 phrec troff o np=200 pdy=0.1

"""

fig, ax = pplot(figsize=(8, 2.5), constrained_layout=True)

ax.params = {"p1": 0.1, "p2": 0.2, "d1": 0.6, "d2": 0.05, "pl1": 0.5, "f0": 0.4}
ax.fontsize = 13

ax.pseq(p)
ax.axis(False)
ax.draw_channels(1, 2)

x = ax.get_time(name="t1end")
ax.vlines(x, 1.5, 1, linestyle="--", color="k", linewidth=1)

fig.savefig(EXAMPLES_DIR.joinpath("hsqcetgpsi.png"), dpi=150)
