from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import time

mobile_emulation = {

   "deviceMetrics": { "width": 900, "height": 1600, "pixelRatio": 3.0 },

   "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" }

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1280,1024")
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)



def alilink(link):
    driver = webdriver.Chrome(executable_path="/home/ubuntu/bots/chromedriver", chrome_options=chrome_options)
    try:
        driver.get(link)
        driver.implicitly_wait(3)
        name = driver.find_element(By.CLASS_NAME, "backflowUI--productName--2sqbI7y").text
        screen = str(time.time())+".png"
        driver.find_element(By.CLASS_NAME, "backflowUI--wrapper--2cztXEy").screenshot(screen)
        try:
            needpeople = driver.find_element(By.CLASS_NAME, "InviteList--needUser--O3VEcsM").text
            needpeople = int([int(s) for s in needpeople.split() if s.isdigit()][0])
        except:
            needpeople = 0
        driver.quit()
        text = f"ℹ️{name}ℹ️\n🔥 {link} 🔥"
        result = [text, screen, needpeople]
        return result
    except:
        driver.quit()
        return 0

def delete_ali_photo(filename):
    os.remove(filename)