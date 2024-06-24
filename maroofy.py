"""
Works
"""
import sys
sys.path.append('/usr/local/bin/geckodriver')
import datetime
from io import BytesIO
import json
import time
from PIL import Image
#import psycopg2
#from psycopg2.extras import Json as jj

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By

#conn = psycopg2.connect(dbname='dbname', user='postgres', password='pwd', host='localhost')
#conn.autocommit = True


def write_to_error_log(e, errmsg):
	err = str(e)[:200].replace("'", "~")
	# cursor.execute(f"INSERT INTO error_log (error, dt, source) VALUES ('{err}', '{str(datetime.datetime.now())}', '{errmsg}')")


def init_firefox_driver():
        options = FirefoxOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--incognito")
        options.add_argument('--start-fullscreen')
        profile = FirefoxProfile()
        options.profile = profile
        options.binary_location = '/snap/firefox/current/usr/lib/firefox/firefox'
        driver = webdriver.Firefox(options=options)  #, executable_path='/usr/local/bin/geckodriver')
        driver.implicitly_wait(10)
        driver.fullscreen_window()
        driver.set_window_size(1340, 648)
        return driver


def maroofy(driver, q):
	try:
		driver.get('https://maroofy.com/')
		inp = driver.find_element(By.TAG_NAME, 'input')
		inp.send_keys(q)
		listbox_id = 'react-select-search-async-select-listbox'
		listbox = driver.find_element(By.ID, listbox_id)
		result = {}
		# process "Loading..."
		while 'Loading...' in listbox.get_attribute('innerHTML'):
			time.sleep(5)

		# process results
		for div in listbox.find_elements(By.CLASS_NAME, 'text-sm'):
			try:
				p = div.find_element(By.XPATH, '..')
				song_title = div.text
				album = p.find_element(By.TAG_NAME, 'p').text
				p.click()
				time.sleep(1)
				# get results
				div1 = driver.find_element(By.CLASS_NAME, 'bg-white')
				items = div1.find_elements(By.TAG_NAME, 'h6')
				tracks_counter = 0
				for item in items:
					if tracks_counter == 20:
						return result
					else:
						try:
							h = item.text
							p = item.find_element(By.XPATH, '..').find_element(By.TAG_NAME, 'p').text
							h = h.replace("'", "")
							p = p.replace("'", "")
							result[h] = p
							tracks_counter += 1
						except:
							pass
			except Exception as e:
				print('Processing results iteration error: ', str(e))
	except Exception as e:
		print('Function Maroofy() got an error: ', str(e))

	return result


def process_links(driver, result):
        nextresult = []
        for item in result:
                try:
                        link = item[0]
                        driver.get(link)
                except Exception as e:
                        print('Processing link got an error: ', str(e))
                        nextresult.append([None, item[1]])
        return nextresult


def get_result_links(driver, result):
	links = {}
	keys = [x for x in result.keys()]
	for k in keys:
		try:
			title = k.replace('&', '').replace('?', '').replace('/', '').replace('\\', '')
			artist = result[k].replace('&', '').replace('?', '').replace('/', '').replace('\\', '')
			print(f'Process item. title: {title} | artist: {artist}')
			prepare_url = 'https://moodplaylist.com/songnew.php?results?search_query=' + title + 'by' + artist + '&song=1'
			driver.get(prepare_url)
			time.sleep(2)
			curl = driver.current_url
			if '###' in curl:
				curl = curl.split('###')[-1]
				if '&song' in curl:
					curl = curl.split('&song=')[0]
					links[title + ' _by_ ' + artist] = curl
		except Exception as e:
			print('Get result links error: ', str(e))
			write_to_error_log(e, 'Get result links error: ')
	return links


def test_maroofy():
	driver = None
	try:
		driver = init_firefox_driver()
	except Exception as e:
		print('First driver initialization returned error: ', str(e))
		write_to_error_log(e, 'First driver initialization returned error:')
		try:
			driver = init_firefox_driver()
		except Exception as e:
			print('Second driver initialization returned error: ', str(e))
			write_to_error_log(e, 'Second driver initialization returned error:')
			return False

	if driver:
		try:
			result = maroofy(driver, q='eminem stan')
			links = get_result_links(driver, result)
			print('Result: ', result)
			print('Links: ', links)
		except Exception as e:
			print('MAIN block error: ', str(e))
			write_to_error_log(e, 'Main block error:')
		finally:
			driver.quit()


test_maroofy()
