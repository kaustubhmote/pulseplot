from pathlib import Path
from pulseplot import pplot

EXAMPLES_DIR = Path(__file__).parent

p = r"""
p1 pl1 ph1 fH pdy0.05 
p2 pl0.6 ph_x fH sp=ramp_50 w txCP tdy-0.08 pdy-0.1
p2 pl0.5 ph2 fX txCP pdy0.05
p3 pl0.8 fH w h//
p3 pl1 sp=fid_20 fX troff o phrec pdy-0.8 ecr np200

p1.5 pl0.3 txdecoupling fcw f2.2 st2.95 ecnone

"""

fig, ax = pplot(figsize=(5, 4), constrained_layout=True)

ax.spacing = 0.02
ax.params = {"p1": 0.2, "fH": 2, "fX": 1}
ax.fontsize = 15
ax.pseq(p)
ax.draw_channels(1, "fH")

ax.set(xlim=[-0.1, 5.3], ylim=[0.5, 3.4])
ax.axis(False)
fig.savefig(EXAMPLES_DIR.joinpath("cross_polarization.png"), dpi=70)
