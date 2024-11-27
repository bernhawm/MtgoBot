import pyautogui
import time
import pytesseract
from PIL import Image
from loguru import logger
import os
import json

# File paths
json_file_path = "price_data/combined_card_data.json"

logger.add("trade_bot.log", rotation="1 MB")


IMAGE_FOLDER = "during_trade_images"


QuantityButton = os.path.join(IMAGE_FOLDER, "QuantityButton.png")
selectionBox = os.path.join(IMAGE_FOLDER, "selectionBox.png")
youRec = os.path.join(IMAGE_FOLDER, "youRec.png")


# Function to wait for an image on the screen
def wait_for_image(image_path, confidence=0.8, timeout=None):
    start_time = time.time()
    while True:
        button_location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if button_location:
            return button_location
        if timeout and (time.time() - start_time) > timeout:
            logger.error(f"Timeout waiting for {image_path}")
            return None
        time.sleep(0.5)  # Avoid excessive CPU usage

# Function to capture a screenshot around a region
def capture_region_around(location, margin=50, save_path="region.png"):
    x = max(0, int(location.left - margin))  # Ensure coordinates are integers
    y = max(0, int(location.top - margin))
    width = int(location.width + 2 * margin)
    height = int(location.height + 2 * margin)

    region = (x, y, width, height)
    screenshot = pyautogui.screenshot(region=region)
    screenshot.save(save_path)
    logger.info(f"Captured region saved as {save_path}")
    return screenshot

### screencapture and pricing functions 
def capture_screen(region=None):
    """Capture a portion of the screen."""
    logger.info("Capturing the screen...")
    screenshot = pyautogui.screenshot(region=region)
    screenshot.save("screen_capture.png")
    logger.info("Screenshot saved as 'screen_capture.png'")
    return screenshot

def extract_text_from_image(image):
    """Extract text from an image using pytesseract."""
    logger.info("Extracting text from image...")
    text = pytesseract.image_to_string(image)
    logger.info("Text extraction completed.")
    return text

def parse_card_data_from_text(text):
    """Parse card data (Name and SET) from the extracted text."""
    logger.info("Parsing card data from text...")
    lines = text.splitlines()
    card_data = []

    start_parsing = False
    for line in lines:
        if start_parsing:
            parts = line.split()
            if len(parts) >= 3:
                name = " ".join(parts[1:-1])  # Name is everything between QTY and SET
                set_name = parts[-1]         # SET is the last part
                card_data.append({"name": name, "set": set_name})
        elif "QTY" in line and "Name" in line and "SET" in line:
            start_parsing = True  # Start parsing after finding the header row

    logger.info(f"Parsed card data: {card_data}")
    return card_data

def compare_cards_with_json(card_data, json_file_path):
    """Compare parsed card data with combined_card_data.json."""
    logger.info("Loading card data from JSON...")
    try:
        with open(json_file_path, 'r') as json_file:
            json_data = json.load(json_file)
    except FileNotFoundError:
        logger.error(f"Error: File '{json_file_path}' not found.")
        return []
    except json.JSONDecodeError:
        logger.error(f"Error: File '{json_file_path}' is not a valid JSON.")
        return []

    results = []
    for card in card_data:
        for card_id, details in json_data.items():
            if card["name"] == details["name"] and card["set"] == details["cardset"]:
                results.append({"id": card_id, "price": details["price"], "name": card["name"], "set": card["set"]})
                break

    logger.info(f"Comparison results: {results}")
    return results

# Step 1: Wait for a trade offer
logger.info("Selecting Quantity Button")
QuantityButton = wait_for_image(QuantityButton, confidence=0.75, timeout=None)
if QuantityButton:
    logger.info("Quantity button detected!")
    # Snip the region around the trade button
    # capture_region_around(QuantityButton, margin=10, save_path="trade_images/trade_screen.png")
    pyautogui.click(QuantityButton)
    logger.info("Selecting wishlist choice!")
    selectionBox = wait_for_image(selectionBox, confidence=0.85, timeout=None)
    if selectionBox:
        pyautogui.click(selectionBox)

    else:
        logger.info("Box Couldnt be selected!")



else:
    logger.error("Trade button not found. Exiting bot.")
    exit()

region = pyautogui.locateOnScreen(youRec)  # Image of the header row
if region:
    print(f"Region found at: {region}")
    x, y, width, height = region
    capture_region = (x, y, width, 400)  # Adjust height as needed


 # Extract text
    text = extract_text_from_image(capture_region)
    
    # Parse card data
    card_data = parse_card_data_from_text(text)
    
    # Compare with JSON
    results = compare_cards_with_json(card_data, json_file_path)
    
    # Display results
    if results:
        print("Matching cards and prices:")
        for result in results:
            print(f"ID: {result['id']}, Name: {result['name']}, SET: {result['set']}, Price: ${result['price']:.2f}")
    else:
        print("No matches found.")