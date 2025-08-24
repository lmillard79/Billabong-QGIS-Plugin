import urllib.parse as urlparse

from PyQt5 import QtXml


class QlrFile:

    def __init__(self, xml):
        try:

            self.doc = QtXml.QDomDocument()
            self.doc.setContent(xml)

        except Exception as e:
            pass

    def get_groups_with_layers(self):
        result = []
        # Get all layer-tree-group elements
        all_groups = self.doc.elementsByTagName("layer-tree-group")
        if all_groups.count() == 0:
            return result
            
        # Find the BILLABONG group (it should be the first group with name="BILLABONG")
        billabong_group = None
        i = 0
        while i < all_groups.count():
            group = all_groups.at(i)
            group_element = group.toElement()
            if (group_element.hasAttribute("name") and 
                group_element.attribute("name") == "BILLABONG"):
                billabong_group = group
                break
            i += 1
            
        # If we didn't find the BILLABONG group, return empty result
        if not billabong_group:
            return result
            
        # Get the actual category groups (children of BILLABONG group)
        category_groups = billabong_group.childNodes()
        i = 0
        while i < category_groups.count():
            category_group = category_groups.at(i)
            if category_group.nodeName() == "layer-tree-group":
                group_element = category_group.toElement()
                group_name = None
                if (group_element.hasAttribute("name") and 
                    group_element.attribute("name") != ""):
                    group_name = group_element.attribute("name")
                    layers = self.get_group_layers(category_group)
                    if layers and group_name:
                        result.append({"name": group_name, "layers": layers})
            i += 1
        return result

    def get_group_layers(self, group_node):
        result = []
        child_nodes = group_node.childNodes()
        i = 0
        while i < child_nodes.count():
            node = child_nodes.at(i)
            if node.nodeName() == "layer-tree-layer":
                layer_name = node.toElement().attribute("name")
                layer_id = node.toElement().attribute("id")
                maplayer_node = self.get_maplayer_node(layer_id)
                # Debugging: print information about the layer
                # print(f"Layer name: {layer_name}, ID: {layer_id}, Maplayer node found: {maplayer_node is not None}")
                if maplayer_node:
                    service = self.get_maplayer_service(maplayer_node)
                    # Debugging: print service information
                    # print(f"Service for layer {layer_name}: {service}")
                    if service:
                        result.append(
                            {
                                "name": layer_name,
                                "id": layer_id,
                                "service": service,
                            }
                        )
            i += 1
        return result

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
            # Handle different datasource formats
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
