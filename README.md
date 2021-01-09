# pulseplot

Tired of opening Inkspace or (*gasp*) Illustrator to make
simple pulse-timing diagrams? Want to combine spectra and 
pulse timing on a single plot without having to manually
piece them together? Look no further...


```python
import pulseplot as pplot

spin_echo = r"""
p1 pl1 ph1 f1 fc=black
d10 tx=τ
p2 pl1 ph2 f1
d10 tx=τ
p5 pl1 f1 sp=fid troff o

"""

fig, ax = plt.subplots(figsize=(10, 2))
ax.pseq(spin_echo)
ax.axis(False)
fig.savefig("spin_echo.png", dpi=150)
```

That's it!

# Features with examples

### Shaped pulse, colors, hatches, symbols, (and in general, the entire power of matplotlib). 

![HSQC](examples/hsqcetgpsi.png "hsqc")


### Choose between alignments

![CP](examples/cross_polarization.png "cp")

### Make Animations
