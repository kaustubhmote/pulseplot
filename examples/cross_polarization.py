from pathlib import Path
from pulseplot import pplot

EXAMPLES_DIR = Path(__file__).parent

p = r"""
p1 pl1 ph1 fH pdy0.05 fck
p2 pl0.6 ph_x fH sp=ramp_-20 w txCP tdy-0.05 pdy-0.05 
p2 pl0.5 ph2 fX txCP pdy0.05
p3 pl0.8 fH w h//
p3 pl0.5 sp=fid2_20 f1.1 sp=fid2_20 troff o phrec pdy-0.3 ecr np200

p1.5 pl0.3 txdecoupling fcw f2.0 st2.95 ecnone

"""
fig, ax = pplot(figsize=(5, 4), constrained_layout=True)

ax.spacing = 0.02
ax.params = {"p1": 0.2, "fH": 2, "fX": 1}
ax.fontsize = 15
ax.center_align = True
ax.pseq(p)
ax.draw_channels("fH", limits=[-0.1, 4])
ax.draw_channels("fX", limits=[-0.1, 2])
ax.axis(False)
ax.set(xlim=[-0.2, 5.3], ylim=[0.5, 2.8])
fig.savefig(EXAMPLES_DIR.joinpath("cross_polarization.png"), dpi=70)
