import pyautogui
import time
import pytesseract
from PIL import Image
from loguru import logger
import os

logger.add("trade_bot.log", rotation="1 MB")

# Define paths to images for the trade button and confirm button
IMAGE_FOLDER = "trade_images"

# TRADE_BUTTON_IMAGE = "trade_request.png"
# TRADE_BUTTON_IMAGE = "newtraderequest.png"
# CONFIRM_BUTTON_IMAGE = "accept_button.png"
TRADE_BUTTON_IMAGE = os.path.join(IMAGE_FOLDER, "newtraderequest.png")
CONFIRM_BUTTON_IMAGE = os.path.join(IMAGE_FOLDER, "accept_button.png")
# LOGIN_BUTTON_IMAGE = os.path.join(IMAGE_FOLDER, "login_button.png")

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

# Function to capture and extract username from the trade screen
def return_username(screenshot):

    
    # Use pytesseract to extract text from the image
    extracted_text = pytesseract.image_to_string(screenshot)
    logger.info(f"Extracted text: {extracted_text}")  # Log the full extracted text for debugging
# print(extracted_text)

    # Extract username (this assumes the username is right after "to" in the text)
    if " HAS SENT YOU A TRADE REQUEST." in extracted_text:
        # username = extracted_text.split("to")[-1].strip()
        username = extracted_text.split(" HAS SENT YOU A TRADE REQUEST.")[0].strip()
        logger.info(f"Username is: {username}")  # Log the full extracted text for debugging

        return username
    else:
        logger.error("Extracted text does not contain the expected format.")
        return None



# Step 1: Wait for a trade offer
logger.info("Waiting for a trade offer...")
trade_button = wait_for_image(TRADE_BUTTON_IMAGE, confidence=0.75, timeout=None)
if trade_button:
    logger.info("Trade button detected!")
    # Snip the region around the trade button
    capture_region_around(trade_button, margin=10, save_path="trade_images/trade_screen.png")
    return_username(screenshot="trade_images/trade_screen.png",)
    pyautogui.click(trade_button)
else:
    logger.error("Trade button not found. Exiting bot.")
    exit()

# # Step 2: Read the username of the trader
# logger.info("Reading the username of the trade offer...")
# screenshot_region = (
#     int(trade_button.left) - 100,
#     int(trade_button.top) - 50,
#     200,
#     50
# )
# username_image = pyautogui.screenshot(region=screenshot_region)
# username_image.save("name_section.png")  # Optional: Save for debugging
# username_text = pytesseract.image_to_string(username_image)

# if username_text.strip():
#     logger.info(f"Trade offer from user: {username_text.strip()}")
# else:
#     logger.warning("Unable to read the username from the trade offer.")

# Step 3: Confirm the trade
logger.info("Attempting to confirm the trade...")
confirm_button = wait_for_image(CONFIRM_BUTTON_IMAGE, confidence=0.95, timeout=10)
if confirm_button:
    logger.info("Confirm button detected!")
    # Snip the region around the confirm button
    capture_region_around(confirm_button, margin=50, save_path="trade_images/confirm_screen.png")
    pyautogui.click(confirm_button)
    logger.info("Trade confirmed!")
else:
    logger.error("Confirm button not found within the timeout!")
