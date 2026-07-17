from pathlib import Path
import pulseplot as pplot
import matplotlib.pyplot as plt
from PIL import Image

EXAMPLES_DIR = Path(__file__).parent

import io
import numpy as np


def create_rotor_gif(output_filename="rotor_animation.gif", fps=5):
    """
    Generates 20 frames varying the 'movement' parameter from 0.1 to 2,
    rendering them completely in-memory, and outputting an animated GIF.
    """

    # generate figures in memory
    movement_steps = np.linspace(0, 2.0, 40)
    frames = []
    for movement_val in movement_steps:
        plt.close("all")

        fig, ax = pplot.subplots(layout='constrained')
        ax.rotor(
            axdims=[0, 0, 11],
            length=6.4,
            radius=0.64,
            xpos=-1,
            ypos=0,
            movement=movement_val,
            smoothness=200,
        )
        ax.rotor(
            axdims=[0, 0, 11],
            length=5.0,
            radius=0.50,
            xpos=1.4,
            ypos=0,
            movement=movement_val * 2.3,
            smoothness=200,
        )
        ax.rotor(
            axdims=[0, 0, 11],
            length=2.0,
            radius=0.26,
            xpos=3.5,
            ypos=0.3,
            movement=movement_val * 4.5,
            smoothness=200,
        )
        ax.rotor(
            axdims=[0, 0, 11],
            length=1.3,
            radius=0.14,
            xpos=4.3,
            ypos=0.2,
            movement=movement_val * 7.3,
            smoothness=200,
        )

        ax.set_xlim(3, 35)
        ax.set_ylim(-2.5, 2.5)
        ax.set_axis_off()

        # 4. Save the figure to an in-memory bytes buffer
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)

        buf.seek(0)
        img = Image.open(buf)
        img.load()
        frames.append(img)
        buf.close()

    # create gif
    duration_ms = int(1000 / fps)
    if frames:
        frames[0].save(
            output_filename,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=duration_ms,
            loop=0,
        )


if __name__ == "__main__":
    create_rotor_gif(EXAMPLES_DIR / "rotor_movement.gif", fps=12)
