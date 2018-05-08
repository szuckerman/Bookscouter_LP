import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import time
import pandas as pd


# This is the same filename that gets output at the end. We're using it here in case someone wants to run the scraper
# again and keep the same file structure. Even if this is one's first time running the scraper, he should make sure
# that the CSV has at least one column titled ISBN containing the ISBNs to scrape.
bookscouter_dat = pd.read_csv('bookscouter_dat.csv')
bookscouter_isbns = set(bookscouter_dat.ISBN)

url = 'https://bookscouter.com/sell/%s'

opts = Options()
opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36")
driver = webdriver.Chrome(chrome_options=opts)


def clean_each_bookstore_list(isbn, my_list):
	'''
	This function takes a list of bookstores, ratings and prices (as provided by Bookscouter.com) and cleans up errors (i.e. puts errors as $0.00).
	It also appends the ISBN searched for to the list to determine the price for said book in each bookstore.

	Params:
		isbn: string
		my_list: 3-element list

	Returns:
		new_list: 3-element list
	'''
	new_list = [isbn, my_list[0], my_list[2]]
	if '$' in new_list[2]:
		new_list[2] = float(new_list[2][1:])
	elif new_list[2] == 'Not Currently Buying':
		new_list[2] = 0.0
	else:
		new_list[2] = 0.0
	return new_list


def put_bookstore_results_in_list(results, sublist_size):
	results_list = results.text.split('\n')[1:]
	results_list2 = [item for item in results_list if item not in ['SELL', 'SHOW MORE VENDORS']]
	composite_list = [results_list2[x:x+sublist_size] for x in range(0, len(results_list2),sublist_size)]
	return composite_list


def get_data_from_page():
	global driver
	book_title = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "book__title")))
	results = driver.find_element_by_class_name('results')
	img_loc = driver.find_element_by_class_name('book__img-container').find_element_by_tag_name('img').get_attribute('src')
	return book_title, results, img_loc


def get_isbn_data(isbn):
	'''
	Params:
		isbm : string

	Returns:
		titles_df: A Pandas DataFrame of basic ISBN metadata. It contains the IMG link for the book, the ISBN and its title.
		results_df: A Pandas DataFrame containing the associated prices paid out by bookstore.
	'''
	global driver
	sublist_size=3
	time.sleep(1)
	response = driver.get(url % isbn)
	book_title, results, img_loc = get_data_from_page()
	titles_df = pd.DataFrame({'ISBN': isbn, 'TITLE': book_title.text, 'IMG': img_loc}, index=[0])
	composite_list = put_bookstore_results_in_list(results, sublist_size)
	results_df = pd.DataFrame([clean_each_bookstore_list(isbn, subset) for subset in composite_list], columns = ['ISBN', 'STORE', 'PRICE'])
	return titles_df, results_df


metadata_df = pd.DataFrame(columns=['ISBN', 'TITLE', 'IMG'])
results_df = pd.DataFrame(columns=['ISBN', 'STORE', 'PRICE'])


# In case the scraping breaks and we need to start over, but want to keep where we left off.
books_finished = set()


count_books = 0
for isbn in bookscouter_isbns.difference(books_finished):
	count_books += 1
	if not count_books%10:
		print('\nTaking a little break. Waking up in 30 seconds.\n')
		time.sleep(30)
	print("Running scraper for book: %s" % isbn)
	metadata_temp, results_temp = get_isbn_data(isbn)
	print("Completed results for book: %s (Title: %s)" % (isbn, metadata_temp.TITLE.iloc[0]))
	metadata_df = pd.concat([metadata_df, metadata_temp])
	results_df = pd.concat([results_df, results_temp])
	results_df = results_df[results_df.PRICE > 0]


books_finished = set(metadata_df.ISBN)


merged_results = results_df.merge(metadata_df)
merged_results.to_csv('bookscouter_results.csv', index=False)
