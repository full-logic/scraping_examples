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

#conn = psycopg2.connect(dbname='dbname', user='postgres', password='pwd', host='localhost')
#conn.autocommit = True


def write_to_error_log(e, errmsg):
	err = str(e)[:200].replace("'", "~")
	# cursor.execute(f"INSERT INTO error_log (error, dt, source) VALUES ('{err}', '{str(datetime.datetime.now())}', '{errmsg}')")


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


def test_video_url_that_unavailable(driver):
	# step1: test is video unavailable with wrong url
	test_video_url = 'https://www.tiktok.com/@pharell/video/7250554180719496453456?_r=1&_t=8dbcEw1ZqjO'
	try:
		driver.get(test_video_url)
	except Exception as e:
		try:
			driver.get(test_video_url)
		except Exception as e:
			print('test_video_url_that_unavailable get url error: ', str(e))
			write_to_error_log(e, 'test_video_url_that_unavailable, get url error')
			return False

	page = driver.page_source.splitlines()
	for line in page:
		if "Video currently unavailable" in line:
			unavailable = True
			return True


def is_wrong_url_profile_exists(driver):
	# Step 2: test is profile exists with wrong url
	not_ch_url = 'https://www.tiktok.com/@aaiqn1lmka'
	try:
		driver.get(not_ch_url)
	except Exception as e:
		try:
			driver.get(not_ch_url)
		except Exception as e:
			print('is_wrong_url_profile_exists get url error: ', str(e))
			write_to_error_log(e, 'is_wrong_url_profile_exists, get url error')
			return False

	for line in driver.page_source.splitlines():
		if "Couldn't find this account" in line:
			not_found_profile = True
			return True


def get_channel_title_test(driver):
	# Step 3: get channel title
	ch_url = 'https://www.tiktok.com/@pharrell'
	try:
		driver.get(ch_url)
	except Exception as e:
		try:
			driver.get(ch_url)
		except Exception as e:
			print('E: ', str(e))
			write_to_error_log(e, 'get_channel_title_test, get url error')
			return False
	try:
		title = driver.find_element(By.XPATH, "//h1[@data-e2e='user-title']").text
		return True
	except Exception as e:
		write_to_error_log(e, 'get_channel_title_test, get title error')
		return False


def get_link_to_profile_by_video(driver):
	# Step 4: get link to profile by video url
	active_video_url = 'https://vm.tiktok.com/ZM25gHeaQ/'
	try:
		driver.get(active_video_url)
	except Exception as e:
		try:
			driver.get(active_video_url)
		except Exception as e:
			write_to_error_log(e, 'get_link_to_profile_by_video, get url error')
			return False
	try:
		username = driver.find_element(By.XPATH, "//span[@data-e2e='browse-username']")
		link_to_profile = username.find_element(By.XPATH, '..').get_attribute('href')
	except Exception as e:
		write_to_error_log(e, 'get_link_to_profile_by_video, get username or link_to_profile error')
		return False


def profile_video_urls_collection(driver):
	# Step 5: profile url's collection
	ch_url = 'https://www.tiktok.com/@pharrell'
	collection = {}
	try:
		driver.get(ch_url)
	except Exception as e:
		print('E: ', str(e))
		try:
			driver.get(ch_url)
		except Exception as e:
			write_to_error_log(e, 'profile_video_urls_collection, get url error')
			return False
	try:
		x = driver.find_element(By.XPATH, "//div[@data-e2e='user-post-item-list']").find_elements(By.TAG_NAME, "a")
	except Exception as e:
		make_screen(driver)
		write_to_error_log(e, 'profile_video_urls_collection, get user post list error')
		print('profile_video_urls_collection, get user post list error: ', str(e))
		return False
	else:
		for i in x:
			try:
				if 'video' in i.get_attribute('href'):
					title = i.get_attribute('title')
					href = i.get_attribute('href')
					if href:
						if title == '':
							title = 'no_title'
						collection[href] = title
			except Exception as e:
				write_to_error_log(e, 'profile_video_urls_collection, get tiktok video url iter error')

	print('Collection: ', collection)
	return True


def test(driver):
	test_results = {}
	# expected behavior
	test_results['test unavailable video url'] = test_video_url_that_unavailable(driver)
	test_results['is wrong profile exists'] = is_wrong_url_profile_exists(driver)
	test_results['get channel title'] = get_channel_title_test(driver)
	test_results['get link to profile from video page'] = get_link_to_profile_by_video(driver)
	test_results['profile video urls collection'] = profile_video_urls_collection(driver)
	print('Test results: ', test_results)
	return True


driver = None
try:
	driver = init_firefox_driver()
except Exception as e:
	write_to_error_log(e, 'Test TikTok, driver not started')

if driver:
	try:
		result = test(driver)
	except:
		pass
	finally:
		driver.quit()
else:
	write_to_error_log(e, 'TikTok testing failed')

