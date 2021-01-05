from pathlib import Path
from pulseplot import pplot

EXAMPLES_DIR = Path(__file__).parent

p = r"""
p.1 pl1 ph1 f2 fc=k
p1 pl0.6 ph_x f2 sp=ramp w txCP 
p1 pl0.5 ph2 f1 tx=CP
p1 pl0.8 f2 w fc=lightgrey tx=decoupling
p1 pl0.5 sp=fid_20 f1 fc=none troff o phrec ecr np200"""

fig, ax = pplot(ncols=2, figsize=(10, 4), constrained_layout=True)

ax[1].center_align = True  # default is False

titleargs = {"fontfamily": "monospace", "fontsize": 12}

ax[0].set_title("ax.center_align = False (default)", **titleargs)
ax[1].set_title("ax.center_align = True", **titleargs)

for axis in ax.flat:
    axis.spacing = 0.01
    axis.fontsize = 15
    axis.draw_channels(1, 2)
    axis.axis(False)
    axis.pseq(p)

fig.savefig(EXAMPLES_DIR.joinpath("cross_polarization.png"), dpi=70)
