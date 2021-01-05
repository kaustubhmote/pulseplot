from pathlib import Path
from pulseplot import pplot

EXAMPLES_DIR = Path(__file__).parent


p1 = r"""
p1 pl1 ph1 fH fck 
p2 pl0.6 ph_x fH sp=ramp_-20 w txCP 
p2 pl0.5 ph2 fX txCP
p3 pl0.8 fH w h// txdecoupling
p3 pl0.5 sp=fid_20 fX fcnone troff o phrec ecr np200

"""

p2 = r"""
p1 pl1 ph1 fH fck
p2 pl0.6 ph_x fH sp=ramp_-20 w txCP
p2 pl0.5 ph2 fX txCP
p3 pl0.8 fH w h//
p3 pl0.5 sp=fid_20 fX fcnone troff o phrec ecr np200

p1.5 pl0.3 txdecoupling fcw f2.0 st2.95 ecnone
"""

fig, ax = pplot(ncols=2, figsize=(10, 4), constrained_layout=True)

ax[1].center_align = True # default is False

titleargs = {"fontname":"Fira Code", "fontsize":12}
ax[0].set_title("ax.center_align = False (default)", **titleargs )
ax[1].set_title("ax.center_align = True", **titleargs)

for axis in ax.flat:
    axis.spacing = 0.02
    axis.params = {"p1": 0.2, "fH": 2, "fX": 1}
    axis.fontsize = 15
    axis.draw_channels("fH", "fX", limits=[-0.1, 5.5])
    axis.limits["xlow"] = 2.0
    # axis.axis(False)

ax[0].pseq(p1)
ax[1].pseq(p2)

fig.savefig(EXAMPLES_DIR.joinpath("cross_polarization.png"), dpi=70)
