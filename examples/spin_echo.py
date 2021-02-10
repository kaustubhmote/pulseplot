from pathlib import Path
import pulseplot as pplot

EXAMPLES_DIR = Path(__file__).parent

spin_echo = r"""
p1 ph1 fc=black
d10 tx=$\tau$ 
p2 ph2 
d10 tx=$\tau$  
p10 sp=fid phrec 
"""

fig, ax = pplot.subplots(figsize=(5, 1))
ax.pseq(spin_echo)
fig.savefig(EXAMPLES_DIR.joinpath("spin_echo.png"), dpi=150)
