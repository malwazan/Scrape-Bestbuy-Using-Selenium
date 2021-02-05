# importing libraries
import re
import time, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import csv


#extract the set of users in a given html page and add them to the given set
link_list=list()			   # store each laptop link
reviews_link_list = list()     # store the links of review page of each laptop
name_list = list()			   # store names of laptops
reviewtext_list=list()
rating_list=list()
date_list=list()
page = 1
review_num = 0

# create csv file using pandas
df = pd.DataFrame({'Laptop Name':name_list,'Review Text':reviewtext_list,'Rating':rating_list, 'Date of Review' : date_list}) 
df.to_csv('reviews.csv', index=False, encoding='utf-8')

####################################################################################  Functions

# get links of all the items on a page
def getItemList(html):
	soup = BeautifulSoup(html, 'html.parser')

	for a in soup.findAll('div', attrs={'class' : 'sku-title'}):
		link = a.find('a', href=True)
		link_list.append("http://www.bestbuy.com"+link['href'])

		s1 = link['href']
		splitted = s1.split('/')
		joined = '/'.join(splitted[2:])
		splitted = joined.split('.')
		joined = splitted[0]
		reviews_link_list.append("http://www.bestbuy.com/site/reviews/"+joined)


def parsePage(html):
	soup_page = BeautifulSoup(html, 'html.parser')
	laptop_name = getName(soup_page)					# it returns name of the laptop
	if (laptop_name == ""):
		pass
	else:
		total_reviews = getReview_Rating_Date(soup_page)    # it all reviews to lists and also return total_no_of_reviews
		#write to file
		if (total_reviews == 0):
			pass
		else:
			for i in range(total_reviews):
				name_list.append(laptop_name)		# Convinience: so that both names list and others list have same number of items


def getName(soup_page):
	name_container = soup_page.find('div', attrs={'class' : 'product-info-container'})
	if (name_container != None):
		name = name_container.find('a', href=True)
		name = name.get_text()
		return name
	else:
		return ""


def getReview_Rating_Date(soup_page):
	reviews_list = soup_page.find('ul', attrs={'class' : 'reviews-list'})
	review_items = reviews_list.findAll('li', attrs={'class' : 'review-item'})   # get list of reviews for each product
	
	if (len(review_items) > 20):
		review_items = review_items[:20]

	if (len(review_items) > 0):
		for review_item in review_items:

			# review rating
			review_rating = review_item.find('div', attrs={'class' : 'review-heading'})
			review_rating = review_rating.find('p')
			#print(review_rating.get_text())    # returns "Rating 5 out of 5 stars with 1 review"
			review_rating = review_rating.get_text()
			review_rating = review_rating.split(' ')
			review_rating = review_rating[1]
			#print(review_rating)
			rating_list.append(review_rating)   # append rating to rating list

			# review date
			review_date = review_item.find('div', attrs={'class' : 'review-context'})
			review_date = review_date.find('time', attrs={'class' : 'submission-date'})
			review_date = review_date['title']
			#print(review_date)
			date_list.append(review_date)		# append review date to date lise

			# review text
			review_text = review_item.find('p', attrs={'class' : 'pre-white-space'})
			review_text = review_text.get_text()
			#print(review_text)
			reviewtext_list.append(review_text)	# append review text to reviewtext list
		return len(reviews_list)
	else:
		return 0   # means that total reviews for particular laptop were 0


def writeDataToCsv():
	frame = pd.DataFrame({'Laptop Name':name_list,'Review Text':reviewtext_list,'Rating':rating_list, 'Date of Review' : date_list})
	frame.to_csv('reviews.csv', mode='a', header=False, index=False, encoding='utf-8')  # mode='a' means to append the data
	name_list.clear()
	reviewtext_list.clear()
	rating_list.clear()
	date_list.clear()

####################################################################################


#main url of the item
start_urls=['https://www.bestbuy.com/site/laptop-computers/all-laptops/pcmcat138500050001.c?cp={0}&id=pcmcat138500050001&intl=nosplash'.format(x) for x in range(1, 47)]   # change cp{} to change page
#open the browser and visit the url
PATH = "C:\\Program Files (x86)\\chromedriver.exe"
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(PATH, options=options)


# create .csv file of all the laptops urls
print("[INFO] creating .csv file of all the laptops urls...")
for url in start_urls:
	# iterate over all the pages and get laptops urls
	driver.get(url)
	#sleep for 2 seconds
	time.sleep(2)
	#get the page url list
	getItemList(driver.page_source)		# Method to collect urls of all the laptops in a list
urls_csv = pd.DataFrame({'Laptops Links':reviews_link_list})
urls_csv.to_csv('all_urls_list.csv', index=False, header=False)
reviews_link_list.clear()
print("[INFO] .csv file created successfully!")


# Load the csv file of all the laptops links
print("[INFO] loading links .csv file...")
with open("all_urls_list.csv", newline='') as f:
	reader = csv.reader(f)
	for row in reader:
		reviews_link_list.append(row[0])
print("Total Number of Links are: " + str(len(reviews_link_list)))


# get name, reviews and rating of each laptop 
for i, link in enumerate(reviews_link_list):
	print ("Scraping:\n"+link)
	driver.get(link)

	parsePage(driver.page_source)  # Method: get name, review, rating, review_date of each laptop in lists

	writeDataToCsv();              # Method: called after getting reviews of every laptop
	print( str(i+1) + " Laptop Data Extracted")





"""
review = "https://www.bestbuy.com/site/reviews/hp-spectre-x360-2-in-1-15-6-4k-uhd-touch-screen-laptop-intel-core-i7-16gb-memory-512gb-ssd-32gb-optane-nightfall-black/6428658"
laptop = "https://www.bestbuy.com/site/        hp-spectre-x360-2-in-1-15-6-4k-uhd-touch-screen-laptop-intel-core-i7-16gb-memory-512gb-ssd-32gb-optane-nightfall-black/6428658.p?skuId=6428658"

https://www.bestbuy.com/site/reviews/microsoft-surface-laptop-3-15-touch-screen-amd-ryzen-5-surface-edition-8gb-memory-128gb-ssd-latest-model-platinum/6374332.p?skuId=6374332
https://www.bestbuy.com/site/reviews/microsoft-surface-laptop-3-15-touch-screen-amd-ryzen-5-surface-edition-8gb-memory-128gb-ssd-latest-model-platinum/6374332?variant=A
"""
