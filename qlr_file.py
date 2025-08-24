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
                # print(f"Reading QLR file from path: {xml}, size: {len(xml_content)} characters")
            else:
                # It's already XML content
                xml_content = xml
                # print(f"Using provided XML content, size: {len(xml_content)} characters")
            
            self.doc = QtXml.QDomDocument()
            success, error_msg, error_line, error_column = self.doc.setContent(xml_content, True)
            if not success:
                # print(f"Failed to parse XML: {error_msg} at line {error_line}, column {error_column}")
                pass
            # else:
                # print("XML parsed successfully")

        except Exception as e:
            # print(f"Exception in QlrFile constructor: {e}")
            pass

    def get_groups_with_layers(self):
        result = []
        # Get all layer-tree-group elements
        all_groups = self.doc.elementsByTagName("layer-tree-group")
        # Debugging: Log the number of groups found
        # print(f"Total layer-tree-group elements found: {all_groups.count()}")
        
        if all_groups.count() == 0:
            # print("No layer-tree-group elements found")
            return result
            
        # Find the BILLABONG group (it should be the first group with name="BILLABONG")
        billabong_group = None
        i = 0
        while i < all_groups.count():
            group = all_groups.at(i)
            group_element = group.toElement()
            # Debugging: Log group information
            # print(f"Checking group {i}: name='{group_element.attribute('name')}'")
            
            if (group_element.hasAttribute("name") and 
                group_element.attribute("name") == "BILLABONG"):
                billabong_group = group
                # print(f"Found BILLABONG group at index {i}")
                break
            i += 1
            
        # If we didn't find the BILLABONG group, return empty result
        if not billabong_group:
            # print("BILLABONG group not found")
            return result
            
        # Get the actual category groups (children of BILLABONG group)
        category_groups = billabong_group.childNodes()
        # print(f"Number of category groups (children of BILLABONG): {category_groups.count()}")
        
        i = 0
        while i < category_groups.count():
            category_group = category_groups.at(i)
            # print(f"Checking category group {i}: node name='{category_group.nodeName()}'")
            
            if category_group.nodeName() == "layer-tree-group":
                group_element = category_group.toElement()
                group_name = None
                if (group_element.hasAttribute("name") and 
                    group_element.attribute("name") != ""):
                    group_name = group_element.attribute("name")
                    # print(f"Found category group: {group_name}")
                    
                    layers = self.get_group_layers(category_group)
                    # print(f"Number of layers in {group_name}: {len(layers)}")
                    
                    if layers and group_name:
                        result.append({"name": group_name, "layers": layers})
                        # print(f"Added group {group_name} with {len(layers)} layers to result")
            i += 1
        # print(f"Total groups with layers: {len(result)}")
        return result

    def get_group_layers(self, group_node):
        result = []
        child_nodes = group_node.childNodes()
        # print(f"Number of child nodes in group: {child_nodes.count()}")
        
        i = 0
        while i < child_nodes.count():
            node = child_nodes.at(i)
            # print(f"Checking node {i}: name='{node.nodeName()}'")
            
            if node.nodeName() == "layer-tree-layer":
                layer_name = node.toElement().attribute("name")
                layer_id = node.toElement().attribute("id")
                # print(f"Found layer: name='{layer_name}', id='{layer_id}'")
                
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
                        # print(f"Added layer {layer_name} to result")
                else:
                    # print(f"Maplayer node not found for layer {layer_name} (ID: {layer_id})")
                    pass
            i += 1
        # print(f"Total layers found in group: {len(result)}")
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
