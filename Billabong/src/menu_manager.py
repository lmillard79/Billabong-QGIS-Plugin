from PyQt5.QtWidgets import QMenu, QAction

class MenuManager:
    """
    Manages the creation and clearing of the plugin menu.
    Supports recursive menu structures.
    """
    def __init__(self, iface, plugin_name):
        self.iface = iface
        self.plugin_name = plugin_name
        self.menu = None
        self.sub_menus = [] # Keep track of submenus to delete them properly
        self.actions = [] # Track all actions for locator filter

    def create_root_menu(self):
        """Creates the main plugin menu in the QGIS menu bar."""
        self.menu = QMenu(self.iface.mainWindow().menuBar())
        self.menu.setObjectName(self.plugin_name)
        self.menu.setTitle(self.plugin_name)
        
        menu_bar = self.iface.mainWindow().menuBar()
        menu_bar.insertMenu(
            self.iface.firstRightStandardMenu().menuAction(), self.menu
        )
        return self.menu

    def build_menu_from_structure(self, structure, parent_menu=None, layer_callback=None):
        """
        Recursively builds the menu from a list/tree structure.
        
        :param structure: List of dicts. Each dict can be a 'group' or 'layer'.
                          Groups have 'children' (list).
                          Layers have 'id', 'name', 'source'.
        :param parent_menu: The QMenu to add items to. Defaults to root menu.
        :param layer_callback: Function to call when a layer action is triggered.
                               Signature: callback(layer_id, source)
        """
        if parent_menu is None:
            parent_menu = self.menu
            
        for item in structure:
            if item.get("type") == "group":
                # Create submenu
                title = item.get("name", "Unnamed Group")
                submenu = QMenu(title, parent_menu)
                parent_menu.addMenu(submenu)
                self.sub_menus.append(submenu)
                
                # Recursively build children
                children = item.get("children", [])
                if children:
                    self.build_menu_from_structure(children, submenu, layer_callback)
                    
            elif item.get("type") == "layer":
                # Create action
                name = item.get("name", "Unnamed Layer")
                layer_id = item.get("id")
                source = item.get("source", "billabong")
                
                action = QAction(name, self.iface.mainWindow())
                if layer_callback and layer_id:
                    # Use a helper to capture the current values in the closure
                    action.triggered.connect(
                        self._make_callback(layer_callback, layer_id, source)
                    )
                parent_menu.addAction(action)
                self.actions.append(action)

    def _make_callback(self, callback, layer_id, source):
        """Helper to create a lambda that captures variables correctly."""
        return lambda: callback(layer_id, source)

    def add_action(self, action):
        """Adds an arbitrary action to the root menu."""
        if self.menu:
            self.menu.addAction(action)
            self.actions.append(action)

    def add_separator(self):
        """Adds a separator to the root menu."""
        if self.menu:
            self.menu.addSeparator()
            
    def add_menu(self, menu):
        """Adds a submenu to the root menu."""
        if self.menu:
            self.menu.addMenu(menu)
            self.sub_menus.append(menu)

    def clear(self):
        """Removes the menu and cleans up resources."""
        # Remove the sub-menus and the menu bar item
        for submenu in self.sub_menus:
            if submenu:
                submenu.deleteLater()
        self.sub_menus = []
        
        for action in self.actions:
            if action:
                action.deleteLater()
        self.actions = []
        
        if self.menu:
            self.menu.deleteLater()
        self.menu = None
