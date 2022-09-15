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

Now create both a directory for input data and one for export data inside the repository.

`mkdir data export`

Then build the docker container.

```
docker build -t slide-heatmap \
    --build-arg USER_ID=$(id -u) \
    --build-arg GROUP_ID=$(id -g) .
```

This command may take some time to run, depending on the system. It downloads the latest Docker Python image, installs all dependencies and builds and installs pixman from source. The prebuild version has a bug with openslide so this is necessary. Then it runs some tests and cleans up afterwards. Expect some more output while doing so. \
For writing the exported files, there will be a user and user group with the same parameters added as your current user to avoid permission errors.

## Usage
To draw heatmap data, a csv file from iMotions is needed. All WSI files viewed in the iMotions meeting must be present inside `data` directory.

Run a new container with following parameters:

```
docker run --rm --name slide-heatmap \
    -v /absolute/path/to/data/:/data/ \
    -v /absolute/path/to/export/:/export/ \
    slide-heatmap \
    008_P013.csv \
    3
```

The `-d` (detached) option can be omitted if program output is desired.
If there is no desire for a container name, the `-name` parameter can also be omitted. \
The `-v` parameter bind mounts a local directory to a directory inside the container. It uses following convention: `local_dir : container_dir`. Don't forget to use abolute paths for this parameter! \
Also make sure to have write permissions to the export directory! \
The last two lines are the parameters which are getting passed to the program. The first one is the desired .csv file and the second is the required output layer. Note that the output layer parameter reads the WSI metadata and uses the resolution of the given layer to render a thumnail of the WSI at layer 0. This ensures that the right aspect ratio is being used. 

### Input parameters and their usage:
| Option | Description |
| ------ | ----------- |
|   -c   | input CSV file |
|   -l   | specify extraction layer (extraction resolution will be read from WSI metadata) |
|   -r   | render resolution for WSI (only needed of no -l is given) |

### Minmal working example
To get heatmap data rendered on all wsi files used in one iMotions meeting, use following line. This command works when running SlideHeatmap native, or inside an already running docker container.

`
python3 src/main.py -c data/testMeeting.csv -l 3
`

Important to know is that a resolution with the same width/height ratio as the original wsi files has to be chosen.
Otherwise it is possible that only a part of the original wsi is being extracted.

> Note: Inside `data` directory must be all .csv and .svs files stored which where used by this iMotions meeting!

When the programm is has finished all renderings, "done." will be printed and it will wait for some input to terminate.

## Folder Structure
    .                           # Repository Root Folder
    ├── .vscode                 # VS Code settings (like run and debug settings)
    ├── src                     # Program Source Files
    ├── docker                  # run script for the entrypoint
    ├── images                  # Sample output images
    ├── export                  # JPG's with rendered heatmaps are exported here
    └── data                    # Stores iMotions and Whole Slide Image files

<br />

> **_NOTE:_** This Project is currently WIP! When features are implemented they get merged into master branch.
