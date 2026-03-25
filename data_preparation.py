# =========================
# TASK 2: DATA PREPARATION (ADVANCED CLEANING)
# =========================

import pandas as pd
import numpy as np

# -------------------------
# 1. LOAD DATA
# -------------------------
df = pd.read_csv("Climate Change Impact on Agriculture.csv")

print("Initial Data Shape:", df.shape)

# -------------------------
# 2. CLEAN COLUMN NAMES
# -------------------------
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# -------------------------
# 3. FIX TEXT ISSUES (SPACES)
# -------------------------
# Remove extra spaces in all text columns
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].str.strip()

# -------------------------
# 4. HANDLE "N/A" VALUES
# -------------------------
# Replace "N/A" with actual NaN
df.replace("N/A", np.nan, inplace=True)

# -------------------------
# 5. FIX DATA TYPES
# -------------------------
# Convert numeric columns (some contain "N/A")
numeric_cols = [
    'average_temperature_c',
    'total_precipitation_mm',
    'co2_emissions_mt',
    'crop_yield_mt_per_ha',
    'extreme_weather_events',
    'irrigation_access_%',
    'pesticide_use_kg_per_ha',
    'fertilizer_use_kg_per_ha',
    'soil_health_index',
    'economic_impact_million_usd'
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# -------------------------
# 6. CHECK MISSING VALUES
# -------------------------
print("\nMissing Values Before Cleaning:")
print(df.isnull().sum())

# -------------------------
# 7. HANDLE MISSING VALUES
# -------------------------
# Numerical → median
for col in numeric_cols:
    df[col] = df[col].fillna(df[col].median())

# Categorical → mode
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].fillna(df[col].mode()[0])

# -------------------------
# 8. REMOVE DUPLICATES
# -------------------------
before = df.shape[0]
df.drop_duplicates(inplace=True)
after = df.shape[0]

print(f"\nDuplicates Removed: {before - after}")

# -------------------------
# 9. OUTLIER TREATMENT (IQR METHOD)
# -------------------------
for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    df[col] = np.where(df[col] < lower, lower, df[col])
    df[col] = np.where(df[col] > upper, upper, df[col])

# -------------------------
# 10. STANDARDIZE CATEGORIES
# -------------------------
df['region'] = df['region'].str.title()
df['crop_type'] = df['crop_type'].str.title()
df['country'] = df['country'].str.title()

# -------------------------
# 11. FEATURE ENGINEERING
# -------------------------
df['climate_stress_index'] = (
    df['average_temperature_c'] * 0.3 +
    df['total_precipitation_mm'] * 0.2 +
    df['co2_emissions_mt'] * 0.3 +
    df['extreme_weather_events'] * 0.2
)

df['yield_per_input'] = df['crop_yield_mt_per_ha'] / (
    df['fertilizer_use_kg_per_ha'] +
    df['pesticide_use_kg_per_ha'] + 1
)

# -------------------------
# 12. NORMALIZATION
# -------------------------
for col in numeric_cols:
    df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

# -------------------------
# 12. DATETIME CONVERSION
# -------------------------
# Remove spaces
df['year'] = df['year'].astype(str).str.strip()

# Replace invalid values
df['year'] = df['year'].replace("N/A", np.nan)

# Convert to numeric
df['year'] = pd.to_numeric(df['year'], errors='coerce')

# Fill missing with median
df['year'] = df['year'].fillna(df['year'].median())

# Convert to integer
df['year'] = df['year'].astype(int)

# -------------------------
# 10.5 SORT DATA (IMPORTANT FOR TIME SERIES)
# -------------------------
df = df.sort_values(by='year')

# -------------------------
# TIME FEATURES (NEW)
# -------------------------
df['year_group'] = pd.cut(
    df['year'],
    bins=[1999, 2005, 2010, 2015, 2020, 2025],
    labels=['2000-05','2006-10','2011-15','2016-20','2021-25']
)
# -------------------------
# 13. VALIDATION CHECKS
# -------------------------
assert (df['crop_yield_mt_per_ha'] >= 0).all()
assert (df['co2_emissions_mt'] >= 0).all()

# -------------------------
# 14. DATA AGGREGATION
# -------------------------
# Yield trend with more insights
yield_trend = df.groupby('year').agg({
    'crop_yield_mt_per_ha': ['mean', 'min', 'max'],
    'climate_stress_index': 'mean'
}).reset_index()

# Flatten column names
yield_trend.columns = ['year', 'yield_mean', 'yield_min', 'yield_max', 'stress_mean']

yield_trend = yield_trend.sort_values(by='year')

# -------------------------
# 15. SAVE CLEAN DATA
# -------------------------
# Capitalize column names
df.columns = df.columns.str.title()

df.to_csv("cleaned_data.csv", index=False)

print("\nFinal Data Shape:", df.shape)
print("Cleaned data saved as 'cleaned_data.csv'")