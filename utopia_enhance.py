"""
Works
"""
import sys
sys.path.append('/usr/local/bin/geckodriver')
import datetime
from io import BytesIO
import json
import random
import time
from PIL import Image
#import psycopg2
#from psycopg2.extras import Json as jj

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#conn = psycopg2.connect(dbname='dbname', user='postgres', password='pwd', host='localhost')
#conn.autocommit = True


def make_screen(driver):
	try:
		p = driver.find_element(By.TAG_NAME, 'body').screenshot_as_png
		x = Image.open(BytesIO(p))
		s_p = 'screen__' + str(random.randint(11, 211)) + '_screen.png'
		x.save(s_p)
		print('NEW DRIVER SCREEN: ', s_p)
		time.sleep(5)
	except Exception as e:
		print('Make screen error: ', str(e))


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
        driver = webdriver.Firefox(options=options)
        driver.implicitly_wait(10)
        driver.fullscreen_window()
        driver.set_window_size(1340, 648)
        return driver


def run_utopia_enhance(driver, url):
	try:
		driver.get('https://enhance.utopiamusic.com/analysis?weblink=' + url)
		time.sleep(10)
		main = driver.find_element(By.TAG_NAME, 'main')
		ul = main.find_element(By.TAG_NAME, 'ul')
		e = main.find_element(By.TAG_NAME, 'div').find_element(By.TAG_NAME, 'h2')
		try:
			element = WebDriverWait(driver, 200).until_not(EC.text_to_be_present_in_element((By.TAG_NAME, 'h2'), 'Fetching data...'))
		except Exception as e:
			print('Get data error: ', str(e))
			make_screen(driver)
			return False

		song_title = e.text
		additional_data = {}
		genres_data = {}

		if song_title:
			genres_data['song_title'] = song_title

		for div in ul.find_elements(By.CLASS_NAME, 'gap-4'):
			for item in div.find_elements(By.TAG_NAME, 'li'):
				key, value = item.find_elements(By.TAG_NAME, 'div')
				additional_data[key.text.lower()] = value.text.lower()

		genres_ct = main.find_element(By.XPATH, "//h3[text()='Genres']").find_element(By.XPATH, '..')
		parameters = genres_ct.find_element(By.TAG_NAME, 'ul')
		for li in parameters.find_elements(By.TAG_NAME, 'li'):
			try:
				genre = li.find_element(By.TAG_NAME, 'p').text
				value_ct = li.find_element(By.TAG_NAME, 'div')
				value = li.find_element(By.TAG_NAME, 'span').text
				genre_information = value_ct.find_element(By.TAG_NAME, 'p').get_attribute("textContent")
				genres_data[genre] = {'info': genre_information, 'value': value}
			except Exception as e:
				print('Iteration error: ', str(e))
	except Exception as e:
		print("Utopia run no-result or try-again")
		write_to_error_log(e, 'Utopia run no-result or try-again:')
		make_screen(driver)
		return 'no-result'
	return [song_title, genres_data, additional_data]


def requests_to_utopia_enhance(test_query=None):
	result = {}
	driver = None
#	with conn.cursor() as cursor:
	try:
		#cursor.execute(f"select chat_id, url, ident from requests where status='full'")
		#res = cursor.fetchall()
		res = [[1, test_query, '1']]
		if res:
			# driver initialization
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

			for item in res:  # process users requests
				genres_data = {'status': 'not-found'}
				try:
					print('Item: ', item)
					chat_id, url, query_ident = item[0], item[1], item[2]
					data = run_utopia_enhance(driver, url)
					print('Data: ', data)
					if data == 'no-result':
						genres_data['status'] = 'no-results'
					else:
						song_title, genres_data, additional_data = data[0], data[1], data[2]
				except Exception as e:
					print('Returned error while music genre recogniton: ', str(e))
					write_to_error_log(e, 'Returned error while music genre recogniton.\nURL: {url}\n')
					make_screen(driver)

				# result = jj(genres_data)  # dump json to save using psycopg2 method
				# cursor.execute(f"INSERT INTO results (chat_id, url, result) VALUES ('{chat_id}', '{url}', {result})")
				# cursor.execute(f"DELETE FROM requests WHERE chat_id = '{chat_id}' AND ident = '{query_ident}'")
	except Exception as e:
		print('RUN_UTOPIA_ENHANCE ERROR: ', str(e))
		write_to_error_log(e, 'RUN_UTOPIA_ENHANCE ERROR')

	if test_query:
		print(result)
	if driver:
		driver.quit()


requests_to_utopia_enhance(test_query='https://www.youtube.com/watch?v=4VxdufqB9zg')