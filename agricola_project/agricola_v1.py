from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.by import By


# This function is used to accept cookies if it appears
def accept_cookies(driver):
    cookies = driver.find_element(By.CSS_SELECTOR, 'input[value="Acconsento"]')
    if cookies:
        cookies.click()
        return driver
    else:
        return driver


# This function searches for the given keyword in the search engine and handles captcha
def search_keyword(driver, keyword):
    driver.find_element(By.ID, 'inputSearchField').send_keys(keyword)
    time.sleep(1)
    driver.find_element(By.ID, 'btnCercaGratuita').click()
    no_captcha = input('should I continue? ')
    if no_captcha == 'y':
        accept_cookies(driver)
        return driver


# This function goes to email pages from the results page, scrapes and return emails 
def get_emails(driver):
    emails = []
    for i in range(20):
        td_elements = driver.find_elements(By.CLASS_NAME, 'gratuitaTd')
        link = td_elements[i].find_element(By.TAG_NAME, 'a').get_attribute('href')
        driver.get(link)
        try:
            email = driver.find_element(By.XPATH, '//*[@id="p_p_id_ricercaportlet_WAR_ricercaRIportlet_"]/div/div/div[2]/div/div/div[1]/div[2]/div[1]/div[1]/div[2]/dl[1]/div/div[1]/dl/dd/a').get_attribute('OnClick')
            email = email[14:-2]
            emails.append(email)
            # print(email)
            driver.execute_script("window.history.go(-1)")
        except:
            driver.execute_script("window.history.go(-1)")
            break
    return emails

    
# This function changes the search result page
def change_page(driver):
    next_page = driver.find_element(By.XPATH, "//*[contains(text(), 'Successivo')]")
    next_page_url = next_page.get_attribute('href')
    driver.get(next_page_url)
    return driver


# This function saves all the scraped emails to a text file
def save_txt(emails):
    with open('emails.txt', 'a') as f:
        for email in emails:
            f.write('%s\n' % email)
    return 

    
# The main block
if __name__ == '__main__':
    URL = 'https://www.registroimprese.it/web/guest/home'
    KEYWORD = input('give keyword: ')


    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.implicitly_wait(10)
    driver.get(URL)


    driver = accept_cookies(driver)
    driver = search_keyword(driver, KEYWORD)
    

    emails = []
    for _ in range(1000): # range of pages to scrape. the limit is 7538
        emails.extend(get_emails(driver))
        driver = change_page(driver)


    save_txt(emails)
    driver.quit()
    
