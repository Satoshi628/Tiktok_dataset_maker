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
import argparse

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

def get_submmit(driver, words, N=10):
    #検索ボックスに検索ワードを入れ実行
    search = driver.find_element_by_name('q')
    search.send_keys(words)
    search.submit()

    #動画一覧ボタンをクリック
    video_button = driver.find_element_by_id('tabs-0-tab-search_video')
    video_button.click()
    sleep(2)
    
    #投稿一覧フォームの探索
    main_body_data_e2e = "search_video-item-list"
    for em in driver.find_elements_by_xpath("/html/body/div/div/div/div/div/div"):
        if em.get_attribute('data-e2e') == main_body_data_e2e:
            main_body = em
            break
    
    submmit_class = "tiktok-1soki6-DivItemContainerForSearch e19c29qe9"
    n = 0
    videos = []
    iine_nums = []
    comment_nums = []
    save_words = []

    while True:
        for em in main_body.find_elements_by_xpath("div")[n:]:
            driver.execute_script("arguments[0].scrollIntoView();", em)
            sleep(0.5)
            if em.get_attribute('class') == submmit_class:
                em.click()
                sleep(0.5)
                iine_nums.append(str2int(driver.find_element_by_xpath("//strong[@data-e2e='browse-like-count']").text))
                comment_nums.append(str2int(driver.find_element_by_xpath("//strong[@data-e2e='browse-comment-count']").text))
                videos.append(get_video(driver))
                save_words.append(words)
                driver.back()
                sleep(0.5)
                n += 1
                if n >= N:
                    return videos, iine_nums, comment_nums, save_words

        # 更新ボタンをクリック
        button_data_e2e = "search-load-more"
        load_button = driver.find_element_by_xpath("//button[@data-e2e='search-load-more']")
        load_button.click()
        sleep(1)
        #投稿一覧フォームの探索
        for em in driver.find_elements_by_xpath("/html/body/div/div/div/div/div/div"):
            if em.get_attribute('data-e2e') == main_body_data_e2e:
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

def rmdir(path):
    if os.path.exists(path):
        shutil.rmtree(path)

def url2video(save_dir_path, video_path):
    response = requests.get(video_path)
    with open(save_dir_path, "wb") as saveFile:
        saveFile.write(response.content)

def arg_set():
    parser = argparse.ArgumentParser(description='scraping setting')

    # 3. parser.add_argumentで受け取る引数を追加していく
    parser.add_argument('-s', '--search', required=True, nargs="*", help='search words')
    parser.add_argument('-n', type=int, help='number of data', default=10)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = arg_set()
    tiktok_url = "https://www.tiktok.com/ja-JP/"
    CHROME_DRIVER_PATH = "chromedriver"

    # ヘッドレスモードでブラウザを起動
    options = Options()
    options.add_argument("--no-sandbox")
    #options.add_argument('--headless')
    options.binary_location = "/usr/bin/chromium-browser"
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get(tiktok_url)
    driver.maximize_window()

    #検索ボックスに検索ワードを入れ実行
    search = driver.find_element_by_name('q')
    search.send_keys("猫")
    search.submit()

    print("ロボット出ないことの証明を行ってください。")
    print("完了したらエンターキーを押してください。")
    input()

    #動画一覧ボタンをクリック
    video_button = driver.find_element_by_id('tabs-0-tab-search_video')
    video_button.click()
    sleep(2)

    video_list = []
    iine_num_list = []
    comment_num_list = []
    save_word_list = []

    for word in args.search:
        videos, iine_nums, comment_nums, save_words = get_submmit(driver, word, N=args.n)
        video_list.extend(videos)
        iine_num_list.extend(iine_nums)
        comment_num_list.extend(comment_nums)
        save_word_list.extend(save_words)

    rmdir("Tiktok_search_dataset")
    mkdir("Tiktok_search_dataset")
    mkdir("Tiktok_search_dataset/videos")

    video_paths = [f"Tiktok_search_dataset/videos/{idx:06}.mp4" for idx in range(len(video_list))]
    df = {"video_path": video_paths,
            "iine": iine_num_list,
            "comment": comment_num_list,
            "search_word":save_word_list}
    df = pd.DataFrame(df)
    df.to_csv("Tiktok_search_dataset/data_info.csv")
    for video, save_path in zip(video_list, video_paths):
        url2video(save_path, video)
    
    driver.close()
    driver.quit()



