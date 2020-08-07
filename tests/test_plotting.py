from pulseplot import pplot
import matplotlib.pyplot as plt
import numpy as np


def test_functions():
    fig, ax = pplot()
    ax.spacing = 0.015
    ax.pulse(plen=0.1, phase=1, power=1, channel=1, hatch=r"///")
    ax.pulse(plen=1, power=0.6, channel=1, wait=True, shape=lambda x: 0.5 + 0.2*x)
    ax.pulse(1, 0.6, channel=0,) 
    ax.pulse(2, 1, truncate=False, color="r", shape=lambda x: 0.25 + np.exp(1j*50*x - 2*x).real)
    ax.set_xlim(-0.5, 4)
    ax.set_ylim(-0.5, 2.4)

    fig.savefig("test_functions.png")



def test_string_input():
    pseq = r"""
    p0.1 pl1 ph0 ch1
    p1 pl0.5 ph1 ch1 txCP phpdy0.1 w
    p1 pl0.5 ph1 ch0 txCP 
    """
    pars = {i: {} for i in range(3)}
    pars[0] = {"hatch": r"///"}

    fig, ax = pplot()
    for i, j in enumerate(pseq.strip().split("\n")):
        ax.pseq(j, **pars[i])

    ax.set_xlim(-0.5, 4)
    ax.set_ylim(-0.5, 4)
    fig.savefig("test_string_input.png")


def test_all():

    pseq = """
    p0.1 pl1 ph0 ch1
    p1 pl0.5 ph1 ch1 sp0 txCP phpdy0.1 w
    p1 pl0.5 ph1 ch0 txCP 
    """

    fig, ax = pplot()
    ax.params = {"sp0": lambda x: x**2 + 0.1}
    ax.pseq(pseq, )
    ax.set_xlim(-0.1, 3)
    ax.set_ylim(-0.1, 3)
    plt.show()


if __name__ == "__main__":
    test_all()
