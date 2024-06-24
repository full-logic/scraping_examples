"""
Works. "rezka.ag" may not be work in Ukraine
"""
import datetime
from io import BytesIO
import json
# import psycopg2
# from psycopg2.extras import Json as jj
import random
import sys
sys.path.append('/usr/local/bin/geckodriver')
import time
from PIL import Image

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By

#conn = psycopg2.connect(dbname='dbname', user='postgres', password='pwd', host='localhost')
#conn.autocommit = True


def make_screen(driver):
	try:
		p = driver.find_element(By.TAG_NAME, 'body').screenshot_as_png
		x = Image.open(BytesIO(p))
		s_p = 'screen__' + str(random.randint(11, 211)) + '_screen.png'
		x.save(s_p)
		print('NEW DRIVER SCREEN: ', s_p)
		time.sleep(1)
	except Exception as e:
		print('Make screen error: ', str(e))


def init_firefox_driver():
        options = FirefoxOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--incognito")
        options.add_argument('--start-fullscreen')
        profile = FirefoxProfile()
        options.profile = profile
        options.binary_location = '/snap/firefox/current/usr/lib/firefox/firefox'
        driver = webdriver.Firefox(options=options)
        driver.implicitly_wait(10)
        driver.fullscreen_window()
        driver.set_window_size(1340, 648)
        return driver


def collect_film_data(driver, films):  # films: [[query_id, phrase],]
	collect_info_errors = []
	output = {}
	search_url = 'https://rezka.ag/search/?do=search&subaction=search&q='

	if driver:
		for mv in films:
			try:
				driver.get(search_url + mv)
				time.sleep(2)
				results = True
				items_q = None
				try:
					res_els = driver.find_element(By.CLASS_NAME, 'b-content__search_wrapper').find_element(By.CLASS_NAME, 'b-content__inline_items').find_elements(By.CLASS_NAME, 'b-content__inline_item')
				except Exception as e:
					print('ERROR. Result elements: ', str(e))
					results = False
					collect_info_errors.append('Error result elements: ' + str(e))

				if results:
					if res_els:
						item = res_els[0]
						try:
							mv_prep = mv.replace("'", "")
							ru_name = item.find_element(By.CLASS_NAME, 'b-content__inline_item-link').find_element(By.TAG_NAME, 'a').text
							img_link = item.find_element(By.CLASS_NAME, 'b-content__inline_item-cover').find_element(By.TAG_NAME, 'img').get_attribute('src')
							year = item.find_element(By.CLASS_NAME, 'b-content__inline_item-link').find_element(By.TAG_NAME, 'div').text
							x = {'ru_name': ru_name, 'img_link': img_link, 'year': year}
							x = json.dumps(x)
							output[mv_prep] = x
							#with conn.cursor() as cursor:
							#	cursor.execute(f"INSERT INTO films_history (title, result) VALUES ('{mv_prep}', '{x}')")
						except Exception as e:
							make_screen(driver)
							print('Process video-card error: ', str(e))

			except Exception as e:
				print('Error: Take one movie results | ', str(e))
				collect_info_errors.append('Error: Take one movie results: ' + str(e))

	return output, collect_info_errors


def search_film_by_phrase(phrase):
	errors = []
	output = {}
	driver = None
	try:
		driver = init_firefox_driver()
	except Exception as e:
		try:
			driver = init_firefox_driver()
		except Exception as e:
			errors.append('Search films by a phrase, init driver error: ' + str(e))

	if driver:
		try:
			driver.get('http://www.whatismymovie.com/results?text=' + phrase)
			time.sleep(1)
			try:
				# click to confirm terms
				driver.find_element(By.ID, 'acceptterms').click()
			except Exception as e:
				pass

			items = driver.find_element(By.CLASS_NAME, 'result-container')
			r = []
			if items:
				titles = items.find_elements(By.TAG_NAME, 'a')
				counter = 0
				process_range = round(len(titles) / 2)
				if process_range == 0:
					process_range = 1

				for i in range(process_range):
					try:
						if '(' and ')' in titles[i].get_attribute('text'):
							r.append(titles[i].get_attribute('text'))
					except:
						pass

					if len(r) >= 10:
						break

			if r:
				# collect info about films, prepare to call function
				time.sleep(2)
				prepared_r = []
				for f in r:
					prepared_r.append(' '.join(f.split(' ')[:-1]))
				output, errors_arr = collect_film_data(driver, prepared_r)  # output {}
				errors.extend(errors_arr)
				dump_output = json.dumps(output)
				#with conn.cursor() as cursor:
				#	cursor.execute(f"INSERT INTO search_history (query, result) VALUES ('{phrase}', '{dump_output}')")
			else:
				errors.append('Whole iteration running without results. Phrase: ' + str(phrase))
				make_screen(driver)

		except Exception as e:
			print('Search films by a phrase, iteration error: ', str(e))
			error.append('Search films by a phrase, iteration error: ', str(e))
		finally:
			driver.quit()

	if errors:
		output = prepared_r  # if rezka.ag called exception

	return output, errors


output, errors = search_film_by_phrase('stiflers mom')
#print('Output: ', output)
print('Errors: ', errors)
print()
print('Output: ', output)
