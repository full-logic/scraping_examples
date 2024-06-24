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
from moodplaylist_data import mood_data, era_data, activity_data

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


def select_mood(driver, q):
	try:
		input_mood_el = driver.find_element(By.ID, 'form-mood')  # select
		p = input_mood_el.find_element(By.XPATH, '..')
		p.find_element(By.CLASS_NAME, 'select2-selection').click()
		driver.find_element(By.CLASS_NAME, 'select2-search__field').send_keys(q)
		driver.find_element(By.ID, 'select2-form-mood-results').find_element(By.XPATH, f"//li[text()='{q.capitalize()}']").click()
	except Exception as e:
		return False
	return True


def select_era(driver, q):
	try:
		input_era_el = driver.find_element(By.ID, 'form-era')  # select
		p = input_era_el.find_element(By.XPATH, '..')
		p.find_element(By.CLASS_NAME, 'select2-selection').click()
		driver.find_element(By.CLASS_NAME, 'select2-search__field').send_keys(q)
		driver.find_element(By.ID, 'select2-form-era-results').find_element(By.TAG_NAME, 'li').click()
	except Exception as e:
		return False
	return True


def select_activity(driver, q):
	try:
		input_activity_el = driver.find_element(By.ID, 'form-activity')  # select
		p = input_activity_el.find_element(By.XPATH, '..').find_elements(By.CLASS_NAME, 'select2')[-1]
		p.find_element(By.CLASS_NAME, 'select2-selection').click()
		driver.find_element(By.CLASS_NAME, 'select2-search__field').send_keys(q)
		driver.find_element(By.ID, 'select2-form-activity-results').find_element(By.TAG_NAME, "li").click()
	except Exception as e:
		return False
	return True


def extract_values(mood, activity):
	e_mood = None
	e_activity = None
	keys = [str(x) for x in activity_data.keys()]
	for k in keys:
		if activity_data[k].get('short') == activity:
			e_activity = k
	keys = [str(x) for x in mood_data.keys()]
	for k in keys:
		if mood_data[k].get('short') == mood:
			e_mood = k
	return e_mood, e_activity


def get_id_from_string(info):  # collect match numbers from the string to get element id value
	numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
	res = ''
	for i in list(info):
		try:
			if i in numbers:
				res += i
		except:
			pass
	return res


def moodplaylist(driver, mood, era, activity):
	try:
		driver.get('https://moodplaylist.com/')
		mood = select_mood(driver, mood)
		era = select_era(driver, era)
		activity = select_activity(driver, activity)
		if mood and era and activity:
			go_btn = driver.find_element(By.ID, 'gift-search')
			go_btn.click()

			result = []
			try:
				time.sleep(11)
				driver.execute_script("window.scroll({top: 20500, left: 0, behavior: 'smooth'});")
				time.sleep(4)
			except Exception as e:
				print('Scrolling error: ', str(e))
				write_to_error_log(e, 'Scrolling error:')
				make_screen(driver)

			songs_ct = driver.find_elements(By.CLASS_NAME, 'songtitlestyle')
			for sc in songs_ct:
				id = sc.get_attribute('id').replace("'", "\'")
				text = sc.text.replace("'", "\'")
				number_of_frame = get_id_from_string(id)
				video_player_id = 'giftselection' + str(number_of_frame)
				link = None
				try:
					vp_el = driver.find_element(By.ID, video_player_id)
					if vp_el:
						link = vp_el.get_attribute('src')
					else:
						print('Videoplayer element not found')
				except Exception as e:
					print('Process song iteration error: ', str(e))
					write_to_error_log(e, 'Process song iteration error:')
					make_screen(driver)

				result.append([link, text])
	except Exception as e:
		return 'error'
	else:
		return result


def process_links(driver, result):  # make links pretty
	nextresult = []
	for item in result:
		try:
			link = item[0]
			if link:
				driver.get(link)
				time.sleep(1)
				curl = driver.current_url
				if '###' in curl:
					curl = curl.split('###')[-1]
					if '&song' in curl:
						curl = curl.split('&song=')[0]
			else:
				curl = ''
			nextresult.append([curl, item[1]])
		except Exception as e:
			print('Iter error: ', str(e))
			nextresult.append([None, item[1]])
			write_to_error_log(e, 'Process links iteration error:')

	return nextresult


def moodplaylist_requests(test_query=None):
	driver = None
	try:
#		with conn.cursor() as cursor:
#		cursor.execute(f"SELECT * FROM requests WHERE status='full'")
#		res = cursor.fetchall()
#		if res:
		if test_query:
			res = test_query
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
			for q in res:
				try:
					chat_id, ident, era, status = q[0], q[1], q[3], q[5]
					mood, activity = extract_values(q[2], q[4])
					result = {}
					if status != 'full':
						result['status'] = 'not-full-request'
					else:
						data = moodplaylist(driver, mood, era, activity)
						if data == 'error':
							result['status'] = 'error'
						else:
							result[chat_id] = process_links(driver, data)
					#dumped_result = jj(result)
					# cursor.execute(f"INSERT INTO results (chat_id, ident, result) VALUES ('{chat_id}', '{ident}', {dumped_result})")
					# cursor.execute(f"DELETE FROM requests WHERE chat_id='{chat_id}' AND ident='{ident}'")
				except Exception as e:
					print('One q iteration returned error: ', str(e))
					write_to_error_log(e, 'One q iteration error:')
	except Exception as e:
		write_to_error_log(e, 'MOODPLAYLIST MAIN BLOCK ERROR')
	finally:
		driver.quit()

	if test_query:
		print(result)

	return True


test_query = [['1', '48a1a756f2d83f1dc57bbf14052b70a6f40d0fce', 'happ', '2000', 'trav', 'full']]
moodplaylist_requests(test_query)
