from pathlib import Path
import pulseplot as pplot
from matplotlib.patches import Ellipse

EXAMPLES_DIR = Path(__file__).parent


fig, ax = pplot.subplots(figsize=(5 * 1.414, 5), layout='constrained')
ax.set_ylim(-10, 12)
ax.set_xlim(-10, 12)

rax = ax.rotor(length=3)
ax.annotate("", xytext=(-7, -7), xy=(-7, 10), arrowprops=dict(facecolor="black", width=0.5))
ax.annotate("", xytext=(-7, -7), xy=(10, 10), arrowprops=dict(facecolor="black", width=0.5))

ax.annotate("", xytext=(-7, 0), xy=(-3, -3), arrowprops=dict(facecolor="black", connectionstyle="arc3,rad=-0.4", arrowstyle='-'))

ax.text(-5, 2, r"54.7$^\mathrm{o}$", fontsize=20)
ax.text(-6, 9, r"B$_\mathrm{0}$", fontsize=20)

fig.savefig(EXAMPLES_DIR.joinpath("mas_rotor.png"), dpi=150)
pplot.show()
