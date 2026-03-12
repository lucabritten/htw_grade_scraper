from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import requests
import pdfplumber
import re
import json
from dotenv import load_dotenv
import os

load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(BASE_DIR, "tmp")
os.makedirs(TMP_DIR, exist_ok=True)

username = os.getenv("UNI_USER")
password = os.getenv("UNI_PASSWD")

telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")


def login_and_download_pdf(username: str, password: str) -> str:
    """
    Logs into the HTW SIM portal using Selenium and downloads the
    grade overview PDF.
    
    Parameters:
        username (str): HIZ username
        password (str): HIZ password
    
    Returns:
        str: Path to the downloaded PDF file.
    """
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options)
    
    driver.get("https://sim.htwsaar.de")
    
    wait = WebDriverWait(driver, 20)
    
    wait.until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    
    current_url = driver.current_url
    driver.find_element(By.TAG_NAME, "button").click()
    
    wait.until(EC.url_changes(current_url))
    
    driver.get("https://sim.htwsaar.de/sap/bc/ui5_ui5/sap/yslcmcertificat/index.html#/LeistungsuebersichtSet/5017326,%2050000467,%20B.Sc.%20Praktische%20Informatik,%20EN")
    
    download_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="container-cm.slcm.certificate---detail3--pdfViewer-popupDownloadButton"]'))
    )
    
    download_button.click()
    
    driver.switch_to.window(driver.window_handles[-1])
    
    pdf_url = driver.current_url

    if pdf_url.startswith("blob:"):
        pdf_base64 = driver.execute_async_script("""
            const url = arguments[0];
            const callback = arguments[1];

            fetch(url)
              .then(r => r.blob())
              .then(blob => {
                  const reader = new FileReader();
                  reader.onloadend = () => callback(reader.result.split(',')[1]);
                  reader.readAsDataURL(blob);
              });
        """, pdf_url)

        import base64
        pdf_bytes = base64.b64decode(pdf_base64)

        pdf_path = os.path.join(TMP_DIR, "grades.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

    else:
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}
        headers = {"User-Agent": "Mozilla/5.0"}

        r = requests.get(pdf_url, cookies=cookies, headers=headers)
        r.raise_for_status()

        pdf_path = os.path.join(TMP_DIR, "grades.pdf")
        with open(pdf_path, "wb") as f:
            f.write(r.content)
    
    driver.quit()
    
    return os.path.join(TMP_DIR, "grades.pdf")

def normalize_module_name(name: str) -> str:
    """
    Normalizes module names so small formatting differences in the PDF
    (like appended ECTS numbers) do not create new entries.
    Example:
        "Software Engineering WiSe 2025 5" -> "Software Engineering WiSe 2025"
    """
    # remove trailing ECTS numbers like " 5" or " 10"
    name = re.sub(r"\s+\d+$", "", name)
    return name.strip()

def parse_pdf(path: str) -> dict:
    """
    Extracts module names and grades from the downloaded PDF.

    Parameters:
        path (str): Path to the saved grade-overview pdf file.

    Returns:
        dict:Dicionary mapping module names to grades.
    """
    
    with pdfplumber.open(path) as pdf:
        text = ""
        
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    
    pattern = r"([A-Za-z0-9\-\(\) ]+)\s+([0-9],[0-9]|AN)"
    
    matches = re.findall(pattern, text)
    
    grades = {}
    
    for module, grade in matches:
        module_name = normalize_module_name(module)
        grades[module_name] = grade
        
    return grades

def detect_changes(old_grades:dict, new_grades:dict) -> list:
    
    messages = []
    
    for module in new_grades:
        
        if module not in old_grades:
            messages.append(f"New exam registration in {module} detected!")
            continue
        
        if old_grades[module] == "AN" and new_grades[module] != "AN":
            messages.append(f"New grade added!\n {module}: {new_grades[module]}")
    
    return messages

def send_notifications(messages: list):
    
    for msg in messages:
        send_telegram_msg(msg, telegram_token, telegram_chat_id)
    

def send_telegram_msg(msg: str, token: str, chat_id: str):
    TOKEN = token
    CHAT_ID = chat_id
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    
    r = requests.post(url, data=payload)
    r.raise_for_status()
    
def main():
    pdf_path = login_and_download_pdf(username, password)
    
    new_grades = parse_pdf(pdf_path)
    
    messages = detect_changes(old_grades, new_grades)
    
    send_notifications(messages)
    
    with open(os.path.join(TMP_DIR, "grades.json"), "w") as f:
        json.dump(new_grades, f, indent=4, sort_keys=True)

if __name__ == "__main__":
    send_telegram_msg("Started checking grades...", telegram_token, telegram_chat_id)
    try:
        with open(os.path.join(TMP_DIR, "grades.json")) as f:
            old_grades = json.load(f)
    except FileNotFoundError:
        old_grades = {}

    main()