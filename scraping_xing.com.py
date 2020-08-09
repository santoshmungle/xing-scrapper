import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import random


data_folder = os.path.join('data', 'xing','profiles')

firefox_driver = os.path.join('data', 'geckodriver')

duckduckgo_folder = os.path.join('data', 'duckduckgo','results')

url_list_file = os.path.join(duckduckgo_folder,'xing_profiles_url.xlsx')


def scrap_all_profiles(url_list_file, driver = None):

    # get urls from a xlsx file
    parsed = pd.read_excel(url_list_file)
    url_list = parsed['url'].values.tolist()

    url_list = ['{}profile/version/embedded/{}/cv'.format(*url.split('profile/'))  for url in url_list]

    #generate filenames for saving data
    file_list = [url.replace('/', '_') for url in url_list]

    #filter out files that are already downloaded in the folder
    url_list, file_list = skip_existing_files(url_list, file_list, data_folder)

    # download files
    download_all_webpages(url_list, file_list, data_folder, driver = driver)
    print('Product lists scrapped !')


def get_driver():
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
    driver = webdriver.Firefox(executable_path=firefox_driver, firefox_profile=firefox_profile)
    return driver 

def xing_login():
    # automatic login into the xing webpage with login info
    driver = get_driver()
    driver.get('https://login.xing.com/')
    username = driver.find_element_by_name("username")
    password = driver.find_element_by_name("password")
    username.send_keys("enter your username here")
    password.send_keys("enter your password here")
    time.sleep(3)
    login_button = driver.find_element_by_xpath("//button[@class='style-ranks-primary-51d68d56 style-base-button-0ee47ed2 style-sizes-m-13be8878 StretchButtonGroup-StretchButtonGroup-stretchButton-87036de4']")
    login_button.click()
    return driver

def download_all_webpages(url_list, file_list, data_folder, driver = None):
    
    assert(len(url_list) == len(file_list))

    if not (driver):
        driver = get_driver()

    for i, url in enumerate(url_list):

        # download data of the webpage
        driver.get(url)
        
        driver.refresh()
        wait_time = 3 + random.random()
        time.sleep(wait_time)

        html = driver.page_source

        # handling 404 not found in xing
        sleep_time = 10
        sleep_time_increament = random.randrange(5)
        if '404' not in driver.title:
            # save it in the data folder
            try:
                with open(os.path.join(data_folder, file_list[i]+'.html'), "w+", encoding="utf-8") as f:
                    f.write(html)
                    f.close()
                print('{} / {}'.format(i, url))

            except OSError:
                pass
        else:
            print('Xing is blocking from searching. Retrying after {} minutes of wait'.format(sleep_time*sleep_time_increament/60))
            time.sleep(sleep_time*sleep_time_increament)
            

    driver.close()


def skip_existing_files(url_list, file_list, data_folder):

    # get exisiting files in data_folder and transform it to match it to file in file_list
    existing_html_files = [os.path.splitext(filename.replace('https___', 'https:__'))[0] for filename in os.listdir(data_folder)]

   
    #find existing files
    file_not_here = [i for i, (file_name, url) in enumerate(zip(file_list, url_list)) if file_name not in existing_html_files]

    #filter out existing files
    url_list = [url_list[i] for i in file_not_here] 
    file_list = [file_list[i] for i in file_not_here] 

    return url_list, file_list


def main():
    #login into the website
    driver = xing_login()
    # scrap all products list by categories of the website
    scrap_all_profiles(url_list_file, driver = driver)
    

if __name__== "__main__":
    main()
