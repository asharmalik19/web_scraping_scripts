"""scrapes car details from https://www.ooyyo.com

This script scrapes all the pages of cars of the country specified in the main function for the required details. Then, stores the details into a csv fle. The country is specified through the url. Urls to the first page of cars of every country is already stored in a list. The script gets the first page, parse details and also parses the url to the next page. It uses a loop to parse url of the next page from the current page and repeat the process of getting the next page, parsing the details and the url of the next page.

This script requires that `pandas`, `bs4`, `requests`, `datetime` be installed in the python environment in which you are running this script.

This file can be imported as a module and contains the following functions:
    
    * get_cars_soup - returns the beautifulsoup object containing the page specified by given url
    * parse_car_details - returns the data parsed from the page given as beatifulsoup object and returns the link to the next page
    * main - the main function
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_cars_soup(session, url):
    '''get the page using the session 

    parameters
    ----------
    session : session object
        object of requests.Session() class
    url : str
        url of the page to get
    
    Raises
    ------
    Exception
        url is not found
    
    Return 
    ------
    soup : beautifulsoup object
        object of class BeautifulSoup from bs4 module
    '''
    res = session.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    return soup

def parse_car_details(soup, data):
    '''parse required details of the cars from the soup and url of the next page
    
    Parameters
    ----------
    soup : beautifulsoup object
        object of BeautifulSoup class from bs4 module
    data : pandas dataframe
        a dataframe to be filled with the parsed details

    Raises   
    ------
    Exception
        url not found

    Return
    ------
    data : pandas dataframe
        a dataframe which holds the scraped data
    next_page_url : str
        url of the next page to be scraped
    '''
    all_info_tags = soup.find_all('div', class_='beta')
    for tag in all_info_tags:
        brand_spans = tag.h2.select('span')
        brand = [_.text for _ in brand_spans]
        h2_text = tag.h2.findAll(text=True, recursive=False)[-1].strip()     
        brand.append(h2_text)        
        brand = ' '.join(brand)
        
        mileage_div = tag.find('div', class_='mileage')
        mileage = mileage_div.strong.text.strip().split(' ')[0]
        car_type_div = tag.find('div', class_='description')
        car_type = car_type_div.span.text.split(',')[0]
        price_a_tag = tag.parent.parent
        price = price_a_tag['data-price']
        pandas_list = [brand, car_type, mileage, price]
        data.loc[len(data)] = pandas_list     

    next_page_url = soup.find('a', class_='btn btn-lg btn-block btn-warning')['href']
    base_url = 'https://www.ooyyo.com'
    next_page_url = base_url + next_page_url

    return data, next_page_url
    

def main():
    country_first_page_links = [
        'https://www.ooyyo.com/austria/used-cars-for-sale/c=CDA31D7114D3854F111B936FAA651453/',
        'https://www.ooyyo.com/belgium/used-cars-for-sale/c=CDA31D7114D3854F111BE36FAA651453/', 
        'https://www.ooyyo.com/bulgaria/used-cars-for-sale/c=CDA31D7114D3854F111B876FAA651453/',
        'https://www.ooyyo.com/czech+republic/used-cars-for-sale/c=CDA31D7114D3854F111B976FAA651453/',
        'https://www.ooyyo.com/denmark/used-cars-for-sale/c=CDA31D7114D3854F111B9E6FAA651453/',
        'https://www.ooyyo.com/france/used-cars-for-sale/c=CDA31D7114D3854F111BFB6FAA651453/',
        'https://www.ooyyo.com/germany/used-cars-for-sale/c=CDA31D7114D3854F111BFE6FAA651453/',
        'https://www.ooyyo.com/hungary/used-cars-for-sale/c=CDA31D7114D3854F111B8F6FAA651453/',
        'https://www.ooyyo.com/italy/used-cars-for-sale/c=CDA31D7114D3854F111BF36FAA651453/',
        'https://www.ooyyo.com/netherlands/used-cars-for-sale/c=CDA31D7114D3854F111BFA6FAA651453/',
        'https://www.ooyyo.com/norway/used-cars-for-sale/c=CDA31D7114D3854F111B926FAA651453/',
        'https://www.ooyyo.com/poland/used-cars-for-sale/c=CDA31D7114D3854F111B956FAA651453/',
        'https://www.ooyyo.com/portugal/used-cars-for-sale/c=CDA31D7114D3854F111B9F6FAA651453/',
        'https://www.ooyyo.com/romania/used-cars-for-sale/c=CDA31D7114D3854F111B746FAA651453/',
        'https://www.ooyyo.com/spain/used-cars-for-sale/c=CDA31D7114D3854F111BE56FAA651453/',
        'https://www.ooyyo.com/sweden/used-cars-for-sale/c=CDA31D7114D3854F111BF26FAA651453/',
        'https://www.ooyyo.com/switzerland/used-cars-for-sale/c=CDA31D7114D3854F111BE86FAA651453/',
        'https://www.ooyyo.com/turkey/used-cars-for-sale/c=CDA31D7114D3854F111B986FAA651453/',
        'https://www.ooyyo.com/united+states/used-cars-for-sale/c=CDA31D7114D3854F111BF66FAA651453/'
    ]
    session = requests.Session()

    #specify the country through the url and get its first page
    soup = get_cars_soup(session, country_first_page_links[7])
    headers = ['brand', 'type', 'mileage', 'price']
    data = pd.DataFrame(columns=headers)
    
    for _ in range(4098): #set loop according to the number of pages for the given country
        try: #handles th situation if all pages are exhausted before loop ends
            data, next_url = parse_car_details(soup, data)
            soup = get_cars_soup(session, next_url)
            print(data)
        except:
            print("finished scraping")
    
    return data



if __name__=='__main__':
    start_time = datetime.now() #measuring the total execution
    data = main()
    data.to_csv('hungary.csv') #create a csv file to store the respective data
    end_time = datetime.now() 
    total_time = end_time - start_time
    print(f"total time taken: {total_time}")

   





