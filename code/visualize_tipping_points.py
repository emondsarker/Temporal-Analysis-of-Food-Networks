import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader

ZONE_AMOC_COLD = [
    "GBR", "IRL", "ISL", "NOR", "SWE", "FIN", "DNK", 
    "DEU", "FRA", "NLD", "BEL", "LUX", "CHE", "AUT", 
    "POL", "CZE", "SVK", "HUN", "EST", "LVA", "LTU", 
    "CAN", "USA"
]

ZONE_MONSOON_FAIL = [
    "IND", "PAK", 
    "NGA", "NER", "MLI", "SEN", "GHA", "CIV"
]

ZONE_AMAZON_DRY = [
    "BRA", "ARG", "PRY", "URY", "BOL", "PER", "COL"
]

def plot_tipping_points():
    print("Generating Tipping Points Map...")
    
    plt.figure(figsize=(15, 10))
    ax = plt.axes(projection=ccrs.Robinson())
    
    ax.add_feature(cfeature.LAND, facecolor='#f5f5f5')
    ax.add_feature(cfeature.OCEAN, facecolor='#e0f7fa')
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5, color='#444444')
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5, alpha=0.5)

    COLOR_AMOC = '#3f51b5'
    COLOR_MONSOON = '#ff9800'
    COLOR_AMAZON = '#d32f2f'
    
    shpfilename = shpreader.natural_earth(resolution='110m', category='cultural', name='admin_0_countries')
    reader = shpreader.Reader(shpfilename)
    countries = reader.records()

    for country in countries:
        iso3 = country.attributes.get('ADM0_A3')
        
        name = country.attributes.get('NAME')
        if name == 'France': iso3 = 'FRA'
        if name == 'Norway': iso3 = 'NOR'
        
        facecolor = None
        if iso3 in ZONE_AMOC_COLD:
            facecolor = COLOR_AMOC
        elif iso3 in ZONE_MONSOON_FAIL:
            facecolor = COLOR_MONSOON
        elif iso3 in ZONE_AMAZON_DRY:
            facecolor = COLOR_AMAZON
            
        if facecolor:
            ax.add_geometries([country.geometry], ccrs.PlateCarree(),
                              facecolor=facecolor, edgecolor='white', linewidth=0.5)

    patch_amoc = mpatches.Patch(color=COLOR_AMOC, label='AMOC Collapse (Cooling Zone)')
    patch_monsoon = mpatches.Patch(color=COLOR_MONSOON, label='Monsoon Failure (Drought Zone)')
    patch_amazon = mpatches.Patch(color=COLOR_AMAZON, label='Amazon Dieback (Savannification)')
    
    plt.legend(handles=[patch_amoc, patch_monsoon, patch_amazon], 
               loc='lower center', ncol=3, frameon=True, fontsize=11, 
               bbox_to_anchor=(0.5, -0.05)) # Place below map

    plt.title('Global Climate Tipping Point Impact Zones', fontsize=16, fontweight='bold', pad=20)
    plt.suptitle('Source Regions of Synchronous Crop Failure (2022 Baseline)', fontsize=12, y=0.92, color='gray')
    
    plt.tight_layout()
    plt.savefig('Map_Tipping_Point_Zones.png', dpi=300, bbox_inches='tight')
    print("Done! Saved 'Map_Tipping_Point_Zones.png'")


plot_tipping_points()
