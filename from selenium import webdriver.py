from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os

def download_file_via_js(driver, file_url, download_path):
    # JavaScript code to create an anchor element and trigger the download
    js_code = f'''
    var a = document.createElement('a');
    a.href = "{file_url}";
    a.download = "{os.path.basename(download_path)}";
    var ev = document.createEvent("MouseEvents");
    ev.initMouseEvent("click", true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
    a.dispatchEvent(ev);
    '''
    driver.execute_script(js_code)

def login_and_download(driver, username_str, password_str):
    # Open Zoom login page
    driver.get("https://zoom.us/signin")

    # Wait for the cookie consent popup and accept it
    try:
        cookie_accept_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        cookie_accept_button.click()
    except:
        print("No cookie consent popup found or failed to click accept button.")

    # Wait for the username input field to be present
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "email")))

    # Find the username and password input fields and enter your credentials
    username = driver.find_element(By.ID, "email")
    username.send_keys(username_str)
    password = driver.find_element(By.ID, "password")
    password.send_keys(password_str)

    # Debug: Take a screenshot before clicking the Sign In button
    driver.save_screenshot("before_sign_in.png")

    # Wait for the Sign In button to be clickable
    try:
        sign_in_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="js_btn_login"]/span'))
        )
    except Exception as e:
        print("Sign In button not found or not clickable.")
        driver.save_screenshot("sign_in_error.png")
        raise e

    # Scroll to the Sign In button
    driver.execute_script("arguments[0].scrollIntoView();", sign_in_button)

    # Click the Sign In button
    sign_in_button.click()

    # Wait for the login process to complete and navigate to the profile page
    try:
        WebDriverWait(driver, 60).until(EC.url_contains("zoom.us/profile"))
        print("Login successful and navigated to profile page.")
    except Exception as e:
        print("Login failed or did not navigate to profile page.")
        driver.save_screenshot("login_failed.png")
        raise e

    # Navigate to the Recordings section
    driver.get("https://zoom.us/recording")

    # Debug: Take a screenshot after navigating to the recordings page
    driver.save_screenshot("after_navigating_to_recordings.png")

    # Wait for the page to load
    try:
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="personal-nav-list"]/li[9]/a')))
        print("Recordings page loaded successfully.")
    except Exception as e:
        print("Recordings page did not load.")
        driver.save_screenshot("recordings_page_load_error.png")
        raise e

    # Find the first recording's dropdown menu and click it
    try:
        more_icon = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="recordingTable"]/div[5]/div[2]/table/tbody/tr/td/div/div/div/div/button/i'))
        )
        if more_icon.is_displayed():
            more_icon.click()
            print('More icon clicked successfully.')
        else:
            print('More icon is not visible.')
            driver.save_screenshot("more_icon_not_visible.png")
    except Exception as e:
        print("More icon not found or not clickable.")
        driver.save_screenshot("more_icon_error.png")
        raise e

    # Use a method similar to DemoTest to find and click the download link
    try:
        li_items = driver.find_elements(By.XPATH, '//div[contains(text(), "Download (1 files)")]')
        for li_item in li_items:
            actions = ActionChains(driver)
            actions.move_to_element(li_item).double_click().perform()
            print("Download link clicked successfully.")
            
            # Wait for iframe to appear and switch to it
            iframe = WebDriverWait(driver, 30).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[contains(@src, "download")]'))
            )

            # Now you can locate and interact with the download link within the iframe
            download_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//a[contains(@class, "download-btn")]'))
            )

            # Get the href of the download button
            download_url = download_button.get_attribute('href')

            # Define the download path
            download_path = os.path.join(os.getcwd(), 'downloaded_recording.mp4')

            # Download the file using JavaScript
            download_file_via_js(driver, download_url, download_path)
            print("File downloaded successfully.")

            # Switch back to the default content
            driver.switch_to.default_content()
            break

    except Exception as e:
        print("Download link not found or not clickable.")
        driver.save_screenshot("download_link_error.png")
        raise e

# Set up the driver
driver = webdriver.Chrome()  # Ensure you have the Chrome WebDriver installed

try:
    # Prompt for username and password
    username = input("Enter your Zoom username: ")
    password = input("Enter your Zoom password: ")
    # Call the function with the provided credentials
    login_and_download(driver, username, password)
finally:
    # Close the browser
    driver.quit()
