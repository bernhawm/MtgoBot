import pyautogui
import time
from loguru import logger
from dotenv import load_dotenv
import os
import pytesseract

load_dotenv()

# Set up logging
logger.add("login_bot.log", rotation="1 MB")

# Paths to reference images for username field, password field, and login button
IMAGE_FOLDER = "login_images"
USERNAME_FIELD_IMAGE = os.path.join(IMAGE_FOLDER, "username_field.png")
PASSWORD_FIELD_IMAGE = os.path.join(IMAGE_FOLDER, "password_field.png")
LOGIN_BUTTON_IMAGE = os.path.join(IMAGE_FOLDER, "login_button.png")

# Credentials loaded from .env
USERNAME = os.getenv("USERNAME1")
PASSWORD = os.getenv("PASSWORD")

# Function to wait for an image on the screen
def wait_for_image(image_path, confidence=0.95, timeout=10):
    start_time = time.time()
    while True:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            return location
        if time.time() - start_time > timeout:
            logger.error(f"Timeout waiting for {image_path}")
            return None
        time.sleep(0.5)

# Function to click on an image on the screen
def click_on_image(image_path, confidence=0.95, timeout=10):
    location = wait_for_image(image_path, confidence, timeout)
    if location:
        pyautogui.click(location)
        logger.info(f"Clicked on {image_path}")
        return True
    logger.error(f"Failed to locate {image_path}")
    return False

# Function to type into a field
# def type_into_field(image_path, text, confidence=0.95, timeout=10):
#     location = wait_for_image(image_path, confidence, timeout)
#     if location:
#         pyautogui.click(location)
#         pyautogui.write(text, interval=0.1)  # Changed to write instead of typewrite
#         time.sleep(0.5)  # Add delay to ensure typing is complete
#         logger.info(f"Entered text into field located at {image_path}")
#         return True
#     logger.error(f"Failed to locate field for {image_path}")
#     return False

def type_into_field(image_path, text, confidence=0.95, timeout=10, validate_existing=False):
    location = wait_for_image(image_path, confidence, timeout)
    if location:
        pyautogui.click(location)
        if validate_existing:
            try:
                # Take a screenshot of the field to extract existing text
                region = (location.left, location.top, location.width, location.height)
                field_screenshot = pyautogui.screenshot(region=region)
                extracted_text = pytesseract.image_to_string(field_screenshot).strip()
                
                logger.info(f"Existing text detected: {extracted_text}")
                
                if extracted_text == text:
                    logger.info(f"Field already contains the correct username: {text}")
                    return True  # Skip typing as the username is already correct
                
                # Clear the field if text is incorrect
                pyautogui.hotkey("ctrl", "a")  # Select all
                pyautogui.press("backspace")   # Delete selected text
                logger.info("Cleared the field for typing new text.")
            except:
                logger.info("failed if_validate_existing")
                return None


        
        # Type the correct text
        pyautogui.write(text, interval=0.1)
        time.sleep(0.5)  # Ensure typing is complete
        logger.info(f"Entered text into field located at {image_path}")
        return True
    logger.error(f"Failed to locate field for {image_path}")
    return False

# Main script
logger.info("Starting login bot...")

# Step 1: Enter username
if USERNAME:
    try:
        # First attempt with the primary username field image
        if type_into_field(USERNAME_FIELD_IMAGE, USERNAME, validate_existing=True):
            logger.info("Username entered successfully on the first attempt.")
        else:
            raise Exception("First attempt failed.")  # Trigger retry logic
    except Exception as e1:
        logger.warning(f"First attempt failed: {e1}. Retrying with a different image...")
        try:
            # Retry with an alternative image
            ALTERNATIVE_USERNAME_FIELD_IMAGE = os.path.join(IMAGE_FOLDER, "username_field1.png")
            if type_into_field(ALTERNATIVE_USERNAME_FIELD_IMAGE, USERNAME, validate_existing=True):
                logger.info("Username entered successfully on the second attempt.")
            else:
                raise Exception("Second attempt also failed.")
        except Exception as e2:
            logger.error(f"Both attempts to enter the username failed: {e2}. Exiting.")
            # exit()
else:
    logger.error("Username not found in .env file. Exiting.")
    exit()

# Step 2: Enter password
if PASSWORD:
    if type_into_field(PASSWORD_FIELD_IMAGE, PASSWORD):
        logger.info("Password entered successfully.")
    else:
        logger.error("Failed to enter password. Exiting.")
        exit()
else:
    logger.error("Password not found in .env file. Exiting.")
    exit()

# Step 3: Click the login button
if click_on_image(LOGIN_BUTTON_IMAGE):
    logger.info("Login button clicked successfully.")
else:
    logger.error("Failed to click login button. Exiting.")
    exit()

logger.info("Login process completed.")
