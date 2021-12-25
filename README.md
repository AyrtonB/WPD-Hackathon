# WPD-Hackathon

This repository includes the workflow used for submissions to the Western Power Distribition Data Science competition.

<br>
<br>

### Installation

You can install the library developed in this work using:

```bash
pip install git+https://github.com/ayrtonb/WPD-Hackathon.git
```

<br>
<br>

### Challenge Details

##### High-level Overview

This initial challenge aims to understand how accurately high resolution features can be estimated given only information from lower resolution data. Specifically we are asking participants to estimate the highest peak value and lowest trough at a one minute resolution within each half hourly period given only half hourly measurements. This is an interesting problem to a distribution network operator as the spikes in demand can mean strain on their network. Such issues may become increasingly common, especially on the lower voltages of the network, due to the expanding use of lower carbon technologies such as electric vehicles, and heat pumps. However, monitoring can be expensive (especially in the long term) as it requires investment in additional storage, communications equipment and processing units.

More details can be found [here](https://codalab.lisn.upsaclay.fr/competitions/213#learn_the_details).

<br>
<br>

### Literature

The literature used in this work is being tracked using Zotero within the [ESAIL group](https://www.zotero.org/groups/2739875/esail/collections/4VKQZ96D), please add new papers and comment on existing ones. These should hopefully make it a lot easier down the line if we turn the work into a paper.

<br>
<br>

### Environment Set-Up

The easiest way to set-up your `conda` environment is with the `setup_env.bat` script for Windows. Alternatively you can carry out these manual steps in your terminal:

```bash
> conda env create -f environment.yml
> conda activate wpdhack
> ipython kernel install --user --name=wpdhack
```


<br>
<br>

### Nb-Dev Design Approach

##### What is Nb-Dev?

> `nbdev` is a library that allows you to develop a python library in Jupyter Notebooks, putting all your code, tests and documentation in one place. That is: you now have a true literate programming environment, as envisioned by Donald Knuth back in 1983!"

<br>

##### Why use Nb-Dev?

It enables notebooks to be used as the origin of both the documentation and the code-base, improving code-readability and fitting more nicely within the standard data-science workflow. The library also provides a [several tools](https://nbdev.fast.ai/merge.html) to handle common problems such as merge issues with notebooks.

<br>

##### How to use Nb-Dev?

Most of the complexity around `nbdev` is in the initial set-up which has already been carried out for this repository, leaving the main learning curve as the special commands used in notebooks for exporting code. The special commands all have a `#` prefix and are used at the top of a cell.

* `#default_exp <sub-module-name>` - the name of the sub-module that the notebook will be outputted to (put in the first cell)
* `#exports` - to export all contents in the cell
* `#hide` - to remove the cell from the documentation

These just describe what to do with the cells though, we have to run another function to carry out this conversion (which is normally added at the end of each notebook):

```python
from nbdev.export import notebook2script
    
notebook2script()
```

<br>
<br>
