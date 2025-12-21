# Graph Maker

Generate JPG graph images from InfluxDB data for e-paper displays.

## Features

- Query data from InfluxDB
- Generate customizable graphs
- Save as JPG images with configurable sizes
- YAML-based configuration for easy management
- Support for multiple graphs in a single run

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd grafMaker
```

2. Copy the example config and edit it with your settings:
```bash
cp config.yaml.example config.yaml
# Edit config.yaml with your InfluxDB credentials and queries
```

3. Run the setup script to create a virtual environment and install dependencies:
```bash
chmod +x setup.sh
./setup.sh
```

This will create a `venv` folder with all dependencies installed locally (not globally).

## Configuration

Edit `config.yaml` to set up your InfluxDB connection and graphs:

- **influxdb**: Connection parameters (URL, token, org, bucket)
- **output**: Output directory, format, and DPI settings
- **graphs**: List of graphs to generate, each with:
  - `name`: Identifier for the graph
  - `query`: Flux query to fetch data from InfluxDB
  - `filename`: Output filename
  - `size`: Width and height in pixels
  - `title`, `xlabel`, `ylabel`: Graph labels

## Usage

**Option 1: Use the convenience script**
```bash
chmod +x run.sh
./run.sh
```

**Option 2: Manual activation**
```bash
source venv/bin/activate
python graph_maker.py
deactivate
```

The generated JPG files will be saved in the output directory specified in the config.

## Example

The default configuration includes two example graphs (temperature and humidity). Update the InfluxDB parameters and queries to match your data.

## E-paper Display

The generated JPG images are optimized for e-paper displays with:
- Configurable output sizes
- High contrast for better visibility
- Efficient file sizes
