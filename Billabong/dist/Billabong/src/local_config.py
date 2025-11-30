import os

from PyQt5.QtCore import QFile, QIODevice

from .qlr_file import QlrFile


class LocalConfig:
    """
    Handles the layers in the user's custom QLR file if it is provided
    in the plugin settings
    """

    def __init__(self, settings):
        self.settings = settings
        self.qlr_file = None
        self.categories = []
        self.load()

    def load(self):
        self.local_qlr_file_path = self.settings.value("custom_qlr_file")
        if self.local_qlr_file_path and os.path.exists(
            self.local_qlr_file_path
        ):
            self.qlr_file = self._load_qlr_file()
            self.categories = (
                self._parse_local_categories() if self.qlr_file else []
            )

    def _load_qlr_file(self):
        """Read and load the QLR file from the local path."""
        f = QFile(self.local_qlr_file_path)
        f.open(QIODevice.ReadOnly)
        return QlrFile(f.readAll())

    def _parse_local_categories(self):
        """Parse categories and layers from the loaded QLR file."""
        if not self.qlr_file:
            return []
        structure = self.qlr_file.get_menu_structure()
        self._update_source(structure)
        return structure

    def _update_source(self, items):
        for item in items:
            if item["type"] == "layer":
                item["source"] = "local"
            elif item["type"] == "group":
                self._update_source(item.get("children", []))

    def get_categories(self):
        return self.categories

    def get_maplayer_node(self, layer_id):
        return self.qlr_file.get_maplayer_node(layer_id)
