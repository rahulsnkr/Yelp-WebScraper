from bs4 import BeautifulSoup
import re
import requests
import pandas as pd

# Change this to your desired url
DEFAULT_URL = 'https://www.yelp.com/biz/ocean-ale-house-san-francisco'

# Dictionary to store extra features
feature_dict = {}

# Getting page
r  = requests.get(DEFAULT_URL)
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
price_range = soup.find('dd', attrs={'class' : 'nowrap price-description'}).getText().strip()
feature_dict['price_range'] = price_range

# Getting health score
health_score = soup.find('dd', attrs={'class' : 'nowrap health-score-description'}).getText().strip()
feature_dict['health_score'] = health_score

# Getting extra features
extra_list = soup.find('div', {'class' : 'short-def-list'}).findAll('dl')
for item in extra_list:
    feature = item.find('dt').getText().strip().lower().replace(" ", "_")
    value = item.find('dd').getText().strip()
    feature_dict[feature] = value

# Initializing dataframe
dataset = pd.DataFrame(columns=('restaurant_name', 'address', 'price_range', 'health_score', 'review', 'date', 'rating'))
k = 0

while(current_page <= limit):
    
    # Getting required page and parsing
    url = DEFAULT_URL + '?start=' + str(url_id)
    r  = requests.get(url)
    url_id += 20
    current_page += 1
    data = r.text
    soup = BeautifulSoup(data, 'lxml')

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

# Writing to file
dataset.to_csv('dataset.csv')
