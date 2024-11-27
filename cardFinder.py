import json

# File paths
json_file_path = "price_data/combined_card_data.json"
wishlist_file_path = "price_data/wishlist.txt"

def main():
    # Load the JSON document
    try:
        with open(json_file_path, 'r') as json_file:
            card_data = json.load(json_file)
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: File '{json_file_path}' is not a valid JSON.")
        return

    # Read the wishlist
    try:
        with open(wishlist_file_path, 'r') as wishlist_file:
            wishlist = [line.strip() for line in wishlist_file if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{wishlist_file_path}' not found.")
        return

    # Find matches
    results = {}
    for card_id, details in card_data.items():
        if details["name"] in wishlist:
            results[card_id] = details["price"]

    # Print the results
    if results:
        print("Matching cards and prices:")
        for card_id, price in results.items():
            print(f"ID: {card_id}, Price: ${price:.2f}")
    else:
        print("No matches found in the wishlist.")

if __name__ == "__main__":
    main()
