from flask import Flask, request, url_for, redirect, render_template, jsonify
from selenium import webdriver
# import by
import selenium
from selenium.webdriver.common.by import By
import json
from time import sleep
# import keys from selenium.webdriver.common.keys
from selenium.webdriver.common.keys import Keys
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

def time_to_hms(seconds: int):
    hour = int(seconds / 3600)
    minute = int(seconds / 60) % 60
    second = int(seconds) % 60
    if hour < 10:
        hour = f"0{hour}"
    if minute < 10:
        minute = f"0{minute}"
    if second < 10:
        second = f"0{second}"
    if int(hour):
        hour_minute_second = f"{hour}:{minute}:{second}"
    else:
        hour_minute_second = f"{minute}:{second}"
    return hour_minute_second

@app.route('/clip')
def clip():
    # attribute
    """
    video_id:str
    start_time:str
    end_time:str
    title:str
    username:str
    """
    # get attribute
    video_id = request.args.get('video_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    title = request.args.get('title')
    username = request.args.get('username')
    if start_time > end_time:
        start_time, end_time = end_time, start_time
    title = f"{title} - {username}"
    # get driver
    driver = app.driver
    while True:
        try:
            driver.get(f"https://www.youtube.com/watch?v={video_id}")
        except selenium.common.exceptions.NoSuchWindowException:
            driver = construct_driver()
            app.driver = driver
            continue
        else:
            break
    sleep(0.5)
    # button with title 'clip'
    #driver.execute_script("document.body.style.zoom = '0.5'")
    try:
        driver.find_element(By.XPATH, "//button[@aria-label='Clip']").click()
    except selenium.common.exceptions.ElementNotInteractableException:
        while True:
            try:
                driver.find_element(By.XPATH, "//button[@aria-label='More actions']").click()
                sleep(0.5)
                driver.find_element(By.XPATH, "//button[@aria-label='Clip']").click()
            except:
                pass
            break
        
    start = driver.find_elements(by=By.ID, value="start")[1]
    start.send_keys(Keys.CONTROL + "a")
    start.send_keys(start_time)
    end = driver.find_elements(by=By.ID, value="end")[1]
    end.send_keys(Keys.CONTROL + "a")
    end.send_keys(end_time)

    driver.find_element(by=By.ID, value="textarea").send_keys(title)

    # button with aria-label 'Share clip

    driver.find_element(By.XPATH, "//button[@aria-label='Share clip']").click()

    while True:
        try:
            x = driver.find_element(By.ID, "share-url")
        except:
            continue
        else:
            return x.get_attribute("value")

def construct_driver():
    driver = webdriver.Chrome()
    with open("cookies.json", "r", encoding="UTF-8") as f:
        cookie_dict = json.load(f)


    driver.maximize_window()
    driver.get(cookie_dict["url"])
    for cookie in cookie_dict["cookies"]:
        if cookie["sameSite"] == "unspecified":
            cookie["sameSite"] = "Lax"
        elif cookie["sameSite"] == "no_restriction":
            cookie["sameSite"] = "None"
        else:
            cookie["sameSite"] = "Strict"
        driver.add_cookie(cookie)

    driver.get(cookie_dict["url"])
    return driver

driver = construct_driver()


if __name__ == '__main__':
    app.driver = driver
    app.run(host='0.0.0.0', port=400, debug=False, threaded=False)