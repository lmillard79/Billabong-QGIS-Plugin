from .billabong import Billabong


def classFactory(iface):
    """
    Initialize the plugin
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    return Billabong(iface)
