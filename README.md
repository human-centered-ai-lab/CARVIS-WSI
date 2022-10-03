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
docker build -t slide-heatmap .
```

This command may take some time to run, depending on the system. It downloads the latest Docker Python image and installs all depenecies so this does not have to be done manually. \
For writing the exported files, there will be a user and user group with the same parameters added as your current user to avoid permission errors.

## Usage
To draw heatmap data, a csv file from iMotions is needed. All WSI files viewed in the iMotions meeting must be present inside `data` directory.

Run a new container with following parameters:

```
docker run --rm \
    -u $(id -u):$(id -g) \
    --name slide-heatmap \
    -v /absolute/path/to/data/:/data/ \
    -v /absolute/path/to/export/:/export/ \
    slide-heatmap \
    -l [EXPORT_LAYER]
```

The `-v` parameter bind mounts a local directory to a directory inside the container. It uses following convention: `local_dir : container_dir`. It is important to use abolute paths for this parameter! \
Also make sure to have write permissions to the export directory!

The `-c` parameter can be left away if no specific CSV file is desired. The container will take automatically the mounted `/data/` directory as input. If you want to specify one file, assume you are already in the mounted directory. \
All the other parameters are working like described in the table down below.

With the `-u` flag a user or user and group id can be specifyed [`id -u` is for user, `id -u` is for group]. This solves permission issues with the exported files by running the process inside the container with this specifyed user. \
If you don't have a special need for this you can leave it like it is and don't have to worry about it.

### Input parameters and their usage:
| Option | Description |
| ------ | ----------- |
|   -c   | input CSV file or input file directory (CSV and SVS files need to be inside here). |
|   -l   | (Recommended) specify extraction layer. the extraction resolution will be read from WSI metadata. |
|   -r   | render resolution for WSI (only needed of no -l is given). |
|   -t   | specify cell size. default is 50. cells are always square. |
|   -s   | output hatched heatmap. it is recommended to use a bigger cell size (~100) in combination with this option. |
|   -v   | enables viewpath drawing. the following parameters can be specifyed if -v is used. |
|   -p   | specify path strength. default value is 2. |
|   -i   | specify path RGB color. default is (3, 252, 102). |
|   -u   | specify point radius. default value is 9. |
|   -o   | specify point RGB color. default is (3, 252, 161). |

### Minmal native working example
To get heatmap data rendered on all wsi files used in one specific iMotions meeting and export all JPG's with their layer 3 resolution, use following line.

`
python3 src/main.py -c data/testMeeting.csv -l 3
`

Important to know is that a resolution with the same width/height ratio as the original wsi files has to be chosen if you specify a fixed resolution. Otherwise it is possible that only a part of the original wsi is being extracted.

> Note: Inside `data` directory must be all .csv and .svs files stored which where used by this iMotions meeting!

When the programm is has finished all renderings, "done." will be printed.

## Folder Structure
    .                           # Repository Root Folder
    ├── .vscode                 # VS Code settings (like run and debug settings)
    ├── src                     # Program Source Files
    ├── docker                  # run script for the entrypoint
    ├── templates               # holds hatching design files
    ├── images                  # Sample output images
    ├── export                  # JPG's with rendered heatmaps are exported here
    └── data                    # Stores iMotions and Whole Slide Image files

<br />

> **_NOTE:_** This Project is currently WIP! When features are implemented they get merged into master branch.
