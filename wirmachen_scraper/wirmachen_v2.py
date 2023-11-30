from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from datetime import datetime
import threading
import logging
import os
import re
import requests
import time
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager


def get_driver(proxy):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=%s' % proxy)
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(executable_path='chromedriver.exe',options=chrome_options)
    driver.implicitly_wait(8)
    print(f'>>>>>>>>>> webdriver created with the proxy {proxy}')
    return driver


def get_page_data(URL, driver, delivery_index, type, edition, actual_quantity, delivery):
    current_time = datetime.now().strftime('%d-%m-%Y %H:%M')
    headline = driver.find_element(By.CSS_SELECTOR, 'h1.product-title').text
    page_data = [current_time, URL, headline, type, edition, actual_quantity, delivery]

    actual_delivery_fonts = driver.find_elements(By.CSS_SELECTOR, '.delivery-date-text')
    actual_delivery = actual_delivery_fonts[delivery_index].text   
    actual_delivery = re.search('\d+', actual_delivery).group(0)
    page_data.append(actual_delivery)

    all_prices_divs = driver.find_elements(By.CSS_SELECTOR, 'div.col-6._list_row.text-right')
    for price_div in all_prices_divs:
        price = price_div.text.split(' ')[0]
        page_data.append(price)
    net_price = driver.find_element(By.CSS_SELECTOR, 'div.col-6._list_row_2.text-right').text.split(' ')[0]
    page_data.append(net_price)
    return page_data  # a list which has data in order according to the header of the csv


def create_file(dir_path, type, delivery):
    current_time = datetime.now().strftime('%Y%m%d%H%M')
    file_name = type + ' ' + delivery + ' ' + current_time
    file_name = re.sub(r'[^\w\säöüß-]', '', file_name) # filter any unwanted characters
    file_name = file_name + '.csv'
    file_path = os.path.join(dir_path, file_name)
    file_path = '\\\\?\\' + os.path.abspath(file_path)  # extending the limit of path length
    with open(file_path, 'w') as f:
        pass
    return file_path


def store_data(dir_path, type, data_dfs, URL):
    delivery_names = [
        'Versand A', 
        'Versand B', 
        'Versand C',
        'Versand D'
    ]
    num_files = 4
    for i in range(len(delivery_names)):
        if data_dfs[i].empty == True: # not creating file for empty dataframe
            num_files = num_files - 1
            continue
        file_path = create_file(dir_path, type, delivery_names[i])
        data_dfs[i].to_csv(file_path, sep='|', index=False)
    
    print(f'>>>>>>>>>>> {num_files} files created for type {type} and URL {URL}')
    return



