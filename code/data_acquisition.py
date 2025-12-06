import pandas as pd
import world_trade_data as wits
import pycountry
import requests
import io
import zipfile

# CONFIGURATION 
YEARS = ['1992', '2002', '2012', '2022']
TARGET_ITEMS = [15, 27, 56] # Wheat, Rice, Maize (FAO Codes)

def get_iso3(name):
    try:
        return pycountry.countries.search_fuzzy(name)[0].alpha_3
    except:
        return None


# PART 1: FAOSTAT (Production & Population)
def fetch_faostat():
    print(">>> [1/2] Fetching FAOSTAT Production & Population...")
    
    # 1. PRODUCTION
    prod_url = "https://fenixservices.fao.org/faostat/static/bulkdownloads/Production_Crops_Livestock_E_All_Data_(Normalized).zip"
    r = requests.get(prod_url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    df_prod = pd.read_csv(z.open(z.namelist()[0]), encoding='latin-1', 
                          usecols=['Area', 'Item Code', 'Item', 'Element', 'Year', 'Value'])
    
    df_prod = df_prod[
        (df_prod['Item Code'].isin(TARGET_ITEMS)) & 
        (df_prod['Element'] == 'Production') & 
        (df_prod['Year'].isin([int(y) for y in YEARS]))
    ]
    df_prod = df_prod.groupby(['Area', 'Year', 'Item'], as_index=False)['Value'].sum()
    df_prod.rename(columns={'Value': 'Production'}, inplace=True)

    # 2. POPULATION
    pop_url = "https://fenixservices.fao.org/faostat/static/bulkdownloads/Population_E_All_Data_(Normalized).zip"
    r = requests.get(pop_url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    df_pop = pd.read_csv(z.open(z.namelist()[0]), encoding='latin-1',
                         usecols=['Area', 'Element', 'Year', 'Value'])
    
    df_pop = df_pop[
        (df_pop['Element'] == 'Total Population - Both sexes') & 
        (df_pop['Year'].isin([int(y) for y in YEARS]))
    ]
    df_pop['Population'] = df_pop['Value'] * 1000 
    df_pop = df_pop[['Area', 'Year', 'Population']]

    # 3. MERGE & HARMONIZE
    print("    Harmonizing ISO codes...")
    unique_areas = set(df_prod['Area']) | set(df_pop['Area'])
    iso_map = {name: get_iso3(name) for name in unique_areas}
    
    df_prod['ISO3'] = df_prod['Area'].map(iso_map)
    df_pop['ISO3'] = df_pop['Area'].map(iso_map)
    
    df_master = pd.merge(df_prod, df_pop, on=['ISO3', 'Year'], how='inner')
    
    # Placeholders for columns
    df_master['Exports'] = 0
    df_master['Imports'] = 0
    df_master['Net_Food_Availability_Capita'] = (df_master['Production'] * 1000) / df_master['Population']
    
    # Save Master File
    df_master = df_master[['Area_x', 'Year', 'Item', 'Production', 'ISO3', 'Area_y', 'Population', 'Exports', 'Imports', 'Net_Food_Availability_Capita']]
    df_master.to_csv("1_Master_Dataset_Harmonized.csv", index=False)
    print("    Saved '1_Master_Dataset_Harmonized.csv'")
    
    return df_master


# PART 2: WITS (Raw Trade Flows)
def fetch_wits_flows(target_countries):
    print(f"\n>>> [2/2] Fetching WITS Trade Flows for {len(target_countries)} countries...")
    
    all_flows = []

    for year in YEARS:
        print(f"    Fetching Year: {year}...")
        
        # We loop through reporters to get their imports (Partner -> Reporter flow)
        # This is often more accurate than asking for exports
        for reporter in target_countries:
            try:
                # Indicator: Import Value (MPRT-TRD-VL)
                df = wits.get_indicator(
                    'MPRT-TRD-VL',
                    reporter=reporter,
                    partner='all',
                    year=year,
                    datasource='tradestats-trade'
                ).reset_index()
                
                for _, row in df.iterrows():
                    partner = row['Partner']
                    val = row['Value']
                    
                    if partner != 'World' and val > 0:
                        all_flows.append({
                            'year': int(year),
                            'target_iso': reporter,      # Importer
                            'source_name': partner,      # Exporter
                            'weight': val
                        })

            except Exception:
                continue
    
    df_flows = pd.DataFrame(all_flows)
    
    # Harmonize Source Names to ISO3 (WITS sometimes returns names for partners)
    print("    Harmonizing Partner ISO codes...")
    unique_partners = df_flows['source_name'].unique()
    partner_map = {}
    for p in unique_partners:
        if len(p) == 3: 
            partner_map[p] = p
        else:
            partner_map[p] = get_iso3(p)
            
    df_flows['source_iso'] = df_flows['source_name'].map(partner_map)
    df_flows.dropna(subset=['source_iso'], inplace=True)
    
    df_flows = df_flows[['year', 'source_iso', 'target_iso', 'weight']]
    df_flows.to_csv("raw_wits_trade_flows.csv", index=False)
    print("    Saved 'raw_wits_trade_flows.csv'")


master_df = fetch_faostat()
valid_isos = [c for c in master_df['ISO3'].unique() if c and len(c)==3]
fetch_wits_flows(valid_isos)