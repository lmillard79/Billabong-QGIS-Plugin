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
        if not self.qlr_file:
            return []
        
        # Use the recursive structure from QlrFile
        structure = self.qlr_file.get_menu_structure()
        
        QgsMessageLog.logMessage(
            f"Loaded menu structure with {len(structure)} top-level items",
            "Billabong",
            Qgis.Info,
        )
        
        return structure

    def _get_qlr_file(self):
        # Always use the local QLR file instead of fetching it remotely
        # This avoids issues with remote fetching and 404 errors
        qlr_path = os.path.join(os.path.dirname(__file__), "..", "data", "billabong.qlr")
        QgsMessageLog.logMessage(
            f"Attempting to load QLR file from: {qlr_path}",
            "Billabong",
            Qgis.Info,
        )
        
        # Check if the file exists
        if not os.path.exists(qlr_path):
            QgsMessageLog.logMessage(
                f"QLR file does not exist at: {qlr_path}",
                "Billabong",
                Qgis.Critical,
            )
            return None
            
        QgsMessageLog.logMessage(
            f"QLR file exists, size: {os.path.getsize(qlr_path)} bytes",
            "Billabong",
            Qgis.Info,
        )
        
        try:
            qlr_file = QlrFile(qlr_path)
            QgsMessageLog.logMessage(
                "QLR file loaded successfully",
                "Billabong",
                Qgis.Info,
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