def main(URL, type, dir_path, proxy):
    driver = get_driver(proxy)
    driver.get(URL)
        
    select_type = Select(driver.find_element(By.CSS_SELECTOR, '#sorten'))
    select_type.select_by_visible_text(type)

    try:
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, 'uc-btn-accept-banner'))).click()
        print(f'>>>>>>>>>>>> clicked the cookies button type: {type}')
    except Exception:
        logging.warning(f'banner did not appear for {type} ')
        type_filtered = re.sub(r'[^\w\säöüß-]', '', type)
        driver.save_screenshot(f'{type_filtered}.png')


    # create dataframes for all delivery options
    data_dfs = [pd.DataFrame(columns=['current_time', 'url', 'headline', 'type', 'edition', 'actual_quantity', 'delivery_time', 'actual_delivery_time', 'our_price', 'additional_options', 'processing_finishing', 'shipping', 'net_price']) for _ in range(4)] 

    # get all editions   
    select_edition = Select(driver.find_element(By.CSS_SELECTOR, '#wmd_shirt_auflage'))
    edition_list = [option.text for option in select_edition.options]    

    try: # ensures that the thread properly terminates and creates files in case of an exception
        for edition in edition_list:
            select_edition = Select(driver.find_element(By.CSS_SELECTOR, '#wmd_shirt_auflage')) 
            select_edition.select_by_visible_text(edition)
            actual_quantity = edition.split(' ')[0].replace('.', '')
            time.sleep(2) 

            # get all delivery options
            delivery_options = driver.find_elements(By.NAME, "deliveryOption")
            for delivery_index in range(len(delivery_options)):
                delivery_options = driver.find_elements(By.NAME, "deliveryOption") 

                # this loop clicks the delivery 2 times more with 4s wait if first click is intercepted
                max_tries = 3
                attempt = 0
                while attempt < max_tries:
                    try:
                        delivery_options[delivery_index].click()
                        time.sleep(1)
                        break
                    except Exception as e:
                        logging.warning(f"The steps for the click interception exception were executed for type {type}: edition {edition}: del index {delivery_index}: {e}")
                        time.sleep(4)
                        delivery_options = driver.find_elements(By.NAME, "deliveryOption")

                        if attempt == 2:
                            logging.error(f'the click was not done for type {type}: edition {edition}: del index {delivery_index}')
                            type_filtered = re.sub(r'[^\w\säöüß-]', '', type)
                            driver.save_screenshot(f'edition {type_filtered}.png')
                        attempt += 1


                delivery = driver.find_element(By.XPATH, "//label[@class='radio-container checked-radio-label ']/span[2]/strong ").text
                page_data = get_page_data(URL, driver, delivery_index, type, edition, actual_quantity, delivery)
                df = data_dfs[delivery_index]
                df.loc[len(df)] = page_data


    except Exception as e:
        logging.warning(f"Outer Exception: An exception was generated by the type {type}: edition {edition}: {e}")

    finally:
        store_data(dir_path, type, data_dfs, URL)
        driver.quit()      
        return 


def start_threads(URL, type_list, dir_path, proxy_list):
    thread_list = []
    for type_index, type in enumerate(type_list):
        proxy = proxy_list[type_index]
        t = threading.Thread(target=main, args=(URL, type, dir_path, proxy))      
        t.start()
        thread_list.append(t)


    for thread in thread_list:
        thread.join()
    return


def create_directory(soup):
    navigation_ol = soup.select_one('.breadcrumb-navigation')
    navigation_li = navigation_ol.find_all('li')
    # path = [li.text.strip().replace('/', '').replace('\\', '') for li in navigation_li[1:]]
    path = [re.sub(r'[/\:*?"<>|]', '', li.text.strip()) for li in navigation_li[1:]]
    path = '\\'.join(path)
    os.makedirs(path, exist_ok=True)
    return path


def make_request(URL):
    MAX_TRIES = 3
    tries = 0
    while tries < MAX_TRIES:
        response = requests.get(URL)
        if response.status_code == 200:
           return response
        else:
            tries += 1
            time.sleep(5)

    logging.error(f'could not make request to {URL}')
    return None



if __name__ == "__main__":
    logging.basicConfig(filename='wirmachen.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s', filemode='w')
    with open('Flyer-URLs.txt', 'r') as f:
        url_list = [line.strip() for line in f.readlines()]

    with open('Webshare 25 proxies.txt', 'r') as f:
        proxy_list = [line.strip() for line in f.readlines()]
    # driver = get_driver(proxy_list[0])
    # driver.quit()
      
    for URL in url_list:
        start_time = datetime.now()
         
        response = make_request(URL)
        if response is None:
            continue
        soup = BeautifulSoup(response.content, 'html.parser')
        dir_path = create_directory(soup)
        select_type = soup.select_one('#sorten')
        type_list = select_type.find_all('option')
        type_list = [option.text for option in type_list]
    
        total_types = len(type_list)
        if total_types > 13:
            chunk_size = 13  
            for i in range(0, total_types, chunk_size):
                chunk = type_list[i:i+chunk_size]
                start_threads(URL, chunk, dir_path, proxy_list)


        else:
            start_threads(URL, type_list, dir_path, proxy_list)
        
        end_time = datetime.now()
        print(f'>>>>>>>>>>> Total time taken by the URL {URL}: {end_time - start_time}')
        logging.info(f'Total time taken by the URL {URL}: {end_time - start_time}')


    print('The scraping is done')
    input("Press enter to exit the application: ")


           




   


