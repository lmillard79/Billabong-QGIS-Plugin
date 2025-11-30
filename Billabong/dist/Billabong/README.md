# Billabong

<img src="https://github.com/lmillard79/Billabong/blob/main/img/WRM_DROPLET.png?raw=true" alt="Billabong logo" height="100">

Billabong is a comprehensive QGIS plugin for hydrology and flood engineering, providing instant access to Australian rainfall data, flood maps, satellite imagery, and essential web tools.

Billabong streamlines the workflow for Australian flood engineers and hydrologists by integrating critical datasets directly into QGIS. It provides organized access to over 100+ national and state-based layers, including Bureau of Meteorology rainfall data, Geoscience Australia topography, Digital Earth Australia satellite imagery, and historical flood maps for Queensland and NSW. The plugin also includes a suite of web tools for quick access to ARR Data Hub, RFFE, BoM design rainfall (IFD), and climate change data, making it an essential toolkit for water resource professionals.

## Features

- **Comprehensive Data Access**: Instant access to 100+ Australian flood, rainfall, topography, and satellite datasets.
- **Organized Hierarchy**: Layers categorized by National/State and logical groups (Surface Water, Groundwater, Catchments).
- **Web Tools Integration**: Quick links to essential engineering tools like ARR Data Hub, RFFE, BoM IFD, and Global Climate Data (GPM, ERA5).
- **Seamless Integration**: Adds layers with styling and labelling automatically applied.
- **Extensible**: Extend the plugin with custom Layer Definition Files (.QLR) and suggest new sources.

## Installation

### Requirements

- QGIS version 3.18 or higher
- Internet access for fetching online map layer web services

### Installation through QGIS

1. Open QGIS.
2. Navigate to `Plugins` > `Manage and Install Plugins`.
3. Search for *Billabong*.
4. Click the `Install` button.

### Installation through GitHub

1. Download the ZIP file from this repository.
2. In QGIS, navigate to `Plugins` > `Manage and Install Plugins`.
3. Click `Install from ZIP` and select the downloaded plugin file.

## Contributing

Please report any bugs or feature requests by creating an issue in this GitHub repository.

## Credits and License

Billabong was developed and is maintained by Lindsay Millard at WRM Water and Environment and is licensed under the GNU General Public License (GPL) v3.0 or later. You are free to use, modify, and distribute this plugin under the terms of the GNU GPL as published by the Free Software Foundation. This plugin is distributed in the hope that it will be useful, but without any warranty. See the [GNU GPL](https://www.gnu.org/licenses/) for more details.
The design and functionality of Billabong draw inspiration from the [Dataforsyningen QGIS plugin](https://github.com/SDFIdk/Qgis-dataforsyningen).
For more detailed instructions and usage guidelines, refer to the [User Manual](docs/index.md).

## Development

This plugin was developed with support from WRM Water and Environment. For information about the development process, fixes, and future enhancements, please see [documentation.md](docs/documentation.md).
