from selenium import webdriver
import logging
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import os
import shutil
import pandas as pd
import time
from urllib.parse import urlparse, parse_qs
import random


def appendProduct(file_path2, data):
    temp_file = 'temp_file.csv'
    if os.path.isfile(file_path2):
        df = pd.read_csv(file_path2, encoding='utf-8')
    else:
        df = pd.DataFrame()

    df_new_row = pd.DataFrame([data])
    df = pd.concat([df, df_new_row], ignore_index=True)

    try:
        df.to_csv(temp_file, index=False, encoding='utf-8')
    except Exception as e:
        print(f"An error occurred while saving the temporary file: {str(e)}")
        return False

    try:
        os.replace(temp_file, file_path2)
    except Exception as e:
        print(f"An error occurred while replacing the original file: {str(e)}")
        return False

    return True


def login(driver, username, password):
    username_input = driver.find_element(By.XPATH, "//input[@id='id']")
    password_input = driver.find_element(By.XPATH, "//input[@id='pw']")
    for character in username:
        username_input.send_keys(character)
        random_number = random.uniform(0.1, 0.3)
        time.sleep(random_number)
    for character in password:
        password_input.send_keys(character)
        random_number = random.uniform(0.1, 0.3)
        time.sleep(random_number)
    time.sleep(1)
    # driver.find_element(By.CSS_SELECTOR,"input#switch").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//button[@id='log.login']").click()


