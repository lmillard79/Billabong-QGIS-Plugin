import os
import urllib.parse as urlparse

from PyQt5 import QtXml


class QlrFile:

    def __init__(self, xml):
        try:
            # Check if xml is a file path or XML content
            if isinstance(xml, str) and os.path.exists(xml):
                # It's a file path, read the content
                with open(xml, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
            else:
                # It's already XML content
                xml_content = xml
            
            self.doc = QtXml.QDomDocument()
            success, error_msg, error_line, error_column = self.doc.setContent(xml_content, True)
            if not success:
                pass

        except Exception as e:
            pass

    def get_menu_structure(self):
        """
        Returns a recursive structure of groups and layers from the BILLABONG group.
        """
        root_groups = self.doc.elementsByTagName("layer-tree-group")
        if root_groups.count() == 0:
            return []

        # Find the BILLABONG group
        billabong_group = None
        i = 0
        while i < root_groups.count():
            group = root_groups.at(i)
            group_element = group.toElement()
            if (group_element.hasAttribute("name") and 
                group_element.attribute("name") == "BILLABONG"):
                billabong_group = group
                break
            i += 1
            
        if not billabong_group:
            return []
            
        return self._parse_group_children(billabong_group)

    def _parse_group_children(self, group_node):
        """
        Recursively parse children of a group node.
        """
        items = []
        child_nodes = group_node.childNodes()
        
        i = 0
        while i < child_nodes.count():
            node = child_nodes.at(i)
            
            if node.nodeName() == "layer-tree-group":
                # Recursive call for subgroups
                group_element = node.toElement()
                group_name = group_element.attribute("name")
                
                # Skip unnamed groups
                if group_name:
                    children = self._parse_group_children(node)
                    # Add group even if empty? Or only if it has children?
                    # Original code filtered empty groups. Let's keep that logic if desired.
                    # But a group might be a container for future stuff.
                    # Let's add it if it has children.
                    if children:
                        items.append({
                            "type": "group",
                            "name": group_name,
                            "children": children
                        })
                        
            elif node.nodeName() == "layer-tree-layer":
                # Parse layer
                layer_data = self._parse_layer_node(node)
                if layer_data:
                    items.append(layer_data)
                    
            i += 1
            
        return items

    def _parse_layer_node(self, layer_node):
        """
        Extract layer info from a layer node.
        """
        layer_name = layer_node.toElement().attribute("name")
        layer_id = layer_node.toElement().attribute("id")
        
        maplayer_node = self.get_maplayer_node(layer_id)
        
        if maplayer_node:
            service = self.get_maplayer_service(maplayer_node)
            if service:
                return {
                    "type": "layer",
                    "name": layer_name,
                    "id": layer_id,
                    "service": service,
                    "source": "billabong" 
                }
        return None

    # Legacy method for backward compatibility during refactor
    def get_groups_with_layers(self):
        """
        Legacy flat structure parser. 
        It only looks one level deep under BILLABONG.
        """
        structure = self.get_menu_structure()
        # Convert the recursive structure to the flat 'selectables' format expected by legacy code
        result = []
        for item in structure:
            if item["type"] == "group":
                layers = []
                self._flatten_layers(item["children"], layers)
                if layers:
                    result.append({
                        "name": item["name"],
                        "layers": layers
                    })
        return result

    def _flatten_layers(self, items, result_list):
        for item in items:
            if item["type"] == "layer":
                result_list.append(item)
            elif item["type"] == "group":
                self._flatten_layers(item["children"], result_list)

    def get_maplayer_service(self, maplayer_node):
        service = "other"
        datasource_node = None
        datasource_nodes = maplayer_node.toElement().elementsByTagName(
            "datasource"
        )
        if datasource_nodes.count() == 1:
            datasource_node = datasource_nodes.at(0)
            datasource = datasource_node.toElement().text()
            
            # Try to extract service information from datasource
            if "url=" in datasource:
                # Extract URL from datasource
                url_start = datasource.find("url='")
                if url_start != -1:
                    url_start += 5  # Move past "url='"
                    url_end = datasource.find("'", url_start)
                    if url_end != -1:
                        url = datasource[url_start:url_end]
                        # Try to identify service from URL
                        if "bom.gov.au" in url:
                            service = "BoM"
                        elif "ga.gov.au" in url:
                            service = "GA"
                        elif "arcgis" in url:
                            service = "ArcGIS"
                        else:
                            service = "web"
            elif "servicename" in datasource:
                # Handle the original format
                url_part = None
                datasource_parts = datasource.split("&") + datasource.split(" ")
                for part in datasource_parts:
                    if part.startswith("url"):
                        url_part = part
                if url_part:
                    url = url_part[5:]
                    url = urlparse.unquote(url)
                    url_params = dict(
                        urlparse.parse_qsl(urlparse.urlsplit(url).query)
                    )
                    try:
                        if url_params["servicename"]:
                            service = url_params["servicename"]
                    except:
                        service = "unknown"
        return service

    def get_maplayer_node(self, id):
        node = self.get_first_child_by_tag_name_value(
            self.doc.documentElement(), "maplayer", "id", id
        )
        return node

    def get_first_child_by_tag_name_value(self, elt, tagName, key, value):
        nodes = elt.elementsByTagName(tagName)
        i = 0
        while i < nodes.count():
            node = nodes.at(i)
            idNode = node.namedItem(key)
            if idNode is not None:
                # Check if the idNode has a text child
                if idNode.firstChild() and idNode.firstChild().isText():
                    child = idNode.firstChild().toText().data()
                    # Layer found
                    if child == value:
                        return node
            i += 1
        return None
