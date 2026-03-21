import os.path

from PyQt5.QtCore import QObject
from qgis.core import Qgis, QgsMessageLog

from .qlr_file import QlrFile


class BillabongConfig(QObject):

    def __init__(self, settings):
        super(BillabongConfig, self).__init__()
        self.settings = settings
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
            msg = f"Billabong: QLR data file not found at {qlr_path}"
            QgsMessageLog.logMessage(msg, "Billabong", Qgis.Critical)
            try:
                from qgis.utils import iface as _iface
                _iface.messageBar().pushMessage("Billabong", "Layer data file is missing — plugin may not function correctly.", level=Qgis.Critical)
            except Exception:
                pass
            return None
            
        QgsMessageLog.logMessage(
            f"QLR file exists, size: {os.path.getsize(qlr_path)} bytes",
            "Billabong",
            Qgis.Info,
        )
        
        try:
            qlr_file = QlrFile(qlr_path)
            QgsMessageLog.logMessage("QLR file loaded successfully", "Billabong", Qgis.Info)
        except Exception as e:
            QgsMessageLog.logMessage(
                f"An error occurred while loading QLR file: {e}",
                "Billabong",
                Qgis.Critical,
            )
            try:
                from qgis.utils import iface as _iface
                _iface.messageBar().pushMessage("Billabong", f"Failed to load layer data: {e}", level=Qgis.Critical)
            except Exception:
                pass
            qlr_file = None

        return qlr_file
