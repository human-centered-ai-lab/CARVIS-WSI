# SlideHeatmap
This Project aims to render heatmap data onto an extracted WSI using eye tracking data collected with iMotions.

<details>
<summary>Here are some up to date output sample files:</summary>
<br><img src="/images/sample_1.png"></br>
<br><img src="/images/sample_2.png"></br>
<br><img src="/images/sample_3.png"></br>
</details>

## Installation
To setup this programm you need to clone the master branch of this repository.

`git clone git@github.com:human-centered-ai-lab/SlideHeatmap.git`

Then install all requirements listed in [requirements.txt](requirements.txt).
Before usage, the `data` directory must be created.

`mkdir data`

Inside the `data` directory all .csv and WSI files (in the .svs file format) will be stored.

## Usage
To draw heatmap data, a csv file from iMotions is needed. All WSI files viewed in the iMotions meeting must be present inside `data` directory.

### Input parameters and their usage:
| Option | Description |
| ------ | ----------- |
|   -c   | input CSV file |
|   -r   | render resolution for WSI |
|   -l   | specify extraction layer (extraction resolution will be read from WSI metadata) |
|   -s   | (optional) svs file path |

### Simple working example
To get heatmap data rendered on all wsi files used in one iMotions meeting, use following line.

`
python3 src/main.py -c data/testMeeting.csv -r 5478,4622
`

Important to know is that a resolution with the same width/height ratio as the original wsi files has to be chosen.
Otherwise it is possible that only a part of the original wsi is being extracted.

> Note: Inside `data` directory must be all .svs files stored which where used by this iMotions meeting!

When the programm is done with all renderings, "done." will be printed and it wait's for some input to terminate.

## Folder Structure
    .                           # Repository Root Folder
    ├── .vscode                 # VS Code settings (like run and debug settings)
    ├── src                     # Program Source Files
    ├── images                  # Sample output images
    └── data                    # Stores iMotions and Whole Slide Image files

<br />

> **_NOTE:_** This Project is currently WIP! When features are implemented they get merged into master branch.