def get_article_id(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    article_id = query_params.get('articleid', [None])[0]

    return article_id


def extract(driver, output_file_path):
    total_links = []
    driver.switch_to.frame(driver.find_element(
        By.XPATH, "//iframe[@id='cafe_main']"))

    links = driver.find_elements(By.XPATH, "//div[@class='inner_list']/a[1]")
    for link in links:
        total_links.append(link.get_attribute('href'))

    posting_id = 1
    for link in total_links:
        print(link)
        driver.get(link)
        time.sleep(8)
        try:
            driver.switch_to.frame(driver.find_element(
                By.XPATH, "//iframe[@id='cafe_main']"))
        except:
            pass
        current_datetime = datetime.now()
        time_of_scraping = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        # getting data
        article_id = get_article_id(link)

        category = driver.find_element(
            By.XPATH, "//div[@class='ArticleTitle']/a").text.replace(" •  ", "")
        text_type = "Post"
        title = driver.find_element(
            By.XPATH, "//h3[@class='title_text']").text.strip()
        writer_id = driver.find_element(
            By.XPATH, "//div[@class='profile_info']/div[1]/button").text.strip()
        writer_position = driver.find_element(
            By.XPATH, "//div[@class='profile_info']/em").text.strip()
        time_of_posting = driver.find_element(
            By.XPATH, "//span[@class='date']").text.strip()
        n_views = driver.find_element(
            By.XPATH, "//span[@class='count']").text.replace("조회", "").strip()
        n_likes = driver.find_element(
            By.XPATH, "//em[.='좋아요']/following-sibling::em").text.strip()
        n_comments = driver.find_element(
            By.XPATH, "(//a[@class='button_comment'])[1]/strong").text.strip()

        try:
            main_text = driver.find_element(
                By.XPATH, "//div[@class='article_viewer']/div[2]").text.strip()
        except:
             main_text = driver.find_element(
                By.XPATH, "//div[@class='article_viewer']").text.strip()

        data = {
            "Time_of_Scraping": time_of_scraping,
            "Category": category,
            "Text_Type": text_type,
            "Posting_ID": article_id,
            "Title": title,
            "Writer_ID": writer_id,
            "Writer_Poistion": writer_position,
            "Time_of_Posting": time_of_posting,
            "Main_Text": main_text,
            "N_Views": n_views,
            "N_Likes": n_likes,
            "N_Comments": n_comments,
            "Comment_ID": "",
            "Commentor_ID": "",
            "Time_of_Comment": "",
            "Comment": "",
            "Is_Reply_To_Comment": "",
            "Comment_ID_Replying": ""
        }
        print(data)
        appendProduct(output_file_path, data)

        comments_pagination = driver.find_elements(
            By.XPATH, "(//div[@class='ArticlePaginate'])[1]/button[@class='btn number']")
        if len(comments_pagination) == 0:
            comments_pagination = 1

        comment_id = 1
        for button in comments_pagination:
            comments = driver.find_elements(
                By.XPATH, "//li[@class='CommentItem']")
            comment_idx = 1
            for idx in range(len(comments)):
                text_type = "Comment"                
                try:
                    comment_list = driver.find_element(By.XPATH,f"//ul[@class='comment_list']/li[{comment_idx+1}]")
                except:
                    comment_list = driver.find_element(By.XPATH,f"//ul[@class='comment_list']/li[{comment_idx}]")

                if 'reply' in comment_list.get_attribute('class'):     
                    comment = driver.find_element(
                    By.XPATH, f"//ul[@class='comment_list']/li[{comment_idx}]/div/div/div[@class='comment_text_box']").text.strip()
                    commentor_id = driver.find_element(
                    By.XPATH, f"//ul[@class='comment_list']/li[{comment_idx}]/div/div/div[@class='comment_nick_box']/div").text.strip()
                    time_of_comment = driver.find_element(
                    By.XPATH, f"//ul[@class='comment_list']/li[{comment_idx}]/div/div/div[@class='comment_info_box']/span").text.strip() 

                    data = {
                    "Time_of_Scraping": time_of_scraping,
                    "Category": category,
                    "Text_Type": text_type,
                    "Posting_ID": article_id,
                    "Title": title,
                    "Writer_ID": writer_id,
                    "Writer_Poistion": writer_position,
                    "Time_of_Posting": time_of_posting,
                    "Main_Text": main_text,
                    "N_Views": n_views,
                    "N_Likes": n_likes,
                    "N_Comments": n_comments,
                    "Comment_ID": comment_id,
                    "Commentor_ID": commentor_id,
                    "Time_of_Comment": time_of_comment,
                    "Comment": comment,
                    "Is_Reply_To_Comment": "FALSE",
                    "Comment_ID_Replying": ""
                    }
                    comment_id += 1
                    comment_idx += 1
                    print(data)
                    appendProduct(output_file_path, data)



                    for reply_idx in range(comment_idx,comment_idx+100):
                        #12
                        comment_list = driver.find_element(By.XPATH,f"//ul[@class='comment_list']/li[{reply_idx}]")
                        if 'reply' in comment_list.get_attribute('class'):
                            is_reply = "TRUE"
                            comment_idx += 1
                            comment = driver.find_element(
                                    By.XPATH, f"//ul[@class='comment_list']/li[{reply_idx}]/div/div/div[@class='comment_text_box']").text.strip()
                            time_of_comment = driver.find_element(
                                    By.XPATH, f"//ul[@class='comment_list']/li[{reply_idx}]/div/div/div[@class='comment_info_box']/span").text.strip()
                            comment_id_replying = commentor_id
                            data = {
                            "Time_of_Scraping": time_of_scraping,
                            "Category": category,
                            "Text_Type": text_type,
                            "Posting_ID": article_id,
                            "Title": title,
                            "Writer_ID": writer_id,
                            "Writer_Poistion": writer_position,
                            "Time_of_Posting": time_of_posting,
                            "Main_Text": main_text,
                            "N_Views": n_views,
                            "N_Likes": n_likes,
                            "N_Comments": n_comments,
                            "Comment_ID": comment_id,
                            "Commentor_ID": commentor_id,
                            "Time_of_Comment": time_of_comment,
                            "Comment": comment,
                            "Is_Reply_To_Comment": is_reply,
                            "Comment_ID_Replying": comment_id_replying
                        }
                            comment_id += 1
                            print(data)
                            appendProduct(output_file_path, data)
                        else:  
                            is_reply = "FALSE"                      
                            break
                else:
                    is_reply = "FALSE"
                    comment = driver.find_element(
                    By.XPATH, f"//ul[@class='comment_list']/li[{comment_idx}]/div/div/div[@class='comment_text_box']").text.strip()
                    commentor_id = driver.find_element(
                    By.XPATH, f"//ul[@class='comment_list']/li[{comment_idx}]/div/div/div[@class='comment_nick_box']/div").text.strip()
                    time_of_comment = driver.find_element(
                    By.XPATH, f"//ul[@class='comment_list']/li[{comment_idx}]/div/div/div[@class='comment_info_box']/span").text.strip()
                    data = {
                    "Time_of_Scraping": time_of_scraping,
                    "Category": category,
                    "Text_Type": text_type,
                    "Posting_ID": article_id,
                    "Title": title,
                    "Writer_ID": writer_id,
                    "Writer_Poistion": writer_position,
                    "Time_of_Posting": time_of_posting,
                    "Main_Text": main_text,
                    "N_Views": n_views,
                    "N_Likes": n_likes,
                    "N_Comments": n_comments,
                    "Comment_ID": comment_id,
                    "Commentor_ID": commentor_id,
                    "Time_of_Comment": time_of_comment,
                    "Comment": comment,
                    "Is_Reply_To_Comment": is_reply,
                    "Comment_ID_Replying": ""
                }
                    comment_id += 1
                    comment_idx += 1
                    print(data)
                    appendProduct(output_file_path, data)                 


                

               

            button.click()
            time.sleep(2)

        # ends


def main():
    output_file_path = 'output.csv'

    options = webdriver.ChromeOptions()
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    driver.get("https://nid.naver.com/nidlogin.login")
    # login(driver,"bizlab2024","bizlab2024**")
    time.sleep(40)
    # time.sleep(2)
    driver.get("https://cafe.naver.com/jihosoccer123?iframe_url=/ArticleList.nhn%3Fsearch.clubid=23611966%26search.boardtype=L")
    time.sleep(2)
    extract(driver, output_file_path)


main()
