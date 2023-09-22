# HallPy_Teach
![GitHub release (with filter)](https://img.shields.io/github/v/release/maclariz/HallPy_Teach)
  ![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/maclariz/HallPy_Teach/.github%2Fworkflows%2Fpackage-build-and-publish.yml)  ![PyPI - Version](https://img.shields.io/pypi/v/HallPy_Teach)

## Description
This package uses PyVISA to control and read instruments (power supplies, multimeters etc.) to run experiments in the Physics Honours Laboratory, initially for Hall Effect, although control of Curie Weiss law is also envisaged. This automates the data acquisition and allows easy recording of many data points in patterns or intervals defined by the user, and produces data files containing the results in numpy arrays, suitable for plotting and data analysis.

## Get Started
Install the package
```python
pip install HallPy_Teach
```
Use it in a notebook with
```python
import HallPy_Teach as hp
```

## Guide to push updates to the package
- Make your changes on a different branch 
- Create a [New Pull Request](https://github.com/maclariz/HallPy_Teach/compare) which merging your branch to main.
  - On the pull request you will be able to see if the workflow is able to build the package
    <img width="854" alt="Screenshot 2023-09-22 at 02 37 51" src="https://github.com/maclariz/HallPy_Teach/assets/59671809/3e2241bd-f8cc-422a-8f53-db53b3d11449">
- If the workflow is successfull on the Pull Request page, feel free to merge to `main` and then create a release on the [Release Page](https://github.com/maclariz/HallPy_Teach/releases)
  - Make sure you add a NEW tag by clicking on the choose tag button and adding a new tag. Make sure its higher than the last release which is ![PyPI - Version](https://img.shields.io/pypi/v/HallPy_Teach)
  - If you chose an older tag, the package will build but the rest of the workflow will fail when github tries to upload the package to Pypi.

## More information can be found on https://hallpy.fofandi.dev
