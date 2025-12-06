# Install packages if missing: install.packages(c("igraph", "tidyverse"))
library(igraph)
library(tidyverse)

cat(">>> [1/3] Building Networks from WITS Data...\n")

flows <- read_csv("raw_wits_trade_flows.csv", show_col_types = FALSE)

centrality_list <- list()
years <- unique(flows$year)

for (yr in years) {
  cat(paste("    Processing Year:", yr, "\n"))
  
  yr_data <- flows %>%
    filter(year == yr) %>%
    select(source_iso, target_iso, weight)
  
  g <- graph_from_data_frame(yr_data, directed = TRUE)
  
  # Unweighted betweenness for trade topology analysis
  w_deg <- strength(g, mode = "all", weights = E(g)$weight)
  betw <- betweenness(g, directed = TRUE, weights = NA, normalized = TRUE)
  
  res <- data.frame(
    ISO3 = names(w_deg),
    Year = yr,
    Weighted_Degree = as.numeric(w_deg),
    Betweenness = as.numeric(betw)
  )
  centrality_list[[as.character(yr)]] <- res
}

df_network <- bind_rows(centrality_list)
write_csv(df_network, "2_Network_Centrality_Scores.csv")
cat("    Saved '2_Network_Centrality_Scores.csv'\n")

cat("\n>>> [2/3] Merging Master Data with Networks...\n")

df_master <- read_csv("1_Master_Dataset_Harmonized.csv", show_col_types = FALSE)

df_reg <- df_master %>%
  left_join(df_network, by = c("ISO3", "Year")) %>%
  mutate(
    Weighted_Degree = replace_na(Weighted_Degree, 0),
    Betweenness = replace_na(Betweenness, 0)
  )

# Sum imports (target) and exports (source) from trade flows
wits_stats <- flows %>%
  group_by(year, iso = source_iso) %>% summarize(Exp_Val = sum(weight), .groups='drop') %>%
  full_join(
    flows %>% group_by(year, iso = target_iso) %>% summarize(Imp_Val = sum(weight), .groups='drop'),
    by = c("year", "iso")
  )

df_reg <- df_reg %>%
  left_join(wits_stats, by = c("Year" = "year", "ISO3" = "iso")) %>%
  mutate(
    Exports = replace_na(Exp_Val, 0),
    Imports = replace_na(Imp_Val, 0)
  ) %>%
  select(-Exp_Val, -Imp_Val)

write_csv(df_reg, "3_Regression_Analysis_Data.csv")
cat("    Saved '3_Regression_Analysis_Data.csv'\n")

cat("\n>>> [3/3] Running 'Tipping Point' Collapse Simulation...\n")

flows <- read_csv("raw_wits_trade_flows.csv", show_col_types = FALSE)

ZONE_AMOC_COLD <- c(
  "GBR", "IRL", "ISL", "NOR", "SWE", "FIN", "DNK",  
  "DEU", "FRA", "NLD", "BEL", "LUX", "CHE", "AUT",  
  "POL", "CZE", "SVK", "HUN", "EST", "LVA", "LTU",  
  "CAN", "USA"
)

ZONE_MONSOON_FAIL <- c(
  "IND", "PAK", 
  "NGA", "NER", "MLI", "SEN", "GHA", "CIV"
)

ZONE_AMAZON_DRY <- c(
  "BRA", "ARG", "PRY", "URY", "BOL", "PER", "COL"
)

SHOCK_COUNTRIES <- unique(c(ZONE_AMOC_COLD, ZONE_MONSOON_FAIL, ZONE_AMAZON_DRY))

SHOCK_MAGNITUDE <- 0.60
TARGET_YEAR     <- 2022

cat(paste("    Simulating Tipping Point impacts on", length(SHOCK_COUNTRIES), "nations...\n"))

flows_2022 <- flows %>% filter(year == TARGET_YEAR)

# Reduce exports from shock zones by magnitude
shocked_flows <- flows_2022 %>%
  mutate(
    weight_shocked = if_else(source_iso %in% SHOCK_COUNTRIES, 
                             weight * (1 - SHOCK_MAGNITUDE), 
                             weight)
  )

country_imports_shocked <- shocked_flows %>%
  group_by(target_iso) %>%
  summarise(
    Imports_Original = sum(weight, na.rm=TRUE),
    Imports_Shocked = sum(weight_shocked, na.rm=TRUE),
    .groups = 'drop'
  )

baseline <- df_reg %>% 
  filter(Year == TARGET_YEAR) %>%
  select(-Imports, -Exports) %>%
  left_join(country_imports_shocked, by = c("ISO3" = "target_iso")) %>%
  mutate(
    Imports_Original = replace_na(Imports_Original, 0),
    Imports_Shocked  = replace_na(Imports_Shocked, 0)
  )

baseline <- baseline %>%
  mutate(
    Production_Shocked = if_else(ISO3 %in% SHOCK_COUNTRIES, 
                                 Production * (1 - SHOCK_MAGNITUDE), 
                                 Production),
    Exports_Shocked = if_else(ISO3 %in% SHOCK_COUNTRIES, 0, 0), 
    Availability_Baseline = ((Production + Imports_Original) * 1000) / Population,
    Availability_After_Shock = ((Production_Shocked + Imports_Shocked) * 1000) / Population,
    Deficit_kg_per_capita = Availability_After_Shock - Availability_Baseline,
    Percent_Drop = if_else(Availability_Baseline == 0, 0, 
                           Deficit_kg_per_capita / Availability_Baseline)
  )

# Severity thresholds: -5% manageable, -30% catastrophic
phase3 <- baseline %>%
  mutate(Severity = case_when(
    Percent_Drop >= -0.05 ~ "Low",        
    Percent_Drop < -0.05 & Percent_Drop >= -0.15 ~ "Medium", 
    Percent_Drop < -0.15 & Percent_Drop >= -0.30 ~ "High",   
    Percent_Drop < -0.30 ~ "Critical",    
    TRUE ~ "Low"
  )) %>%
  select(ISO3, Production, Imports_Original, Imports_Shocked, Population, 
         Availability_Baseline, Availability_After_Shock, Percent_Drop, Severity)

write_csv(phase3, "5_Phase3_Lifeboat_Collapse.csv")
cat("    Saved '5_Phase3_Lifeboat_Collapse.csv'\n")
cat("\n>>> ANALYSIS COMPLETE.\n")
