from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pulseplot as pplot
from pulseplot import PulseSeq

TESTDIR = Path(__file__).parent


def test_pulse_1():
    fig, ax = pplot.subplots()
    ax.pulse("p1 pl1 ph1 f1 fck")
    ax.pulse("p2 pl2 ph2 f1 fcr h//")
    ax.pulse("p1 pl1 ph_x f0 fcg h||", shape=lambda x: np.exp(-((x - 0.5) ** 2) / 0.05))
    ax.pulse("p3 pl0.4 f1 ecr fcr al0.2 tfs12", text="A long Pulse text")
    ax.pulse(
        "p1 pl-0.5 f1 fcb al0.5 spg",
        text="shaded",
        shape=lambda x: np.exp(-((x - 0.5) ** 2) / 0.05),
    )
    ax.pulse("p2 pl0.5 f1 spfid ecr o troff", facecolor="none")
    ax.pulse("p1 pl1 f2 st8 sp=gauss")

    fig.savefig(TESTDIR.joinpath("test_pulse_1.png"))


def test_pulse_delay():
    fig, ax = pplot.subplots()
    ax.pulse(r"p1 pl1 ph1 f1 fck")
    ax.delay(r"d2 tx$\tau$ f1")
    ax.pulse(r"p1 pl1 ph1 f1 fck")
    ax.delay(r"d2 tx$\tau$ f1")
    ax.fid(r"p2 pl0.5 f1")
    fig.savefig(TESTDIR.joinpath("test_pulse_delay.png"))


def test_pulseseq():

    p = r"""
    p1 pl1 ph_x f2 fck nH90
    d2 tx$\tau$ f1
    p2 pl1 ph2 f2 w
    p2 pl1 ph3 f1 
    d2 tx$\tau$ f1
    p1 pl1 ph4 f1 fck w
    p1 pl1 ph5 f2 fck
    p3 pl1 sp=fid f1 troff o fcnone ecr w
    p3 pl0.9 sp=rampup_30 f2 tx=decoupling tkw={'fontsize':10}

    """


    fig, ax = pplot.subplots()
    ax.params = {"p1": 0.2, "pl1": 1, "p2": 0.3, "f1": 0, "f2": 2}
    p = PulseSeq(p, external_params=ax.params)
    p.edit(name="H90", facecolor="r")
    ax.spacing = 0.05
    ax.fontsize = 13
    ax.pseq(p)
    fig.savefig(TESTDIR.joinpath("test_pulseseq_1.png"))
    ax.clear()
    p.edit(index=0, phase=r"_y")
    ax.pseq(p)
    fig.savefig(TESTDIR.joinpath("test_pulseseq_2.png"))


def test_shaped_pulses():
    p = r"""
    p2 pl1 f1 sp=gauss tx=gauss ph1 ecr fcr al0.5 tkw={'rotation':90}
    p2 pl1 f2 sp=ramp_50 tx=rampup ph_x
    p2 pl1 f1 sp=ramp_-50 tx=rampdown ph_new tkw={'fontsize':10}
    p2 pl0.5 f2 sp=tan_50 tx=tanup
    p2 pl0.6 fH sp=tan_-50 tx=tandown
    p2 pl1 f2 troff o sp=fid phrec ecg
    p2 pl-0.5 sp=grad f1 fck
    p1 pl1 sp=sine f2 fcy
    p2 pl1 sp=q3 f1 fc=grey
    p2 pl1 sp=q5 f2 fc=grey

    """
    fig, ax = pplot.subplots()
    ax.fontsize = 11
    ax.params = {"p2": 4, "d1": 0.2, "f1":0, "f2":2, "fH":0}
    ax.pseq(p)
    fig.savefig(TESTDIR.joinpath("test_shaped_pulses.png"))


if __name__ == "__main__":
    test_shaped_pulses()
