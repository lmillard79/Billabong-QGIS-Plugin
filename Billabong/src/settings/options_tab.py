import os
import webbrowser

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton
from qgis.core import QgsSettings
from qgis.gui import (
    QgsFileWidget,
    QgsOptionsPageWidget,
    QgsOptionsWidgetFactory,
)

DESIGNER, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "settings.ui")
)


class BillabongOptionsFactory(QgsOptionsWidgetFactory):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    def icon(self):
        return QIcon(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "img", "WRM_DROPLET.png")
        )

    def createWidget(self, parent):
        return ConfigOptionsPage(parent, self.plugin)


class ConfigOptionsPage(QgsOptionsPageWidget, DESIGNER):

    def __init__(self, parent, plugin):
        super().__init__(parent)
        self.plugin = plugin
        self.setupUi(self)
        self.file_widget = self.findChild(QgsFileWidget, "custom_qlr_file")
        self.feedback_button = self.findChild(QPushButton, "feedbackButton")

        # Connect the feedback button
        if self.feedback_button:
            self.feedback_button.setText("Report an Issue")
            self.feedback_button.clicked.connect(self.open_github_issues)

        self.load_settings()

    def helpKey(self):
        return "settings"

    def load_settings(self):
        """Load the saved settings"""
        settings = QgsSettings()
        file_path = settings.value("custom_qlr_file", "", type=str)
        self.file_widget.setFilePath(file_path)

    def apply(self):
        """Save the current settings"""
        settings = QgsSettings()
        file_path = self.file_widget.filePath()
        settings.setValue("custom_qlr_file", file_path)

        self.plugin.reload_menu()
        return True

    def open_github_issues(self):
        """Open the GitHub issues page to report an issue."""
        webbrowser.open("https://github.com/lmillard79/Billabong/issues")
