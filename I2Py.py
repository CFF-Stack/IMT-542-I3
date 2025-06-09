import csv
from collections import defaultdict
from typing import List, Dict
import os
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime


# 🚀 Class for Integrated Data
class IntegratedData:
    def __init__(self, state_code, state_name, population):
        self.state_code = state_code
        self.state_name = state_name
        self.population = population
        self.disaster_declarations = []
        self.source_data = {"census": {}, "fema": []}

    def add_disaster(self, disaster):
        self.disaster_declarations.append(disaster)


# 🚀 Function to transform Census data
def transform_census_data(census_csv_path: str) -> Dict[str, Dict]:
    census_data = {}
    with open(census_csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        headers = next(reader)
        for state_name, population_str in list(headers.items())[1:]:
            state_name = state_name.strip().replace('"', '').replace('\ufeff', '')
            population = int(population_str.replace(",", "")) if population_str else 0
            census_data[state_name] = {
                "state_name": state_name,
                "population": population,
                "source_row": {"state_name": state_name, "population": population}
            }
    print("✅ Census data loaded for states:", list(census_data.keys())[:10])
    return census_data


# 🚀 Function to transform FEMA data
def transform_fema_data(fema_csv_path: str) -> Dict[str, List[Dict]]:
    fema_data = defaultdict(list)
    with open(fema_csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            state_code = row.get("stateCode", "").strip()
            disaster = {
                "disaster_number": int(row.get("disasterNumber", "0")),
                "declaration_title": row.get("declarationTitle", "").strip(),
                "incident_type": row.get("incidentType", "").strip(),
                "declaration_date": row.get("declarationDate", "").strip(),
                "incident_begin_date": row.get("incidentBeginDate", "").strip(),
            }
            fema_data[state_code].append(disaster)
    print("✅ FEMA data loaded for states:", list(fema_data.keys())[:10])
    return fema_data


# 🚀 Function to integrate data
def integrate_data(census_data: Dict[str, Dict], fema_data: Dict[str, List[Dict]]) -> List[IntegratedData]:
    STATE_CODE_TO_NAME = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
        "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
        "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
        "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
        "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
        "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
        "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
        "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
        "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
        "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
        "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
        "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
        "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "PR": "Puerto Rico"
    }

    integrated_records = []
    for state_code, disasters in fema_data.items():
        state_name = STATE_CODE_TO_NAME.get(state_code)
        if not state_name:
            continue
        census_info = census_data.get(state_name)
        if not census_info:
            continue

        record = IntegratedData(state_code, state_name, census_info["population"])
        record.source_data["census"] = census_info["source_row"]
        record.source_data["fema"] = disasters
        for disaster in disasters:
            record.add_disaster(disaster)
        integrated_records.append(record)

    print(f"✅ Integrated dataset length: {len(integrated_records)}")
    return integrated_records


# 🚀 Function to visualize, save image and CSV output with timestamp
def visualize_integrated_data(integrated_dataset, output_dir="Sample Outputs"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Filenames for paired outputs
    output_image = f"Population_and_Disaster_Declarations_{timestamp}.png"
    output_csv = f"Population_and_Disaster_Declarations_{timestamp}.csv"

    image_path = os.path.join(output_dir, output_image)
    csv_path = os.path.join(output_dir, output_csv)

    states, populations, disaster_counts = [], [], []
    for record in integrated_dataset:
        if record.state_name and record.population > 0:
            states.append(record.state_name)
            populations.append(record.population)
            disaster_counts.append(len(record.disaster_declarations))

    if not states:
        print("⚠️ No data to visualize. Check your datasets.")
        return

    # Create DataFrame
    df = pd.DataFrame({
        "State": states,
        "Population": populations,
        "Disaster Declarations": disaster_counts
    }).sort_values("Population", ascending=False)

    # Save as CSV
    df.to_csv(csv_path, index=False)
    print(f"✅ Data saved to CSV: {csv_path}")

    # Create visualization
    fig, ax1 = plt.subplots(figsize=(15, 8))
    ax1.bar(df["State"], df["Population"], color='skyblue', alpha=0.7, label="Population")
    ax1.set_xlabel("State")
    ax1.set_ylabel("Population", color="blue")
    ax1.tick_params(axis='y', labelcolor="blue")
    ax1.set_xticks(range(len(df["State"])))
    ax1.set_xticklabels(df["State"], rotation=90, fontsize=8)

    ax2 = ax1.twinx()
    ax2.plot(df["State"], df["Disaster Declarations"], color="red", marker="o", label="Disaster Declarations")
    ax2.set_ylabel("Number of Disasters", color="red")
    ax2.tick_params(axis='y', labelcolor="red")

    plt.title("Population and Disaster Declarations by State (All States/Territories Included)")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(image_path, dpi=300)
    print(f"✅ Visualization saved to {image_path}")
    plt.show()


# 🚀 Main block: one script to rule them all!
if __name__ == "__main__":
    census_csv = "DECENNIALCD1182020.P1-2025-06-08T162550.csv"
    fema_csv = "FemaWebDisasterDeclarations.csv"

    census_data = transform_census_data(census_csv)
    fema_data = transform_fema_data(fema_csv)
    integrated_dataset = integrate_data(census_data, fema_data)

    for record in integrated_dataset[:5]:
        print(f"State: {record.state_name} | Population: {record.population} | Disasters: {len(record.disaster_declarations)}")

    visualize_integrated_data(integrated_dataset, output_dir="Sample Outputs")
