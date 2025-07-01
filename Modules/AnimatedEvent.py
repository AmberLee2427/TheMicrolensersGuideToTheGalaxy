import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from typing import Optional

def create_lens_animation(M: float, 
                          mu: float, 
                          Dl: float, 
                          Ds: float, 
                          output_file: Optional[str] = "lens_animation.gif",
                          save_path: Optional[str] ="./Assets/"
                          ) -> None:
    """
    Create an animated GIF showing the lensing effect with a fixed remnant and a moving background star.

    Parameters
    ----------
    M : float
        Lens mass in solar masses (M_sun).
    mu : float
        Proper motion in mas/yr.
    Dl : float
        Distance to the lens in kpc.
    Ds : float
        Distance to the source in kpc.
    output_file : Optional str
        Name of the output GIF file.
    save_path : Optional str
        Path to save the output GIF

    Returns
    -------
    None

    Notes  
    -----
    The file defaults are set to work with the RemnantsAndDarkMatter.ipynb notebook.
    """
    # **Fixed Frame Interval**
    frame_interval = 1000/5  # constant for all masses

    # **Make num_frames depend on mass**
    base_frames = 30  # Base number of frames
    num_frames = min(150, int(base_frames * (1 + np.log10(M + 1))))  # More frames for bigger masses (up to 150)

    # Set remnant color based on mass
    if M <= 1.4:
        remnant_color = "white"
        edge_color = "white"
    elif M <= 2.35:
        remnant_color = "grey"
        edge_color = "grey"
    else:
        remnant_color = "black"
        edge_color = "orange"

    # **Keep the remnant size FIXED**
    fixed_lens_size = 0.5  # Fixed size for the remnant
    remnant_radius = fixed_lens_size
    remnant_alpha = 0.9  # Less transparent now

    # **Source size scales inversely with lens mass (log scale)**
    source_radius = fixed_lens_size / (1 + np.log10(M + 1))  # Inversely proportional

    # **Fixed Source Movement in Pixel Space**
    fixed_pixel_movement = 3.0  # Constant across all masses
    x_source = np.linspace(-fixed_pixel_movement, fixed_pixel_movement, num_frames)  # Fixed range

    # Create rectangular figure
    fig, ax = plt.subplots(figsize=(8, 4))  # Widened figure, reduced height
    fig.patch.set_facecolor("black")  # Black background
    ax.set_xlim(-3, 3)  # FIXED axis limits (no mass dependence)
    ax.set_ylim(-1.5, 1.5)  # Reduce vertical space
    ax.set_aspect('equal')
    ax.set_facecolor("black")
    ax.axis('off')

    # **Draw source behind the remnant using `zorder`**
    source_artist = plt.Circle((-fixed_pixel_movement, 0), source_radius, color='gold', alpha=0.8, zorder=1)  # **zorder=1 (Back)**
    remnant = plt.Circle((0, 0), remnant_radius, color=remnant_color, ec=edge_color, lw=2, alpha=remnant_alpha, zorder=2)  # **zorder=2 (Front)**

    ax.add_artist(source_artist)
    ax.add_artist(remnant)

    # Animation function
    def update(frame):
        source_artist.set_center((x_source[frame], 0))
        return source_artist,

    # Create animation
    ani = FuncAnimation(fig, update, frames=num_frames, blit=True, interval=frame_interval)

    # Save as GIF
    output_file_path = save_path + output_file
    ani.save(output_file_path, writer=PillowWriter(fps=20))
    #ani.save(output_file, writer='imagemagick', fps=10)
    plt.close(fig)

    print(f"Animation saved to {output_file_path}")

# Test the function if this script is run directly
if __name__ == "__main__":
    M = 10  # Stellar-mass black hole
    mu = 5  # Proper motion in mas/yr
    Dl = 2  # Lens distance in kpc
    Ds = 8  # Source distance in kpc
    create_lens_animation(
        M,
        mu,
        Dl,
        Ds,
        output_file="test_lens_animation.gif",
        save_path="./"  # Save in the current directory
    )
