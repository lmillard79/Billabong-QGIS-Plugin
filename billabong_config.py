import codecs
import os.path
from datetime import datetime, timezone
from urllib.request import urlopen

from PyQt5.QtCore import QFile, QIODevice, QObject
from qgis.core import Qgis, QgsMessageLog

from .qlr_file import QlrFile


class BillabongConfig(QObject):

    def __init__(self, settings):
        super(BillabongConfig, self).__init__()
        self.settings = settings
        self.cached_billabong_qlr_file = os.path.join(
            self.settings.value("cache_path"), "billabong_data.qlr"
        )
        self.qlr_file = None
        self.categories = []

    def load(self):
        self.qlr_file = self._get_qlr_file()
        self.categories = self._parse_categories() if self.qlr_file else []

    def get_categories(self):
        return self.categories

    def get_maplayer_node(self, layer_id):
        return self.qlr_file.get_maplayer_node(layer_id)

    def _parse_categories(self):
        """Parse categories and layers from the QLR file."""
        categories = []
        groups = self.qlr_file.get_groups_with_layers()
        
        # Skip if no groups found
        if not groups:
            return categories
            
        for group in groups:
            # Skip groups without name or layers
            if not group.get("name") or not group.get("layers"):
                continue
                
            # Create selectables list
            selectables = []
            for layer in group["layers"]:
                # Skip layers without name or id
                if not layer.get("name") or not layer.get("id"):
                    continue
                    
                selectables.append({
                    "type": "layer",
                    "source": "billabong",
                    "name": layer["name"],
                    "id": layer["id"],
                })
            
            # Only add group if it has selectables
            if selectables:
                categories.append({
                    "name": group["name"],
                    "selectables": selectables,
                })
                
        return categories

    def _get_qlr_file(self):
        # Always use the local QLR file instead of fetching it remotely
        # This avoids issues with remote fetching and 404 errors
        try:
            qlr_file = QlrFile(
                os.path.join(os.path.dirname(__file__), "billabong.qlr")
            )
        except Exception as e:
            # There was an error loading the QLR file
            QgsMessageLog.logMessage(
                f"An error occurred while loading QLR file: {e}",
                "Billabong",
                Qgis.Critical,
            )
            qlr_file = None

        return qlr_file

    def _read_cached_qlr(self):
        f = QFile(self.cached_billabong_qlr_file)
        f.open(QIODevice.ReadOnly)
        content = f.readAll()
        return QlrFile(content)

    def _get_remote_qlr(self):
        with urlopen(self.settings.value("billabong_qlr")) as response:
            return response.read().decode("utf-8")

    def _write_local_qlr(self, content):
        if os.path.exists(self.cached_billabong_qlr_file):
            os.remove(self.cached_billabong_qlr_file)
        with codecs.open(self.cached_billabong_qlr_file, "w", "utf-8") as f:
            f.write(content)
