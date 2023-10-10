from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.by import By
import csv
from bs4 import BeautifulSoup



# This function goes to email pages from the results page, scrapes and return emails 
def get_emails(links):
    emails = []
    # failed_email_links = []
    for link in links:
        try:
            driver.get(link)
            email = driver.find_element(By.CSS_SELECTOR, 'a.showModalPec').get_attribute('OnClick')
            email = email[14:-2]
            print(email)
            emails.append([email])
            # time.sleep(1)
        except:
            # print('failed')
            pass
            # failed_email_links.append(link)
    return emails


# This function saves all the scraped emails to a text file
def save_csv(emails):
    with open('emails.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerows(emails)
    return 


def parse(page):
    soup = BeautifulSoup(page, 'html.parser')
    next_page_url = soup.select_one('a:contains("Successivo")')['href']
    td_elements = soup.find_all('td', class_='gratuitaTd')
    links = [next_page_url]
    for td in td_elements:
        link = td.find('a')['href']
        links.append(link)
    return links


    
# The main block
if __name__ == '__main__':
    URL = 'https://www.registroimprese.it/web/guest/home'


    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.implicitly_wait(4)
    driver.get(URL)
    

    emails_count = int(input('number of emails? '))
    pages_count = emails_count//20
    # start_time = time.time()
    for _ in range(pages_count):
        page = driver.page_source
        links = parse(page)
        next_page_url = links[0]
        links = links[1:]
        emails = get_emails(links)
        save_csv(emails)
        try:
            driver.get(next_page_url) # gets the next page
        except:
            print('next page loading failed')
            not_loaded = True
            while not_loaded: # keeps trying to load the next page until it succeeds
                try:
                    driver.get(next_page_url)
                except:
                    time.sleep(5)
                    continue
                not_loaded = False


        time.sleep(4) 
    
    # end_time = time.time()
    # print(end_time - start_time)


        # emails, failed_emails = get_emails(failed_email_links)
        # save_csv(emails)
    
    driver.quit()

