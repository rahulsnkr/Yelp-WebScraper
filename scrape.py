from bs4 import BeautifulSoup
import re
import requests
import pandas as pd

def get_restaurants(URL):
    
    """
        URL - URL of the place for which restaurants are to be scraped
        Returns a list of the URLs of all the restaurants in the given place.
    """
    print("Getting all restaurants")
    # Getting page
    page  = requests.get(URL)
    place_data = page.text

    # Parsing
    place_soup = BeautifulSoup(place_data, 'lxml')

    # Getting total pages
    place_total_pages = place_soup.find('div', {'class' : 'page-of-pages arrange_unit arrange_unit--fill'}).getText()
    place_total_pages = [int(s) for s in place_total_pages.split() if s.isdigit()]
    place_page_limit = place_total_pages[-1]


    restaurant_links = []   # To store links all restaurant of a place

    place_page_url_id = 0
    place_current_page = 1

    while(place_current_page <= place_page_limit):


        # Getting required page ain the given pland parsing
        place_page_url = URL + '&start=' + str(place_page_url_id)
        place_page_r  = requests.get(place_page_url)

        print("Scraping page", place_current_page, "of", place_page_limit)

        place_page_url_id += 30
        place_current_page += 1
        place_page_data = place_page_r.text
        place_soup = BeautifulSoup(place_page_data, 'lxml')

        # Getting lists of all restaurants in that page
        links = place_soup.findAll('li', attrs={'class': 'regular-search-result'})

        # Append list with all restaurant links in that page
        for link in links:
            a_tag = link.find('a', attrs={'class': 'biz-name js-analytics-click'})
            rest_url = 'https://www.yelp.com' + a_tag['href']
            restaurant_links.append(rest_url)

    return restaurant_links



def get_features(URL):
    
    """
        URL - URL of the restaurant for which features are to be scraped.
        Returns a Pandas Dataframe of all the scraped features
    """
    print("Getting all features")
    # Dictionary to store extra features
    feature_dict = {}

    # Getting page
    r  = requests.get(URL)
    data = r.text
    url_id = 0

    # Parsing
    soup = BeautifulSoup(data, 'lxml')

    # Getting total pages
    total_pages = soup.find('div', {'class' : 'page-of-pages arrange_unit arrange_unit--fill'}).getText()
    total_pages = [int(s) for s in total_pages.split() if s.isdigit()]
    limit = total_pages[-1]
    current_page = 1

    # Getting price range
    try:
        price_range = soup.find('dd', attrs={'class' : 'nowrap price-description'}).getText().strip()
        feature_dict['price_range'] = price_range
    except:
        pass

    # Getting health score
    try:
        health_score = soup.find('dd', attrs={'class' : 'nowrap health-score-description'}).getText().strip()
        feature_dict['health_score'] = health_score
    except:
        pass

    # Getting extra features
    try:
        extra_list = soup.find('div', {'class' : 'short-def-list'}).findAll('dl')
        for item in extra_list:
            feature = item.find('dt').getText().strip().lower().replace(" ", "_")
            value = item.find('dd').getText().strip()
            feature_dict[feature] = value
    except:
        pass

    # Initializing dataframe
    dataset = pd.DataFrame(columns=('review', 'date', 'rating'))
    k = 0

    while(current_page <= limit):

        # Getting required page and parsing
        url = URL + '?start=' + str(url_id)
        r  = requests.get(url)
        url_id += 20
        current_page += 1
        data = r.text
        soup = BeautifulSoup(data, 'lxml')
        
        print("Scraping page", current_page, "of", limit)

        # Getting all reviews and ratings
        reviews_ratings = soup.findAll('div', attrs={'class': 'review-content'})

        # Inserting each example into dataset
        for review_rating in reviews_ratings:
            review = review_rating.find('p').getText()
            rating = review_rating.select('div[class*="i-stars i-stars--regular"]')
            rating = float(re.findall("\d+\.\d+", rating[0]['title'])[0])
            date = re.findall("\d+\/\d+\/\d+", review_rating.find('span', attrs={'class' : 'rating-qualifier'}).getText())[0]
            dataset.loc[k] = [review, date, rating]
            k+=1

    # Inserting the extra features
    for key, val in feature_dict.items():
        dataset[key] = val

    return dataset
    
def main():
    
    """
        Main function to scrape data
    """
    
    # Change this to get restaurants of a different place
    PLACE_URL = 'https://www.yelp.com/search?cflt=restaurants&find_loc=Salem%2C+OR'
    
    # Getting all restaurant URLs for the given place
    restaurants = get_restaurants(PLACE_URL)
    
    # DataFrame to hold the final result
    dataset = pd.DataFrame()
    
    # Scraping features for each restaurant
    for restaurant in restaurants:
        dataset = pd.concat([dataset, get_features(restaurant)], ignore_index = True)
        
        # Writing after each iteration in case of any error
        dataset.to_csv('dataset.csv')
        
    # Writing result to file
    dataset.to_csv('dataset.csv')
    
if __name__ == '__main__':
    main()
