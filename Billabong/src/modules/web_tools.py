import webbrowser
from PyQt5.QtWidgets import QMenu, QAction
from ..constants import (
    RFFE_URL, FFA_URL, CCC_URL,
    ARR_DATA_URL, BOM_IFD_URL, BOM_CLIMATE_URL, SILO_URL,
    BOM_WATER_DATA_URL, BOM_HRS_URL, BOM_GEOFABRIC_URL, 
    GA_ELEVATION_URL, ELVIS_URL, GA_CATALOG_FLOOD_URL, 
    ESSD_ARTICLE_URL, BOM_IFD_SE_URL,
    NSW_SES_DATA_URL, NSW_DATA_FLOOD_URL, NSW_DOI_URL,
    NSW_NARCLIM_DATA_URL, NSW_NARCLIM_INFO_URL,
    QLD_DATA_FLOOD_URL, QLD_HISTORICAL_FLOOD_URL, QLD_WATER_MODELLING_URL,
    GPM_URL, GPM_DATA_URL, GPM_DIR_URL, NASA_WORLDVIEW_URL,
    NOAA_PRECIP_URL, CHRS_PRECIP_URL, ECMWF_ERA5_URL,
    CDS_ERA5_SINGLE_URL, CDS_ERA5_LAND_URL, MSWEP_URL,
    WORLDCLIM_URL, CDS_SAT_PRECIP_URL, CDS_INSITU_URL,
    NCAR_GUIDE_URL, GEE_DATASETS_URL
)

class WebToolsModule:
    """
    Module for handling external web tool links.
    Designed to be easily extensible for future tools.
    """
    def __init__(self, iface):
        self.iface = iface

    def get_menu(self):
        """
        Returns a QMenu containing actions for external web tools.
        """
        menu = QMenu("Web Tools", self.iface.mainWindow())
        
        # Core Tools
        self._add_link(menu, "RFFE - Regional Flood Frequency Estimation", RFFE_URL)
        self._add_link(menu, "FFA - Flood Frequency Analysis", FFA_URL)
        self._add_link(menu, "CCC - Climate Change Factors", CCC_URL)
        
        menu.addSeparator()
        
        self._add_link(menu, "ARR Data Hub", ARR_DATA_URL)
        self._add_link(menu, "BoM Design Rainfall (IFD)", BOM_IFD_URL)
        self._add_link(menu, "BoM Climate Data", BOM_CLIMATE_URL)
        self._add_link(menu, "SILO Point Data (Longpaddock)", SILO_URL)
        
        menu.addSeparator()
        
        # National Data
        national_menu = QMenu("National Data", menu)
        self._add_link(national_menu, "BoM Water Data Online", BOM_WATER_DATA_URL)
        self._add_link(national_menu, "BoM Hydrologic Reference Stations", BOM_HRS_URL)
        self._add_link(national_menu, "BoM Geofabric", BOM_GEOFABRIC_URL)
        self._add_link(national_menu, "BoM IFD (SE Australia Gridded)", BOM_IFD_SE_URL)
        self._add_link(national_menu, "ELVIS Elevation Data", ELVIS_URL)
        self._add_link(national_menu, "GA Digital Elevation", GA_ELEVATION_URL)
        self._add_link(national_menu, "GA Flood Catalog", GA_CATALOG_FLOOD_URL)
        self._add_link(national_menu, "ESSD Article (2025)", ESSD_ARTICLE_URL)
        menu.addMenu(national_menu)

        # New South Wales
        nsw_menu = QMenu("New South Wales", menu)
        self._add_link(nsw_menu, "SES Flood Data", NSW_SES_DATA_URL)
        self._add_link(nsw_menu, "NSW Government Data (Flood)", NSW_DATA_FLOOD_URL)
        self._add_link(nsw_menu, "NSW Flood Data (DOI)", NSW_DOI_URL)
        self._add_link(nsw_menu, "NARCliM 2.0 Projections", NSW_NARCLIM_DATA_URL)
        self._add_link(nsw_menu, "NARCliM Information", NSW_NARCLIM_INFO_URL)
        menu.addMenu(nsw_menu)

        # Queensland
        qld_menu = QMenu("Queensland", menu)
        self._add_link(qld_menu, "QLD Government Data (Flood)", QLD_DATA_FLOOD_URL)
        self._add_link(qld_menu, "Historical Flood Map Series", QLD_HISTORICAL_FLOOD_URL)
        self._add_link(qld_menu, "Water Modelling Network Publications", QLD_WATER_MODELLING_URL)
        menu.addMenu(qld_menu)

        menu.addSeparator()

        # International & Satellite
        intl_menu = QMenu("International && Satellite Data", menu)
        
        # NASA / GPM
        gpm_menu = QMenu("NASA / GPM", intl_menu)
        self._add_link(gpm_menu, "GPM Home", GPM_URL)
        self._add_link(gpm_menu, "GPM Data", GPM_DATA_URL)
        self._add_link(gpm_menu, "GPM Directory", GPM_DIR_URL)
        self._add_link(gpm_menu, "NASA Worldview", NASA_WORLDVIEW_URL)
        intl_menu.addMenu(gpm_menu)

        # Copernicus / ECMWF
        copernicus_menu = QMenu("Copernicus / ECMWF", intl_menu)
        self._add_link(copernicus_menu, "ECMWF ERA5 Info", ECMWF_ERA5_URL)
        self._add_link(copernicus_menu, "ERA5 Single Levels (CDS)", CDS_ERA5_SINGLE_URL)
        self._add_link(copernicus_menu, "ERA5 Land (CDS)", CDS_ERA5_LAND_URL)
        self._add_link(copernicus_menu, "Satellite Precipitation (CDS)", CDS_SAT_PRECIP_URL)
        self._add_link(copernicus_menu, "In-Situ Gridded Obs (CDS)", CDS_INSITU_URL)
        intl_menu.addMenu(copernicus_menu)

        # Global & Research
        research_menu = QMenu("Global Datasets", intl_menu)
        self._add_link(research_menu, "NOAA Precipitation Tables", NOAA_PRECIP_URL)
        self._add_link(research_menu, "CHRS Precip Estimation", CHRS_PRECIP_URL)
        self._add_link(research_menu, "MSWEP (GloH2O)", MSWEP_URL)
        self._add_link(research_menu, "WorldClim 2.1", WORLDCLIM_URL)
        self._add_link(research_menu, "NCAR Climate Data Guide", NCAR_GUIDE_URL)
        self._add_link(research_menu, "Google Earth Engine Datasets", GEE_DATASETS_URL)
        intl_menu.addMenu(research_menu)

        menu.addMenu(intl_menu)
        
        return menu

    def _add_link(self, menu, name, url):
        action = QAction(name, menu)
        # Using a default lambda argument to capture the URL correctly in the loop/scope
        action.triggered.connect(lambda checked, u=url: webbrowser.open(u))
        menu.addAction(action)
