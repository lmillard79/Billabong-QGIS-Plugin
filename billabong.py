import os.path
import webbrowser

from PyQt5.QtCore import QFileInfo, Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QAction, QMenu, QMessageBox, QDialog
from PyQt5 import uic
from qgis.core import QgsProject, QgsSettings, QgsTextAnnotation
from qgis.gui import QgsMapCanvas

from .config import Config
from .constants import ABOUT_FILE_URL, PLUGIN_NAME, QLR_URL
from .layer_locator_filter import LayerLocatorFilter
from .settings import BillabongOptionsFactory


class Billabong:
    """QGIS Plugin Implementation for Australian Flood and Rainfall Data"""

    def __init__(self, iface):
        """Constructor
        :param iface: An interface instance that will be passed to this class
                      which provides the hook by which you can manipulate the
                      QGIS application at run time.
        :type iface:  QgsInterface
        """
        self.iface = iface  # Reference to the QGIS interface
        self.settings = QgsSettings()

        path = QFileInfo(os.path.realpath(__file__)).path()
        cache_path = path + "/data/"
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)

        self.settings.setValue("cache_path", cache_path)
        self.settings.setValue("billabong_qlr", QLR_URL)
        self.settings.setValue(
            "help/helpSearchPath",
            [
                "https://docs.qgis.org/$qgis_short_version/$qgis_locale/docs/user_manual/",
                "https://wms-engineering.github.io/Billabong/",
            ],
        )

        # Initialize watermark
        self.watermark = None

    def initGui(self):
        self.options_factory = BillabongOptionsFactory(self)
        self.options_factory.setTitle(PLUGIN_NAME)
        self.iface.registerOptionsWidgetFactory(self.options_factory)

        self.create_menu()

    def create_menu(self):
        self.config = Config(self.settings)
        self.config.load()
        self.groups_and_layers = self.config.get_groups_and_layers()

        self.menu = QMenu(self.iface.mainWindow().menuBar())
        self.menu.setObjectName(PLUGIN_NAME)
        self.menu.setTitle(PLUGIN_NAME)

        helper = lambda _id: lambda: self.open_billabong_node(_id)
        local_helper = lambda _id: lambda: self.open_local_node(_id)

        self.menu_with_actions = []
        layer_action_map = {}  # Used for the locator filter

        # Process each category (billabong and local)
        for category in self.groups_and_layers:
            # Skip empty categories
            if not category:
                continue
                
            # Process each group in the category
            for group in category:
                # Skip groups without name or selectables
                if not group.get("name") or not group.get("selectables"):
                    continue
                    
                group_menu = QMenu()
                group_menu.setTitle(group["name"])
                
                # Process each layer in the group
                for layer in group["selectables"]:
                    # Skip layers without name or id
                    if not layer.get("name") or not layer.get("id"):
                        continue
                        
                    action = QAction(layer["name"], self.iface.mainWindow())
                    if layer.get("source") == "billabong":
                        action.triggered.connect(helper(layer["id"]))
                    else:
                        action.triggered.connect(local_helper(layer["id"]))
                    group_menu.addAction(action)

                    layer_action_map[layer["name"]] = action

                # Only add group menu if it has actions
                if group_menu.actions():
                    self.menu.addMenu(group_menu)
                    self.menu_with_actions.append(group_menu)

            # Add separator only if there are actions
            if self.menu.actions():
                self.menu.addSeparator()

        # Add locator filter
        self.layer_locator_filter = LayerLocatorFilter(
            self.iface, layer_action_map
        )
        self.iface.registerLocatorFilter(self.layer_locator_filter)

        # Add About the plugin menu item
        icon_about_path = os.path.join(
            os.path.dirname(__file__), "img/icon_about.png"
        )
        self.about_menu = QAction(
            QIcon(icon_about_path),
            "About the plugin",
            self.iface.mainWindow(),
        )
        self.about_menu.triggered.connect(self.about_plugin)
        self.menu.addAction(self.about_menu)

        menu_bar = self.iface.mainWindow().menuBar()
        menu_bar.insertMenu(
            self.iface.firstRightStandardMenu().menuAction(), self.menu
        )

    def open_local_node(self, id):
        node = self.config.get_local_maplayer_node(id)
        self.open_node(node, id)

    def open_billabong_node(self, id):
        node = self.config.get_billabong_maplayer_node(id)
        
        # Show Bureau of Meteorology acknowledgement if opening a BoM layer
        if id and ("BoM" in id):
            self.show_bom_acknowledgement()
        
        self.open_node(node, id)

    def open_node(self, node, id):
        QgsProject.instance().readLayer(node)
        layer = QgsProject.instance().mapLayer(id)
        if layer:
            # Add watermark for attribution
            self.add_watermark(layer.name())
            layer = [
                layer for layer in QgsProject.instance().mapLayers().values()
            ]
            return layer
        else:
            return None

    def about_plugin(self):
        """Show the about dialog with links to Digital Atlas."""
        try:
            # Load the about dialog UI
            about_dialog_ui_path = os.path.join(os.path.dirname(__file__), "settings", "about_dialog.ui")
            dialog = QDialog()
            uic.loadUi(about_dialog_ui_path, dialog)
            dialog.exec_()
        except Exception as e:
            # If UI file is not found, open the website
            webbrowser.open(ABOUT_FILE_URL)

    def unload(self):
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)
        self.iface.deregisterLocatorFilter(self.layer_locator_filter)
        self.options_factory = None
        self.layer_locator_filter = None
        self.clear_menu()

    def reload_menu(self):
        self.clear_menu()
        self.iface.deregisterLocatorFilter(self.layer_locator_filter)
        self.layer_locator_filter = None
        self.create_menu()

    def clear_menu(self):
        # Remove the sub-menus and the menu bar item
        for submenu in self.menu_with_actions:
            if submenu:
                submenu.deleteLater()
        if self.menu:
            self.menu.deleteLater()
        self.menu = None

    def add_watermark(self, layer_name):
        """Add an attribution watermark to the map canvas when a layer is added."""
        # Remove existing watermark if present
        if self.watermark:
            QgsProject.instance().annotationManager().removeAnnotation(self.watermark)
        
        # Create new watermark
        self.watermark = QgsTextAnnotation()
        
        # Set watermark text based on layer source
        if "Bureau of Meteorology" in layer_name or "BoM" in layer_name:
            text = "© Bureau of Meteorology"
        elif "Geoscience" in layer_name or "GA" in layer_name:
            text = "© Geoscience Australia"
        elif "Flood" in layer_name:
            text = "© Australian Flood Data"
        elif "Rainfall" in layer_name:
            text = "© Australian Rainfall Data"
        else:
            text = "Map data from publicly available sources"
        
        # Configure the watermark
        self.watermark.setDocumentSize(200, 30)
        self.watermark.setMapPosition(self.iface.mapCanvas().extent().center())
        self.watermark.setFrameSize(200, 30)
        
        # Set text properties
        document = self.watermark.document()
        document.setDefaultStyleSheet(
            "body { color: rgba(0, 0, 0, 150); font-size: 10px; font-family: Arial; }"
        )
        document.setHtml(f"<body>{text}</body>")
        
        # Position watermark in bottom right corner
        canvas = self.iface.mapCanvas()
        canvas_size = canvas.size()
        self.watermark.setFrameOffsetFromReferencePoint(
            canvas_size.width() - 210, canvas_size.height() - 40
        )
        
        # Add watermark to project
        QgsProject.instance().annotationManager().addAnnotation(self.watermark)

    def remove_watermark(self):
        """Remove the attribution watermark from the map canvas."""
        if self.watermark:
            QgsProject.instance().annotationManager().removeAnnotation(self.watermark)
            self.watermark = None

    def show_bom_acknowledgement(self):
        """Show the Bureau of Meteorology data acknowledgement dialog."""
        try:
            # Load the dialog UI
            dialog_ui_path = os.path.join(os.path.dirname(__file__), "settings", "bom_ack_dialog.ui")
            dialog = QDialog()
            uic.loadUi(dialog_ui_path, dialog)
            dialog.exec_()
        except Exception as e:
            # If UI file is not found, show a simple message box
            QMessageBox.information(
                self.iface.mainWindow(),
                "Bureau of Meteorology Data Acknowledgement",
                "By using Bureau of Meteorology data through this plugin, you acknowledge and agree to BoM's Terms of Service.\n\n"
                "Use of this data is for visualization purposes only within QGIS.\n\n"
                "For more information, please visit: http://www.bom.gov.au/other/copyright.shtml"
            )
