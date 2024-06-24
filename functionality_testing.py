"""
local listing, tests
"""

print('Run tests')

from instagram_tiktok import insta_tiktok
from bigjpg_api import send_request as image_request
from ai2 import test_ai2 as run_ai2_test
from ai3 import run_ai3 as run_ai3_test

from urllib3.util.retry import Retry
import os
import json
import requests
from pytube import YouTube
from requests.adapters import HTTPAdapter
import urllib
import datetime

import psycopg2

conn = psycopg2.connect(dbname='musicbot_new', user='postgres', password='ducasslepwd1', host='localhost')
conn.autocommit = True

channel_chat_id = '-1111111111111'
yt_test_video = 'https://www.youtube.com/watch?v=GxkLy_mvGXE'
yt_video_filename = "Walk On Water.mp4"
filename = 'testimage.jpg'


def run_tests():
	print('---STAGE 1: DOWNLOAD MEDIA FROM YouTube and TikTok')
	test_results = []
	try:
		test_results.append('<b>YouTube download library №1</b>')
		file_path = YouTube(str(yt_test_video)).streams.filter(progressive=True, file_extension='mp4').first().download()
		pytube_existing = os.path.exists(yt_video_filename) or 'Walk On Water' in file_path
		if pytube_existing:
			test_results.append('\n<b>+</b> YouTube download library №1 works')
			os.remove(yt_video_filename)
		else:
			test_results.append('\n<b>!</b> YouTube download library №1 not work or work with errors')

		test_results.append('\n\n')

	except Exception as e:
		err = str(e)[:200].replace("'", "")
		err.replace('"', '')
		with conn.cursor() as cursor:
			cursor.execute(f"INSERT INTO error_log (error, dt, source) VALUES ('{err}', '{str(datetime.datetime.now())}', 'Run tests for YouTube download library №1 error')")

	test_results.append('\n\n')

	try:
		test_results.append('<b>YouTube download library №2</b>')
		os.system(f'yt-dlp -S "res:480" --id {yt_test_video}')
		name_by_id = "GxkLy_mvGXE"
		folder_files = os.listdir('/filepath')
		yt_dlp_find = False
		for f in folder_files:
			if name_by_id in f:
				os.remove('/filepath' + f)
				yt_dlp_find = True

		if yt_dlp_find:
			test_results.append('\n<b>+</b> YouTube download library №2 works')
		else:
			test_results.append('\n<b>!</b> YouTube download library №2 not work or work with errors')

		test_results.append('\n\n')

	except Exception as e:
		err = str(e)[:200].replace("'", "")
		err.replace('"', '')
		with conn.cursor() as cursor:
			cursor.execute(f"INSERT INTO error_log (error, dt, source) VALUES ('{err}', '{str(datetime.datetime.now())}', 'Run tests for YouTube download library №2 error')")

	try:
		# Testing TikTok
		test_results.append('<b>TikTok download library</b>')
		tiktok_url = 'https://vm.tiktok.com/ZMMGgaFs1/'
		url_tt = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
		headers_tt = {
			'x-rapidapi-host': "tiktok-video-no-watermark2.p.rapidapi.com",
			'x-rapidapi-key': "87ac85beddmshe96279a2bb70030p155f76jsn0e459bc81d4e"
		}
		err = False
		try:
			session = requests.Session()
			retry = Retry(connect=3, backoff_factor=0.5)
			adapter = HTTPAdapter(max_retries=retry)
			session.mount('http://', adapter)
			session.mount('https://', adapter)
			querystring_tt = {"url":tiktok_url,"hd":"0"}
			response = session.get(url_tt, headers=headers_tt, params=querystring_tt)
			response_dict = json.loads(response.text)
		except Exception as e:
			print('TikTok test run error: ', str(e))
			err = True
		if not err:
			try:
				url_link = response_dict.get('data').get('play')
				filepath = 'temp_tiktok_storage/test_tt.mp4'
				urllib.request.urlretrieve(url_link, filepath)
			except Exception as e:
				err = True
				test_results.append('\n<b>!</b> TikTok video find but was not loaded to the server')

		if not err:
			filepath = 'temp_tiktok_storage/test_tt.mp4'
			if os.path.exists(filepath):
				os.remove(filepath)
				test_results.append('\n<b>+</b> TikTok downloading works')
		elif err:
			test_results.append('\n<b>!</b> TikTok downloading not work. Request failed')
	except Exception as e:
		err = str(e)[:200].replace("'", "")
		err.replace('"', '')
		with conn.cursor() as cursor:
			cursor.execute(f"INSERT INTO error_log (error, dt, source) VALUES ('{err}', '{str(datetime.datetime.now())}', 'Error while testing downloading from TikTok')")

	test_results.append('\n\n')

	print('---STAGE 2: NEURAL NETWORKS')
	try:
		downloaded, errors, filename = image_request('photo', '0', '1', 'testimage.jpg', 'testimage.jpg')
		test_results.append('<b>Neural network for improve images quality</b>')
		if downloaded == True:
			test_results.append('\n<b>+</b> Neural network for improve images quality works')
		elif downloaded == False:
			test_results.append('\n<b>!</b> Neural network for improve images quality not work or work with errors')
		if len(errors) > 0:
			test_results.append('\n<b>+</b> Neural network for improve images quality not work or work with errors')
			ai1_output = ''
			for i in errors:
				ai1_output += '\nError of working network 1 (imporve image quality) by test: ' + str(i)
		if filename:
			os.remove(filename)

		test_results.append('\n\n')

	except Exception as e:
		err = str(e)[:200].replace("'", "")
		err.replace('"', '')
		with conn.cursor() as cursor:
			cursor.execute(f"INSERT INTO error_log (error, dt, source) VALUES ('{err}', '{str(datetime.datetime.now())}', 'Error while testing neural network for improve images quality')")
	try:
		test_results.append('<b>Neural network to search films by phrase</b>')
		output, errors, queue_execution_timer = run_ai2_test()
		if len(errors) == 0:
			if len(output.keys()) > 0:
				data = output.get('0')
				if len(data.keys()) > 0:
					# all right
					test_results.append('\n<b>+</b> Neural network to search films by phrase works')
				else:
					test_results.append('\n<b>!</b> Neural network to search films by phrase works but result was not sended to user')
			else:
				test_results.append('\n<b>!</b> Neural network to search films by phrase not work or work with errors')
		else:
			test_results.append('\n<b>!</b> Neural network to search films by phrase not work or work with errors')

		test_results.append('\n\n')

	except Exception as e:
		err = str(e)[:200].replace("'", "")
		err.replace('"', '')
		with conn.cursor() as cursor:
			cursor.execute(f"INSERT INTO error_log (error, dt, source) VALUES ('{err}', '{str(datetime.datetime.now())}', 'Error while testing neural network for films searching')")

	try:
		test_results.append('<b>Copywriter neural network</b>')
		result = run_ai3_test(test_call=True)  # [is_success, data]
		if result is not None:
			data = result[1]
			if data.get('success') == True:
				test_results.append('\n<b>+</b> Copywriter neural network works')
			else:
				test_results.append('\n<b>!</b> Copywriter neural network not work or work with errors')
		else:
			test_results.append('\n<b>!</b> Copywriter neural network not work or work with errors')

		test_results.append('\n\n')

	except Exception as e:
		err = str(e)[:200].replace("'", "")
		err.replace('"', '')
		with conn.cursor() as cursor:
			cursor.execute(f"INSERT INTO error_log (error, dt, source) VALUES ('{err}', '{str(datetime.datetime.now())}', 'Error while testing copywriter neural network')")

	try:
		# output the results
		output = ''
		for line in test_results:
			output += line
		with conn.cursor() as cursor:
			cursor.execute("DELETE FROM testing_log")  # delete old test results
			cursor.execute(f"INSERT INTO testing_log (dt, output) VALUES ('{str(datetime.datetime.now())}', '{output}')")
	except Exception as e:
		err = str(e)[:200].replace("'", "")
		err.replace('"', '')
		with conn.cursor() as cursor:
			cursor.execute(f"INSERT INTO error_log (error, dt, source) VALUES ('{err}', '{str(datetime.datetime.now())}', 'Error while preparing test result')")

	return output

run_tests()
