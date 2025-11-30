from PyQt5 import QtCore

from .billabong_config import BillabongConfig
from .local_config import LocalConfig


class Config(QtCore.QObject):

    def __init__(self, settings):
        super(Config, self).__init__()
        self.settings = settings
        self.billabong_config = BillabongConfig(self.settings)
        self.local_config = LocalConfig(settings)

    def load(self):
        self.local_config.load()
        self.billabong_config.load()

        self.billabong_groups_and_layers = self.billabong_config.get_categories()
        self.local_groups_and_layers = self.local_config.get_categories()

        self.groups_and_layers = []
        # Only add non-empty categories
        if self.billabong_groups_and_layers:
            self.groups_and_layers.append(self.billabong_groups_and_layers)
        if self.local_groups_and_layers:
            self.groups_and_layers.append(self.local_groups_and_layers)

    def get_groups_and_layers(self):
        return self.groups_and_layers

    def get_billabong_maplayer_node(self, id):
        return self.billabong_config.get_maplayer_node(id)

    def get_local_maplayer_node(self, id):
        return self.local_config.get_maplayer_node(id)
