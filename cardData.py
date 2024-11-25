import json
import os

# File paths
PRICE_FILE = "price_data/price-history-2024-11-23.txt"
DEFINITIONS_FILE = "price_data/card-definitions.txt"
OUTPUT_FILE = "price_data/combined_card_data.json"

# Load data from files
def load_json(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {file_path}: {e}")
            return None

# Combine the data
def combine_data(price_data, definition_data):
    combined_data = {}
    for card_id, price in price_data.items():
        card_id_str = str(card_id)  # Ensure IDs are consistent as strings
        if card_id_str in definition_data:
            combined_data[card_id_str] = {
                "price": price,
                **definition_data[card_id_str]  # Merge card definitions with price
            }
        else:
            print(f"Warning: Card ID {card_id_str} found in prices but not in definitions.")
    return combined_data

# Main script
if __name__ == "__main__":
    print("Loading data...")
    price_data = load_json(PRICE_FILE)
    definition_data = load_json(DEFINITIONS_FILE)

    if price_data is None or definition_data is None:
        print("Failed to load one or both files. Exiting.")
        exit()

    print("Combining data...")
    combined_data = combine_data(price_data, definition_data)

    print(f"Saving combined data to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, indent=4)

    print("Data combined and saved successfully!")
