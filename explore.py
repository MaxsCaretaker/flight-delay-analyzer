import pandas as pd

# Load only the columns we need
cols = [
    "FlightDate", "IATA_Code_Marketing_Airline", "Origin", "Dest",
    "DepDelay", "ArrDelay", "Cancelled",
    "CarrierDelay", "WeatherDelay", "NASDelay"
]

df = pd.read_csv("flights.csv", usecols=cols, low_memory=False)

# Rename for convenience
df.columns = ["date", "airline", "origin", "dest",
              "dep_delay", "arr_delay", "cancelled",
              "carrier_delay", "weather_delay", "nas_delay"]

# Quick look
print(f"Total flights: {len(df)}")
print(f"Airlines: {df['airline'].unique()}")
print(f"Sample data:")
print(df.head())

# Save cleaned version
df.to_csv("flights_clean.csv", index=False)
print("\nSaved to flights_clean.csv!")