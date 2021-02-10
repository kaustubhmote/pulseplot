from pathlib import Path
import pulseplot as pplot

EXAMPLES_DIR = Path(__file__).parent

# elements of hsqc
grad = r"p1 pl0.5 sp=grad fc=grey f0"
pH90 = r"p1 pl1 fc=black f2"
pN90 = r"p1 pl1 fc=black f1"
pH180 = r"p2 pl1 f2"
pN180 = r"p2 pl1 f1"
flipback = r"p5 pl0.5 sp=gauss fc=lightgrey f2"
tau = r"d10 f2 tx=$\tau$"


# hsqc sequence
hsqc = fr"""
d5 tx=$^1H$ f2 w pl=0.5
d5 tx=$^{{15}}N$ f1 w
d5 tx=Grad f0 tdy-0.2
d5

# dephase 15N
{pN90}
{grad}
d2

# inept
{pH90}
{tau}
d-1
{grad}
{pH180} w
{pN180}
{grad}
d-1
{tau}
{pH90} ph_y 
{flipback} ph_-x
{grad}
{pN90} ph_x$^*$

# t1 evolution
d14 tx=$t_1$ f1 w
d7
{pH180} c kc
d7

# add line here
p0 n=t1end f1 pl0.8 w skw={{'linestyle':'--', 'linewidth':1}}

# echo, 15n dephasing
d4 f1 tx=$\delta_1$
{pN180}
d4 f1 tx=$\delta_1$
d-1
{grad} pl0.8 h---- 

# reverse inept
{pH90} w
{pN90} ph1
{tau} f1
d-1
{grad}
{pH180} w
{pN180}
{grad} 
d-1
{tau} f1

# refocus
{pN90} w
{pH90} ph_y
{tau}
{pH180} w
{pN180}
{tau}
{pH90}


# refocus, 1H rephasing
d4 f2 tx=$\delta_2$
{pH180}
d4 f2 tx=$\delta_2$
d-1
{grad} pl0.3 h---- 

# detect
p10 pl0.2 f1 ph=_WALTZ-16 w h////
p10 pl1 f2 sp=fid_20_4 phrec np=200
"""

fig, ax = pplot.subplots(figsize=(8, 2.5), constrained_layout=True)

ax.params = {"f1": 2, "f2": 4, "f0": 0.7}
ax.phase_dy = 0.1

ax.pseq(hsqc)
ax.draw_channels(0.7, 2, 4)

# x = ax.get_time(name="t1end")
# ax.vlines(x, 3, 2, linestyle="--", color="k", linewidth=1)

fig.savefig(EXAMPLES_DIR.joinpath("hsqcetgpsi.png"), dpi=150)
