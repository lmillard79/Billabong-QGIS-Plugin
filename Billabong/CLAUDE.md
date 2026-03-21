# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Billabong is a QGIS plugin (Python) for Australian flood engineers and hydrologists. It provides a QGIS menu with 100+ Australian hydrology/flood/rainfall map layers and web tool links. Requires QGIS 3.18+.

## Development Workflow

### Deploy to QGIS for testing
Run `deploy.bat` — this uses `robocopy` to sync the source directory to:
`%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\Billabong`

After deploying, restart QGIS or use the **Plugin Reloader** plugin to reload changes.

### Package for distribution
```
python package.py
```
Outputs `dist/Billabong.zip` ready for upload to plugins.qgis.org.

### Compile Qt resources (if `resources/resources.qrc` changes)
```
pyrcc5 resources/resources.qrc -o resources/resources.py
```

### Compile UI files (if `.ui` files change)
```
pyuic5 src/settings/settings.ui -o src/settings/settings_ui.py
```

## Architecture

The plugin entry point is `__init__.py` → `classFactory()` → returns a `Billabong` instance (`src/billabong.py`).

### Data flow: How layers get into the menu

1. **`data/billabong.qlr`** — A QGIS Layer Definition File (XML) containing all layer definitions, styled and organized under a root `<layer-tree-group name="BILLABONG">`.

2. **`src/qlr_file.py` (`QlrFile`)** — Parses the `.qlr` XML. `get_menu_structure()` recursively traverses the `BILLABONG` group, returning a list of dicts with `type: "group"` or `type: "layer"` nodes. `get_maplayer_node(id)` retrieves the full XML node for a layer (used when loading into QGIS).

3. **`src/billabong_config.py` (`BillabongConfig`)** — Loads `data/billabong.qlr` from disk and calls `QlrFile.get_menu_structure()`.

4. **`src/local_config.py` (`LocalConfig`)** — Same parsing logic for a user-supplied custom `.qlr` file (path stored in `QgsSettings["custom_qlr_file"]`). Marks layers with `source: "local"`.

5. **`src/config.py` (`Config`)** — Aggregates both configs. Returns a list of structures (billabong first, then local if present).

6. **`src/menu_manager.py` (`MenuManager`)** — Recursively builds `QMenu`/`QAction` items from the structure. All leaf `QAction`s are tracked in `self.actions` for the locator filter.

7. **`src/billabong.py` (`Billabong.create_menu()`)** — Orchestrates everything: loads config → builds menu via MenuManager → adds WebToolsModule → registers `LayerLocatorFilter`.

### Loading a layer into QGIS

When a user clicks a layer action, `Billabong.on_layer_selected()` calls either `open_billabong_node()` or `open_local_node()`, which retrieves the XML node via `Config` and calls `QgsProject.instance().readLayer(node)` to add it to the map.

BoM layers show an acknowledgement dialog (`src/settings/bom_ack_dialog.ui`) before loading.

### Key files

| File | Purpose |
|------|---------|
| `data/billabong.qlr` | Master layer catalog — **edit this to add/modify layers** |
| `src/constants.py` | All URLs (web tools + data sources) |
| `src/modules/web_tools.py` | Web Tools submenu construction |
| `src/settings/options_tab.py` | QGIS Options panel (custom QLR file path setting) |
| `src/layer_locator_filter.py` | QGIS locator bar integration for searching layers |
| `src/settings/*.ui` | Qt Designer UI files for dialogs |
| `metadata.txt` | QGIS plugin metadata (version, description, tags) |

### Adding new layers

Edit `data/billabong.qlr` directly in QGIS (via Layer > Save As Layer Definition File) or in a text editor. Layers must be nested under `<layer-tree-group name="BILLABONG">`. The menu hierarchy mirrors the group nesting in the QLR file.

### Adding new web tool links

1. Add the URL constant to `src/constants.py`.
2. Import and wire it in `src/modules/web_tools.py` using `self._add_link(menu, "Label", URL)`.
