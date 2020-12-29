from pulseplot import pplot
import matplotlib.pyplot as plt
import numpy as np


def test_pulse_1():
    fig, ax = pplot()
    ax.pulse("p1 pl1 ph1 f1 fck")
    ax.pulse("p2 pl2 ph2 f1 fcr h//")
    ax.pulse("p1 pl1 ph_x f0 fcg h||", shape=lambda x: np.exp(-((x - 0.5) ** 2) / 0.05))
    ax.pulse("p3 pl0.4 f1 ecr fcr al0.2", text="A long Pulse text")
    ax.pulse(
        "p1 pl-0.5 f1 fcb al0.5 spg",
        text="shaded",
        shape=lambda x: np.exp(-((x - 0.5) ** 2) / 0.05),
    )
    ax.pulse("p2 pl0.5 f1 spf ecr o troff", facecolor="none")
    ax.fid("p2 pl0.5 f2 st8")

    ax.set_xlim(0, 11)
    ax.set_ylim(0, 3)

    fig.savefig("test_pulse_1.png")

    assert 1 is 1
