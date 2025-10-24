The Microlenser's Guide to the Galaxy
=====================================

Hoist your towel and hitch a ride—this guide is the friendly stowaway you want on every microlensing voyage. Inside you will find choose-your-own-adventure notebooks, practical utilities, and the hard-won wisdom of the Roman microlensing community, all seasoned with the proper amount of pan-galactic sparkle.

Whether you are untangling your very first Paczyński curve or wrestling a binary source into submission, these resources are here to light the path, keep the jokes coming, and remind you that science is best done with curiosity in one hand and a mug of something comforting in the other.


Notebook Expeditions
--------------------

Pick a notebook, click the rocket, and let Binder spin up a live JupyterLab with the exercise already open. Prefer an offline jaunt? Each title links to the rendered documentation page so you can scout the terrain before you land.

- |binder-intro| :doc:`Notebooks/Introduction` — Orientation, Einstein radii, and a guided tour of microlensing essentials.
- |binder-single| :doc:`Notebooks/SingleLens` — Build and fit the classic 1L1S model, one glorious Paczyński bump at a time.
- |binder-binary| :doc:`Notebooks/BinarySource` — Explore the choreography of dual sources and nail down blended fluxes.
- |binder-planets| :doc:`Notebooks/PlanetsAndBrownDwarfs` — Hunt for planetary companions and elusive brown dwarfs in the wings of microlensing events.
- |binder-remnants| :doc:`Notebooks/RemnantsAndDarkMatter` — Trace the signatures of remnants and dark denizens lurking in Roman’s field of view.
- |binder-eras| :doc:`Notebooks/Eras` — Time-travel through the observational eras that shaped microlensing lore.
- |binder-modelling| :doc:`Notebooks/Modelling` — Dive deep into modelling strategies, optimisation tricks, and goodness-of-fit diagnostics.
- |binder-mulens| :doc:`Notebooks/MulensModelFSPLError` — Wrestle with finite-source effects the MulensModel way and learn to love numerical subtleties.


How the Exercises Appear Here
-----------------------------

The documentation always reflects the learner-ready notebooks: during the build we copy the repository’s `Notebooks/` directory as-is, so every exercise cell still shows the blank prompt rather than the worked answer. When you develop locally, use `replacement.py` and `solutions.py` to toggle between solved and reset states—but rest easy knowing that the published docs keep things delightfully spoiler-free.


.. toctree::
   :maxdepth: 1
   :caption: Notebook Library

   Notebooks/Introduction
   Notebooks/SingleLens
   Notebooks/BinarySource
   Notebooks/PlanetsAndBrownDwarfs
   Notebooks/RemnantsAndDarkMatter
   Notebooks/Eras
   Notebooks/Modelling
   Notebooks/MulensModelFSPLError


.. |binder-intro| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/AmberLee2427/TheMicrolensersGuideToTheGalaxy/HEAD?labpath=Notebooks%2FIntroduction.ipynb
   :alt: Launch Introduction notebook on Binder

.. |binder-single| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/AmberLee2427/TheMicrolensersGuideToTheGalaxy/HEAD?labpath=Notebooks%2FSingleLens.ipynb
   :alt: Launch Single Lens notebook on Binder

.. |binder-binary| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/AmberLee2427/TheMicrolensersGuideToTheGalaxy/HEAD?labpath=Notebooks%2FBinarySource.ipynb
   :alt: Launch Binary Source notebook on Binder

.. |binder-planets| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/AmberLee2427/TheMicrolensersGuideToTheGalaxy/HEAD?labpath=Notebooks%2FPlanetsAndBrownDwarfs.ipynb
   :alt: Launch Planets and Brown Dwarfs notebook on Binder

.. |binder-remnants| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/AmberLee2427/TheMicrolensersGuideToTheGalaxy/HEAD?labpath=Notebooks%2FRemnantsAndDarkMatter.ipynb
   :alt: Launch Remnants and Dark Matter notebook on Binder

.. |binder-eras| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/AmberLee2427/TheMicrolensersGuideToTheGalaxy/HEAD?labpath=Notebooks%2FEras.ipynb
   :alt: Launch Eras notebook on Binder

.. |binder-modelling| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/AmberLee2427/TheMicrolensersGuideToTheGalaxy/HEAD?labpath=Notebooks%2FModelling.ipynb
   :alt: Launch Modelling notebook on Binder

.. |binder-mulens| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/AmberLee2427/TheMicrolensersGuideToTheGalaxy/HEAD?labpath=Notebooks%2FMulensModelFSPLError.ipynb
   :alt: Launch MulensModel finite-source notebook on Binder
