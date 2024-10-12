import pandas as pd
import numpy as np
import warnings

warnings.simplefilter("ignore")

df = pd.read_csv('C:/Users/tomwr/Datascience/data_visualization/national_water_plan/national_water_plan.csv')


# Site name
df["Site name"] = df["Site name"].fillna("Unknown Site Name", inplace=False)
df.replace({"Site name":
           {"TBC": "Unknown Site Name",
                   "Not Matched in Consents Database": "Unknown Site Name"}},
           inplace=True)

# Bathing Water Discharge Flag
df["Bathing Water Discharge Flag"] = df["Bathing Water Discharge Flag"].fillna("N")
df["Bathing Water Discharge Flag"].replace({"N": "No",
                                            "Y": "Yes"},
                                           inplace=True)
# Shellfish Water Discharge Flag
df["Shellfish Water Discharge Flag"] = df["Shellfish Water Discharge Flag"].fillna("N")
df["Shellfish Water Discharge Flag"].replace({"N": "No",
                                              "Y": "Yes"},
                                             inplace=True)
# Ecological High Priority Site Flag
df["Ecological High Priority Site Flag"] = df["Ecological High Priority Site Flag"].fillna("N")
df["Ecological High Priority Site Flag"].replace({"N": "No",
                                                  "Y": "Yes"},
                                                 inplace=True)

# Non-bathing Priority Site Flag
df["Non-bathing Priority Site Flag"].fillna("N", inplace=True)
df["Non-bathing Priority Site Flag"].replace({"N": "No",
                                              "Y": "Yes"},
                                             inplace=True)
# Spill Events 2020, 2021, 2022
df["Spill Events 2020"].fillna(0, inplace=True)
df["Spill Events 2021"].fillna(0, inplace=True)
df["Spill Events 2022"].fillna(0, inplace=True)

# Spill Improvement Date Planned
df["Spill Improvement Date Planned"].fillna(2040, inplace=True)  # This is most common after 2023

# Rainfall Improvement Target Delivery Flag
df["Rainfall Improvement Target Delivery Flag"].fillna("N", inplace=True)  # Assume No
df["Rainfall Improvement Target Delivery Flag"].replace({"N": "No",
                                                         "Y": "Yes",
                                                         "UNK": "No"},
                                                        inplace=True)


# Improvements List
df["Improvements List"].fillna("No planned improvements", inplace=True)

improvement_list = ["Storage", "Mew screen", "Other improvements to be confirmed",
                    "Nature-Based", "Increased pass forward flow", "Bespoke solution",
                    "Sealing of sewers", "Operational", "Smart sewers", "Spill treatment"]

# Initialize all improvement columns with 0
for improvement in improvement_list:
    df[improvement] = 0

# Iterate through each row and check for improvements
for index, row in df.iterrows():
    for improvement in improvement_list:
        if improvement in row["Improvements List"]:
            df.at[index, improvement] = 1

# Predicted Annual Spill Frequence Post Scheme
df['Predicted Annual Spill Frequence Post Scheme'].fillna(round(np.nanmedian(df['Predicted Annual Spill Frequence Post Scheme'])),
                                                          inplace=True)
df.rename(columns={'Predicted Annual Spill Frequence Post Scheme': 'Predicted Annual Spill Frequency Post Scheme'},
          inplace=True)

# Baseline
df["Baseline"].fillna(0.0, inplace=True)  # Most common value.

# Baseline Less than Target --> Baseline Less than Target Flag
baseline_target_conditions = [(df["Baseline"] <= df["Predicted Annual Spill Frequency Post Scheme"]),
                              (df["Baseline"] > df["Predicted Annual Spill Frequency Post Scheme"])]
df["Baseline Less than Target Flag"] = np.select(baseline_target_conditions, ["Yes", "No"], default="No")
df.drop(columns=["Baseline Less Than Target"], inplace=True)

# Remove Requires No Improvement column as redundant
df.drop(columns=["Requires No Improvement"], inplace=True)

# Projected Spills 2025,2030,2035,2040,2045,2050
df["2025 Projected Spills"].fillna(np.nanmedian(df["2025 Projected Spills"]), inplace=True)
df["2030 Projected Spills"].fillna(np.nanmedian(df["2030 Projected Spills"]), inplace=True)
df["2035 Projected Spills"].fillna(np.nanmedian(df["2035 Projected Spills"]), inplace=True)
df["2040 Projected Spills"].fillna(np.nanmedian(df["2040 Projected Spills"]), inplace=True)
df["2045 Projected Spills"].fillna(np.nanmedian(df["2045 Projected Spills"]), inplace=True)
df["2050 Projected Spills"].fillna(np.nanmedian(df["2050 Projected Spills"]), inplace=True)

df.drop(columns=["Improvements List"], inplace=True)

df["Average Spill Count"] = (df["Spill Events 2020"] + df["Spill Events 2021"] + df["Spill Events 2022"])/3
df["All Spill Events"] = df["Spill Events 2020"] + df["Spill Events 2021"] + df["Spill Events 2022"]

# Create a column that is a row-wise sum of column 35 (Storage) to 44 (Spill treatment)
df["Improvement Count Needed"] = df["Storage"] + df["Mew screen"] + df["Other improvements to be confirmed"] + \
                                 df["Nature-Based"] + df["Increased pass forward flow"] + df["Bespoke solution"] + \
                                 df["Sealing of sewers"] + df["Operational"] + df["Smart sewers"] + df["Spill treatment"]
# Set 'All' column to 'Yes
df["All"] = "Yes"

# Write out to Local PC
df.to_csv('C:/Users/tomwr/Datascience/Datasets/Tabular/national_water_plan/national_water_plan.csv', index=False)
