# PyStereo

Desktop application for plotting and analysing structural geology data on stereonets (lower-hemisphere equal-area and equal-angle projections). Built with Tkinter and [mplstereonet](https://github.com/joferkington/mplstereonet).


## Features

- Planes (foliations), lineations and poles to planes
- Contour plots of orientation density
- Rotation of data
- Adjustable plot settings for each data type
- Import of measurements from text files, export of data and plots

## Installation

Requires Python 3.11 or newer (Tkinter is included in the standard Python installer for Windows and macOS; on Linux install `python3-tk`).

```
git clone https://github.com/ativojtko/PyStereo.git
cd PyStereo
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS
pip install .
```

## Usage

```
pystereo
```

or

```
python -m pystereo
```

## Input data

Plain text files with one measurement per line, separated by tabs or semicolons (`.tsv`, `.csv`):

| Column | Description |
|--------|-------------|
| 1 | ID (integer) |
| 2 | Type: `L` lineation, `S` plane, `P` pole |
| 3 | Azimuth, 0 to < 360° |
| 4 | Inclination (0–90° for planes, lineations and poles) |
| 5 | Comment (optional) |

Example:

```
1	S	120	45	foliation, outcrop A
2	L	95	30
```

Ready-to-use files are in the [`examples/`](examples/) folder. Rows that cannot be read are reported in a table together with the reason.

## Project structure

```
pystereo/
├── core/      calculations
├── plots/     stereonet plotting (mplstereonet)
├── gui/       main window, panels, dialogs
├── assets/    icons
└── file_io.py data import and export
```

## Citation

If you use PyStereo in your work, please cite it using the information in [`CITATION.cff`](CITATION.cff).

## Authors

Hana Balažovjechová, Rastislav Vojtko, Miroslav Zverka, Marcel Vasiľák

## License

MIT, see [`LICENSE.txt`](LICENSE.txt).