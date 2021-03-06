from pathlib import Path

import matplotlib.animation as animation
import numpy as np
import pulseplot as pplot

EXAMPLES_DIR = Path(__file__).parent


def format_time(time):

    name = r"\Delta"

    if time == 0:
        return " "

    if time == 1:
        return fr"${name}$"

    else:
        return f"${time}{name}$"


t = np.linspace(0, 2, 1000)
indirect_fid = np.exp(1j * 20 * 2 * np.pi * t - t)



def make_seq_pars(sequence):

    return [[i, j, format_time(j)] for i, j in zip(*sequence)]


states = "x y x y x y x y".split(), [0, 0, 2, 2, 4, 4, 6, 6]
states_tppi = "x y -x -y x y -x -y".split(), [0, 0, 2, 2, 4, 4, 6, 6]
tppi = "x y -x -y x y -x -y".split(), range(8)
phase_insensitive = "x x x x x x x x".split(), range(8) 



sequences = {
    "States": make_seq_pars(states),
    "States-TPPI": make_seq_pars(states_tppi),
    "TPPI": make_seq_pars(tppi),
    "Phase-Insensitive": make_seq_pars(phase_insensitive),
}


def psq(phase, delay, delay_txt, intensity):
    p90 = r"p0.5 pl1 fc=grey f1 skw={'linewidth': 2}"
    delay_pars = r"f1 nt1 tfs20 f1"

    psq_formatted = fr"""
        {p90} ph_{phase} pfs=30
        d={delay} tx={delay_txt} {delay_pars}
        {p90}
        d10 tx$\tau_{{mix}}$ f1 tfs20
        {p90}
        p10 pl{intensity} sp=fid_-15 f1 fc=none np=400 ec=red
        
        """

    return psq_formatted


fig, ax = pplot.subplot_mosaic(
    [["States", "States-TPPI"], ["TPPI", "Phase-Insensitive"]],
    constrained_layout=True,
    figsize=(16, 4),
    dpi=300,
)

parts, allparts = [], []

for i in range(len(sequences["TPPI"])):

    scan = fig.text(
        0.5,
        0.5,
        f"{i+1}",
        fontsize=50,
        ha="center",
        va="center",
        bbox=dict(facecolor="wheat", edgecolor="black", boxstyle="round,pad=0.2"),
    )

    for k, seq in sequences.items():

        # actual plotting
        ax[k].set_facecolor("seashell")
        ax[k].phase_dy = 0.1
        ax[k].params = {}
        ax[k].spacing = 0.1
        ax[k].time = 8
        ax[k].center_align = True
        ax[k].pseq(psq(*seq[i], 1))
        ax[k].axis(True)
        for _, s in ax[k].spines.items():
            s.set_visible(False)

        ax[k].set_xticks([])
        ax[k].set_yticks([])
        
        # make things look a bit nice
        ax[k].set_ylim(0, 2)
        ax[k].set_xlim(0, 38)

        if k in ["States", "TPPI"]:
            x = 1
            ha = "left"
        else:
            x = 37
            ha = "right"

        ax[k].text(x, 0.05, f"{k}", fontsize=25, ha=ha, va="bottom",
            bbox=dict(facecolor="salmon", edgecolor="black", boxstyle="round, pad=0.2"),
)
        # get parts for animation
        if i == 0:
            npatches, ntexts = len(ax[k].patches), len(ax[k].texts)

        parts.append(ax[k].patches[-npatches:] + ax[k].texts[-ntexts:] + [scan])

    allparts.append([item for sublist in parts for item in sublist])
    parts = []


ani = pplot.animation(fig, allparts, interval=1000, blit=False, repeat_delay=1000)
ani.save(EXAMPLES_DIR.joinpath("quadrature.gif"))
