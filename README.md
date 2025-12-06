# Temporal Analysis of Food Networks

A comprehensive analysis of global food trade networks and climate tipping points, examining how network centrality correlates with food security and simulating the cascading impacts of major climate disruptions.

## Repository Structure

```
network-science/
├── code/
│   ├── data_acquisition.py          # Fetch raw data from FAOSTAT & WITS (OPTIONAL)
│   ├── network_analysis.R            # Build networks & run simulations
│   ├── visualize_research_questions.py # Generate research visualizations
│   └── visualize_tipping_points.py   # Generate climate impact map
├── data/
│   ├── 1_Master_Dataset_Harmonized.csv       # Production & population data
│   ├── 2_Network_Centrality_Scores.csv       # Weighted degree & betweenness
│   ├── 3_Regression_Analysis_Data.csv        # Network + food security merged
│   ├── 4_Simulation_Baseline_2022.csv        # Baseline scenario data
│   └── 5_Phase3_Lifeboat_Collapse.csv        # Tipping point simulation results
└── README.md
```

## Execution Order

### Option 1: Use Pre-processed Data (Recommended)

If data files already exist in the `data/` folder, skip data acquisition and proceed directly:

```bash
# Step 1: Build networks and run tipping point simulation
Rscript code/network_analysis.R

# Step 2: Generate research question visualizations
python code/visualize_research_questions.py

# Step 3: Generate climate tipping point map
python code/visualize_tipping_points.py
```

### Option 2: Acquire Raw Data (Optional)

If you need to fetch fresh data from external APIs:

```bash
# Step 1: Fetch data from FAOSTAT & WITS APIs (creates data CSVs)
python code/data_acquisition.py

# Step 2: Build networks and run tipping point simulation
Rscript code/network_analysis.R

# Step 3: Generate research question visualizations
python code/visualize_research_questions.py

# Step 4: Generate climate tipping point map
python code/visualize_tipping_points.py
```

## Script Details

### data_acquisition.py (Optional)

**Purpose**: Fetches raw data from FAO and World Bank WITS databases

- Retrieves FAOSTAT production & population data (1992-2022)
- Downloads WITS trade flow data for selected countries
- Harmonizes country codes to ISO-3 format
- **Output**: `raw_wits_trade_flows.csv` and input CSV for network_analysis.R

**Note**: Requires internet connection and external API access. Skip if data is already available.

---

### network_analysis.R

**Purpose**: Core analysis pipeline with three phases

1. **Phase 1 - Network Science**: Builds directed trade networks, calculates weighted degree and betweenness centrality
2. **Phase 2 - Data Merging**: Integrates network metrics with food security indicators
3. **Phase 3 - Tipping Point Simulation**: Models cascade effects of climate disruptions on global food availability

**Outputs**:

- `2_Network_Centrality_Scores.csv`
- `3_Regression_Analysis_Data.csv`
- `5_Phase3_Lifeboat_Collapse.csv`

---

### visualize_research_questions.py

**Purpose**: Generates three publication-ready visualizations

1. **RQ1_Network_Evolution.png**: Global food trade volume trends (1992-2022)
2. **RQ2_Regression_Analysis.png**: Trade power vs. food security correlation (2022)
3. **RQ3_Simulation_Map.png**: Geographic impact of hypothetical Russia/Ukraine export shock

---

### visualize_tipping_points.py

**Purpose**: Maps three climate tipping point zones with synchronized crop failures

**Zones**:

- **AMOC Collapse (Blue)**: Northern Europe + North America (severe cooling)
- **Monsoon Failure (Orange)**: West Africa + South Asia (severe drought)
- **Amazon Dieback (Red)**: South America (savannification)

**Output**: `Map_Tipping_Point_Zones.png`

---

## Dependencies

### Python

- `pandas` - Data manipulation
- `matplotlib`, `seaborn` - Visualization
- `cartopy` - Geospatial mapping

### R

- `igraph` - Network analysis
- `tidyverse` - Data wrangling (dplyr, readr)

### External APIs (Optional)

- FAOSTAT (Food production & population)
- WITS (World trade flows)
