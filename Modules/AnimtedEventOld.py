import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

def create_lens_animation(output_file="lens_animation.gif", M=1.0, mu=5.0, Dl=2.0, Ds=8.0):
    """
    Create an animated GIF showing the lens crossing in front of a source.

    Parameters
    ----------
    output_file : str
        Name of the output GIF file.
    M : float
        Lens mass in solar masses (M_sun).
    mu : float
        Proper motion in mas/yr.
    Dl : float
        Distance to the lens in kpc.
    Ds : float
        Distance to the source in kpc.
    """
    # Calculate Einstein radius
    kappa = 8.144  # mas/M_sun
    as2mas = 1000.0
    pirel_as = (1.0 / (Dl * 1000) - 1.0 / (Ds * 1000))
    pirel_mas = pirel_as * as2mas
    theta_E = np.sqrt(kappa * M * pirel_mas)

    # Animation parameters
    num_frames = 100
    x_lens = np.linspace(-2 * theta_E, 2 * theta_E, num_frames)

    # Set lens color based on mass
    if M <= 1.4:
        lens_color = "white"
        edge_color = "white"
    elif M <= 2.35:
        lens_color = "grey"
        edge_color = "grey"
    else:
        lens_color = "black"
        edge_color = "orange"

    # Create figure
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor("black")  # Proper black background
    ax.set_xlim(-3 * theta_E, 3 * theta_E)
    ax.set_ylim(-3 * theta_E, 3 * theta_E)
    ax.set_aspect('equal')
    ax.set_facecolor("black")  # Proper black background
    ax.axis('off')

    # Draw source and lens
    source = plt.Circle((0, 0), theta_E * 0.5, color='gold', alpha=0.8)
    lens = plt.Circle((0, 0), theta_E * 0.3, color=lens_color, ec=edge_color, lw=2, alpha=0.9)
    ax.add_artist(source)
    lens_artist = ax.add_artist(lens)

    # Animation function
    def update(frame):
        lens_artist.set_center((x_lens[frame], 0))
        return lens_artist,

    # Create animation
    ani = FuncAnimation(fig, update, frames=num_frames, blit=True, interval=50)

    # Save as GIF
    ani.save(output_file, writer=PillowWriter(fps=20))
    plt.close(fig)

    print(f"Animation saved to {output_file}")

# Test the function if this script is run directly
if __name__ == "__main__":
    create_lens_animation(
        output_file="test_lens_animation.gif",
        M=10,  # Stellar-mass black hole
        mu=5,  # Proper motion in mas/yr
        Dl=2,  # Lens distance in kpc
        Ds=8   # Source distance in kpc
    )