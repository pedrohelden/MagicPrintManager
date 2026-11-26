# Magic Print Manager

Tool for generating A4 duplex-ready PDFs of Magic: The Gathering cards.

## Features

- A4 layout with a 3×3 card grid.
- Standard Magic card backs.
- 63 × 88 mm card dimensions.
- Cutting guidelines.
- Single PDF with interleaved front and back pages.
- Graphical interface built with Tkinter.
- Collection naming and timestamped output files.

## Requirements

- Windows
- Python 3.12+
- requests
- Pillow
- ReportLab
- pypdf

## Installation

```powershell
pip install requests pillow reportlab pypdf
```

## Run

```powershell
python core\gui.py
```

## CSV Format

Required columns: `card`, `set`, `quantity`.

## Output

Generated PDFs are saved in the `output` directory.

## Version

**1.0.1**
