import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.colors as mcolors

# --- CONFIGURATION ---
FILE_NETWORK = "2_Network_Centrality_Scores.csv"
FILE_REGRESSION = "3_Regression_Analysis_Data.csv"
FILE_SIMULATION = "5_Phase3_Lifeboat_Collapse.csv"

def plot_network_evolution():
    print("Generating Plot 1: Network Evolution...")
    try:
        df = pd.read_csv(FILE_NETWORK)
        
        # Aggregate Weighted Degree (Total Trade Volume) by Year
        # We use Sum or Mean. Sum shows total global volume growth.
        evolution = df.groupby('Year')['Weighted_Degree'].sum().reset_index()
        
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=evolution, x='Year', y='Weighted_Degree', marker='o', linewidth=2.5, color='#2c3e50')
        
        plt.title('Evolution of Global Food Network Volume (1992-2022)', fontsize=14, fontweight='bold')
        plt.ylabel('Total Global Trade Volume (Weighted Degree)', fontsize=12)
        plt.xlabel('Year', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('RQ1_Network_Evolution.png', dpi=300)
        print("  - Saved 'RQ1_Network_Evolution.png'")
        plt.close()
    except Exception as e:
        print(f"  - Error: {e}")

def plot_vulnerability_regression():
    print("Generating Plot 2: Vulnerability Regression...")
    try:
        # We want to see if Centrality (Trade Power) protects against Hunger (Availability)
        df = pd.read_csv(FILE_REGRESSION)
        
        # Filter for 2022 only
        df_2022 = df[df['Year'] == 2022].copy()
        
        plt.figure(figsize=(10, 6))
        
        # Log scale for Degree often looks better as trade follows power laws
        sns.scatterplot(
            data=df_2022, 
            x='Weighted_Degree', 
            y='Net_Food_Availability_Capita',
            hue='ISO3', # Just to vary colors, or remove hue
            legend=False,
            alpha=0.6,
            edgecolor='w'
        )
        
        plt.xscale('log')
        plt.title('Does Trade Power Correlate with Food Security? (2022)', fontsize=14, fontweight='bold')
        plt.xlabel('Centrality (Weighted Degree) - Log Scale', fontsize=12)
        plt.ylabel('Net Food Availability (kg/capita)', fontsize=12)
        
        sns.regplot(
            data=df_2022, 
            x='Weighted_Degree', 
            y='Net_Food_Availability_Capita', 
            scatter=False, 
            color='red',
            line_kws={'linestyle':'--'}
        )
        
        plt.grid(True, linestyle=':', alpha=0.5)
        plt.tight_layout()
        plt.savefig('RQ2_Regression_Analysis.png', dpi=300)
        print("  - Saved 'RQ2_Regression_Analysis.png'")
        plt.close()
    except Exception as e:
        print(f"  - Error: {e}")

def plot_lifeboat_map():
    print("Generating Plot 3: The 'Lifeboat' Map...")
    try:
        df = pd.read_csv(FILE_SIMULATION)
        
        # Convert Percent_Drop (e.g. -0.25) to Positive Loss % (e.g. 25.0) for plotting
        # If Drop is positive (gain), set to 0 risk.
        df['Loss_Pct'] = df['Percent_Drop'].apply(lambda x: abs(x)*100 if x < 0 else 0)
        
        data_map = dict(zip(df['ISO3'], df['Loss_Pct']))

        plt.figure(figsize=(15, 10))
        ax = plt.axes(projection=ccrs.Robinson())
        ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.5)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
        ax.add_feature(cfeature.OCEAN, color='#E0F7FA')
        ax.add_feature(cfeature.LAND, color='#f0f0f0')

        cmap = plt.get_cmap('YlOrRd')
        norm = mcolors.Normalize(vmin=0, vmax=50)

        shpfilename = shpreader.natural_earth(resolution='110m', category='cultural', name='admin_0_countries')
        reader = shpreader.Reader(shpfilename)
        countries = reader.records()

        for country in countries:
            iso3 = country.attributes.get('ADM0_A3')
            # Manual Fixes for Cartopy ISOs vs Standard ISOs
            if country.attributes.get('NAME') == 'France': iso3 = 'FRA'
            if country.attributes.get('NAME') == 'Norway': iso3 = 'NOR'
            
            val = data_map.get(iso3, 0)
            
            ax.add_geometries([country.geometry], ccrs.PlateCarree(),
                              facecolor=cmap(norm(val)),
                              edgecolor='black', linewidth=0.3)

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm._A = []
        cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.05, shrink=0.6)
        cbar.set_label('Projected Food Availability Drop (%)', fontsize=12)

        plt.title('The "Lifeboat" Collapse: Impact of 100% Export Cut from RUS/UKR', fontsize=16, fontweight='bold')
        plt.savefig('RQ3_Simulation_Map.png', dpi=300, bbox_inches='tight')
        print("  - Saved 'RQ3_Simulation_Map.png'")
        plt.close()
        
    except Exception as e:
        print(f"  - Error: {e}")


plot_network_evolution()
plot_vulnerability_regression()
plot_lifeboat_map()
print("Done. Check the .png files.")