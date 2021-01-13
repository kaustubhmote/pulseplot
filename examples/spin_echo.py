from pathlib import Path
import pulseplot as pplot

EXAMPLES_DIR = Path(__file__).parent

spin_echo = r"""
p0.2 pl1 ph1 f1 fc=black
d2 tx=$\tau$ f1 tdy=0.4
p0.4 pl1 ph2 f1
d2 tx=$\tau$ f1 tdy=0.4
p2 pl1 f1 sp=fid troff o phrec pdy0.2

"""

fig, ax = pplot.subplots(figsize=(5, 1))
ax.fontsize = 10
ax.pseq(spin_echo)
ax.axis(False)
fig.savefig(EXAMPLES_DIR.joinpath("spin_echo.png"), dpi=150)