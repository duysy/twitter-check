import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time,re,requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
BASE_SERVER_URL = "http://flask:5000/"

options = webdriver.ChromeOptions()
options.add_argument('--verbose')
options.add_argument('--no-sandbox')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument("--disable-extensions")


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
options.add_argument("--window-size=1920,1080")
options.add_argument(f"user-agent={user_agent}")
options.add_argument("--headless")


time.sleep(10)
driver = webdriver.Remote(
    command_executor='http://chrome:4444/wd/hub',
    options=options,
)

driver.set_page_load_timeout(90)
driver.implicitly_wait(6)

driver.get("https://twitter.com/")

with open('cookies.pkl', 'rb') as f:
    cookies = pickle.load(f)
for cookie in cookies:
    driver.add_cookie(cookie)
driver.get("https://twitter.com/")


def checkFollow(from_user,target_user):
    print("START CHECK",from_user,"FOLLOW",target_user)
    driver.get(f"https://twitter.com/{from_user}/following")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'span')))
    time.sleep(4)
    # driver.save_screenshot("checkFollow.png")
    print(driver.current_url)
    if "login" in driver.current_url:
        return "PLEASE_CONFIG_AUTH"
    twitter_usernames = re.findall(r'>@(\w+)<', driver.page_source)
    twitter_usernames  = set(twitter_usernames)
    if target_user in twitter_usernames:
        return True
    return False

def checkRepost(from_user,target_post_id):
    print("START REPOST",from_user,"POST",target_post_id)
    driver.get(f"https://twitter.com/{from_user}")
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'span')))
    time.sleep(4)
    # driver.save_screenshot("checkRepost.png")
    print(driver.current_url)
    if "login" in driver.current_url:
        return "PLEASE_CONFIG_AUTH"
    if target_post_id in driver.page_source:
        return True
    return False

while True:
    taskResponse = requests.get(f"{BASE_SERVER_URL}/twitter/get-task/")
    if not taskResponse.text == "EMPTY":
        taskData = taskResponse.json()
        if taskData.get("type") == "CHECK_USER_FOLLOW":
            idTask =str(taskData.get("idTask")).replace("@","") 
            user_name = str(taskData.get("user_name")).replace("@","")
            user_target = str(taskData.get("user_target")).replace("@","")
            status = checkFollow(user_name,user_target)
            url = f"{BASE_SERVER_URL}/twitter/set-task-value/{idTask}"
            payload = json.dumps({
            "status": str(status)
            })
            headers = {
            'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
        elif taskData.get("type") == "CHECK_USER_REPOST":
            idTask =str(taskData.get("idTask")).replace("@","") 
            user_name = str(taskData.get("user_name")).replace("@","")
            target_post_id = str(taskData.get("target_post_id")).replace("@","")
            status = checkRepost(user_name,target_post_id)
            url = f"{BASE_SERVER_URL}/twitter/set-task-value/{idTask}"
            payload = json.dumps({
            "status": str(status)
            })
            headers = {
            'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
    time.sleep(1)