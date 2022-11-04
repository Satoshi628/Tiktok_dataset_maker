#coding: utf-8
#----- 標準ライブラリ -----#
import requests
import json
import os
import random
import string
from time import sleep
import re
import shutil

#----- 専用ライブラリ -----#
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd

#----- 自作モジュール -----#
# None

def get_video(element):
    try:
        return element.find_element_by_tag_name("video").get_attribute('src')
    except:
        return None

def get_submmit(driver, N=10):
    #actions = ActionChains(driver)
    #actions.move_to_element(driver.find_element_by_xpath(<<xpath>>)).perform()
    
    #投稿一覧フォームの探索
    main_body_class = "tiktok-1id9666-DivMainContainer ec6jhlz0"
    for em in driver.find_elements_by_xpath("/html/body/div/div/div"):
        if em.get_attribute('class') == main_body_class:
            main_body = em
            break
    
    
    submmit_class = "tiktok-1nncbiz-DivItemContainer etvrc4k0"
    n = 0
    videos = []
    iine_nums = []
    comment_nums = []
    share_nums = []

    while True:
        for em in main_body.find_elements_by_xpath("div/div")[n:]:
            driver.execute_script("arguments[0].scrollIntoView();", em)
            sleep(1)

            if em.get_attribute('class') == submmit_class:
                text = em.text
                iine_nums.append(str2int(text.split("\n")[-3]))
                comment_nums.append(str2int(text.split("\n")[-2]))
                share_nums.append(str2int(text.split("\n")[-1]))
                videos.append(get_video(em))
                n += 1
                if n >= N:
                    return videos, iine_nums, comment_nums, share_nums

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
        #投稿一覧フォームの探索
        for em in driver.find_elements_by_xpath("/html/body/div/div/div"):
            if em.get_attribute('class') == main_body_class:
                main_body = em
                break

def str2int(str_int):
    UNIT = {"K": 10 ** 3,
            "M": 10 ** 6,
            "G": 10 ** 9}
    if re.fullmatch('[0-9]+', str_int):
        return int(str_int)
    else:
        unit = UNIT[str_int[-1]]
        number = float(str_int[:-1])
        return int(number * unit)

def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def url2video(save_dir_path, video_path):
    response = requests.get(video_path)
    with open(save_dir_path, "wb") as saveFile:
        saveFile.write(response.content)

if __name__ == "__main__":
    tiktok_url = "https://www.tiktok.com/ja-JP/"
    CHROME_DRIVER_PATH = "chromedriver"

    #　ヘッドレスモードでブラウザを起動
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument('--headless')
    options.binary_location = "/usr/bin/chromium-browser"
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get(tiktok_url)
    driver.maximize_window()

    data_num = 20
    videos, iine_nums, comment_nums, share_nums = get_submmit(driver, N=data_num)

    shutil.rmtree("Tiktok_main_page_dataset")
    mkdir("Tiktok_main_page_dataset")
    mkdir("Tiktok_main_page_dataset/videos")

    video_paths = [f"Tiktok_main_page_dataset/videos/{idx:06}.mp4" for idx in range(len(videos))]
    df = {"video_path": video_paths,
            "iine": iine_nums,
            "comment": comment_nums,
            "share": share_nums}
    df = pd.DataFrame(df)
    df.to_csv("Tiktok_main_page_dataset/data_info.csv")
    for video, save_path in zip(videos, video_paths):
        url2video(save_path, video)
    
    driver.close()
    driver.quit()



