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
Import it in a Jupyter notebook or anyother notebook like python environment
```python
import HallPy_Teach as hp
```
Doing an experiment
There are two methods to doing experiments. 
***Method 1*** requires less hassel and allows you to setup your instruments to run the experiments via a GUI. The GUI will guide you through connecting and trouble shooting the required experiment and subsiquently the intsruments required for the selected experiemnt.
***Method 2*** is a more manual approach, this is the less prefered option but we've stated the second method here anyway because it is the method one would follow if they design their own experiment file. The guide to setting up your own experiments can be found on the [HallPy_Teach Website](https://hallpy.fofandi.dev/guides/)

### Method 1
#### Step 1: Experiemnt & Instrument Setup
When the following code block is run you will be guided through choosing the experiment and setting up the instruments for said experiment.
```python
import HallPy_Teach as Teach
experiment = Teach.Setup()
```

#### Step 2: Experiment Parameters & Data Collection
***You cannot run Step 2 without compelting step 1*** <br>
When the following code block is run you will start seeing the data being collected.
Only run this codeblock once your you've setup your experiment aparatus and you're ready to collect the data. 
If the experiment requires parameters to be set, such as *voltage sweep ranges* and *data collection intervals* you will see a guide to setting the required parameter(s).
Once the data collection has started you should see the data being visualised as it comes in. Once all the data is collected you should see a prompt saying so.
```python
data = experiment.doExperiment(experiment.expInsts)
```

### Method 2
***Read Method 1 before reading Method 2***
As stated before **Method 2** is added so users can run their own designed experiments. As you can see in the example below we are importing `yourExperimentFile.py` from which we will get the custom experiment.
```python
import yourExperimentFile.py as yourExp
import HallPy_Teach as Teach
allInstruments = Teach.initInstruments()
yourExpInstruments = yourExp.setup(allInstruments)
data = yourExp.doExperiment(yourExpInstruments)
```
As stated before **Method 2** exists so that you can run your own experiemnts which means that supporting good error handeling and guides for how to solve said errors is down to the author of the custom experiment. Just for the sake of reference, you can find a code block below which runs the `HallEffect` experiment, a experiment provided by the library, with **Method 2** instead of **Method 1**.

## Guide to push updates to the package
- Make your changes on a different branch 
- Create a [New Pull Request](https://github.com/maclariz/HallPy_Teach/compare) which merging your branch to main.
  - On the pull request you will be able to see if the workflow is able to build the package
    <img width="915" alt="Screenshot 2023-09-22 at 13 47 16" src="https://github.com/maclariz/HallPy_Teach/assets/59671809/ab48586b-c27e-4cf6-b9e0-f6afc1dd95cd">
- If the workflow is successfull on the Pull Request page, feel free to merge to `main` and then create a release on the [Release Page](https://github.com/maclariz/HallPy_Teach/releases)
  - Make sure you add a NEW tag by clicking on the choose tag button and adding a new tag. Make sure its higher than the last release which is ![PyPI - Version](https://img.shields.io/pypi/v/HallPy_Teach)
  - If you chose an older tag, the package will build but the rest of the workflow will fail when github tries to upload the package to Pypi.

## More information can be found on https://hallpy.fofandi.dev
