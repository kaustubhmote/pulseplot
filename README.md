# pulseplot

Tired of opening Inkspace or (*gasp*) Illustrator to make
simple pulse-timing diagrams? Want to combine spectra and 
pulse-timing diagrams on a single plot without having to manually
piece them together? Want an easy way to make shaped pulses, hatches, indicates phases, FIDs, and animation? How about something like this:


```python
import pulseplot as pplot

spin_echo = r"""
p0.2 pl1 ph1 f1 fc=black
d2 tx=$\tau$ f1 tdy=0.4
p0.4 pl1 ph2 f1
d2 tx=$\tau$ f1 tdy=0.4
p2 pl1 f1 sp=fid troff o phrec pdy0.2

"""

fig, ax = pplot.subplots(figsize=(10, 2))
ax.pseq(spin_echo)
ax.axis(False)
fig.savefig("spin_echo.png", dpi=150)
```

![Spin-Echo](examples/spin_echo.png "spin echo")
[See Source](examples/spin_echo.py)

### Or, maybe something more complicated?

![HSQC](examples/hsqcetgpsi.png "hsqc")
[See Source](examples/hsqcetgpsi.py)


# Requirements
1. Python 3.8 or higher
1. Matplotlib 3.3 or higher
1. Numpy


# Installation

1. Using pip
```
python -m pip install git+https://github.com/kaustubhmote/pulseplot
```

2. From Source
```
git clone https://github.com/kaustubhmote/pulseplot
cd pulseplot
[activate your virtual environment]
python -m pip install -r requirements.txt
```


# Usage

### The basics:

```python
>>> import pulseplot as pplot
>>> fig, ax = pplot.subplots()
>>> ax.pulse(r"p1 pl1 ph1 f1")
>>> ax.pulse(plen=1, power=1, phase=1, channel=1)
>>> ax.delay(r"d1")
>>> ax.delay(time=1)
>>> sequence = r"""
    p1 pl1 ph1
    d1
    """
>>> ax.pseq(sequence)
>>> pplot.show()
```
The following discussion aliases `matplotlib.pyplot` to `plt`, as is the norm. 

The function `pplot.subplots` returns a matplotlib `Figure` and `Axes` objects, and is just a thin wrapper around `plt.subplots()` call. It passes along all arguments given to it to `plt.subplots`. The only additional thing it does is define some methods on `Axes` that is returned (`ax`), so that it can, among other things, add pulses, delays, track their posistions on the horizontal axis, etc. In particular, the `ax.pulse` and `ax.delay` methods "apply" pulses and delays with either strings, keyword arguments, or both. the method `pseq` is probably the most useful, as multiple pulse and delays can be given conviniently. In addition the nice `plt.subplot_mosiac` function is also available in a similar manner as `pplot.subplot_mosiac`. If you instead want to use manually add an Axes to Figure using `fig.add_subplot(...)`, you should see [this]() example.

Note: Use raw strings (`r"..."`) to avoid issues with escape characters.


## Pulses and pulse annotations

```python
>>> # the following statements are equivalent

>>> ax.pseq(r"p1 pl1 f1") # or, ax.pulse(...)
>>> ax.pseq(r"p=1 pl=1 f=1")
```
This is in many ways similar to the Bruker syntax. The above statement draws a rectangle (pulse) with length=1 (p1), hieght=1 (pl1) starting at x-position that is automatically determined and y-position=1 (f1). Optionally, you can declare this with "=" for clarity. 


```python
>>> ax.pseq(r"p1 pl1 f1 ph1")
>>> ax.pseq(r"p1 pl1 f1 ph_x") 
>>> ax.pseq(r"p1 pl1 f1 ph1 pdy0.1 pdx-0.2")
>>> ax.pseq(r"p1 pl1 f1 tx$CP$")
```
The `ph1` declaration (equivalent to `ph=1`) adds a text $\phi_1$ at an automatically calculated location at the top of the pulse. If instead, you want to put in only a label `x`, simply start the text to be put in with an underscore. If you are not happy with the exact location of this label, use `pdx` and `pdy` to move the label from its automatically calculated position. Similarly, a text can be specified by `tx`and moved around using `tdx` and `tdy` from its default position (which is somewhere in the center of the pulse itself).


## Delays and annotations

```python
>>> ax.pseq(r"d2 tx$\tau$ tdy0.4 f1") # or, ax.delay(...)
```
The `d2` declaration adds a delay. `pulseplot` tracks the current 'time' by incrementing `ax.time` everytime a pulse or a delay is added, and automatically passing the current time to the next pulse or delay. The next pulse will be separated from the first by 2 units. Similar to the `ph` declaration, the `tx$\tau$` declaration adds a text at an automatically calculated location. You can move it around by the `tdx` and `tdy` declarations.

## Simultaneous and centered pulses

```python
>>> ax.pseq(r"""
p1 pl1 ph1 f1 w
p1 pl1 ph2 f2
p1 pl1 ph1 f1 c
""")
```
By default, `ax.time` moves to the end of the pulse after it is applied. Simply add a `w` in the declaration (stands for "wait") to not do so. This is convinient when left aligning two pulses. Add a `c` to indicate that the pulse is to be centered at the current position. 

## Shaped pulses

```python
>>> ax.pseq("""p1 pl1 f1 sp=fid troff o""")
>>> ax.pulse("p1 pl1 ph1 f1", shape=lambda x:x**2)
```
This would not be very useful library without the ability to add shaped pulses. Simply use the `sp=` declaration to give the shape. Currently, the library has these shapes: *fid, gauss, ramp, tan, sine, grad*. These are customizable. For example, `r"p1 pl1 sp=ramp_-30"` gives a shape with a linear ramp from 100% to 70% of the specified power level.  You should look through examples to see how to customize the reset of the shapes. 

If you need a completely different shape, you will need to define it as a function of a single variable, and pass the function to the `shape` argument in `ax.pulse`. Python's `lambda functions` comes in very handy here, as shown in the example above.

The case `sp=fid` is a bit special. All pulses are implemented as shapes using the `Polygon` patch in matplotlib. Only the top part of the pulse is the actual shape and vertical lines are drawn by default to the channel so that this looks like a pulse. For an fid, we turn this off using `troff`.  All `Polygon` patches, by default, are closed, i.e. the first and last points are joined. This should be turned off for an FID using the declaration `o` (stands for "open").


### Colors, hatches, and transparency. 

There are several more declarations than can be passed.

```python
>>> # The two statements below are equivalent

>>> ax.pulse(r"p1 pl1 ph1 f1 fc=black ec=red al=0.5 h=///")
>>> ax.pulse(
        r"p1 pl1 ph1 f1", 
        facecolor="black", 
        edgecolor="red", 
        alpha=0.5, 
        hatch="///",
    )

```




### Alignments

![CP](examples/cross_polarization.png "cp")
[See source](examples/cross_polarization.py)


# Make Animations
