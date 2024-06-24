"""
Outdated, not works
"""

import datetime
import urllib
import psycopg2
from psycopg2.extras import Json as jj
from pyquery import PyQuery as pq

site_url = 'https://www.olx.ua'
url = 'https://www.olx.ua/d/uk/zapchasti-dlya-transporta/avtozapchasti/dvigatel/'
conn = psycopg2.connect(dbname='dbname', user='parser', password='pwd', host='localhost')
conn.autocommit = True


def write_error_information(date_time, setting_id, text, data):
    with conn.cursor() as cursor:
        cursor.execute(f"INSERT INTO parser_bugtracker (date_time, setting_id, text, data) VALUES ('{date_time}', '{setting_id}', '{text}', '{data}')")


def process_one_filter(url, user_id, setting_id, archive_ex, archive_data, full_state):
    try:
        if full_state != 'empty':
            items_titles = []
            items_counter = 0
            d = pq(url=url, opener=lambda url: urllib.request.urlopen(url).read())
            x = list(d("[data-cy='l-card']"))
            items = {}
            for i in x:
                if not 'promoted' in i:
                    link = site_url + d(i).find('a').attr('href')
                    title = d(i).find('h6').text()
                    if not title in archive_data:
                        price = d(i).find("[data-testid='ad-price']").text()
                        location = d(i).find("[data-testid='location-date']").text()
                        image_url = d(i).find(f"[alt='{title}']").attr('srcset')

                        items[link] = {}
                        items[link]['link'] = link
                        items[link]['title'] = title
                        items[link]['price'] = price
                        items[link]['location'] = location
                        items[link]['user_id'] = user_id
                        items[link]['setting_id'] = setting_id
                        items[link]['image_url'] = image_url
                        items_titles.append(title)
                        items_counter += 1

            for j in items.keys():
                d = pq(url=items[j]['link'], opener=lambda url: urllib.request.urlopen(url).read())
                items[j]['image_url'] = d("[data-testid='swiper-image']").attr('src')
                items_titles.append(items[j]['title'])

            for obj in items:
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("INSERT INTO test_subs_results (user_id, sub, setting_id, send_status) VALUES ('%s', %s, '%s', 0)" % (str(user_id), jj(items.get(obj)), str(setting_id)))
                    items_counter += 1
                except Exception as e:
                    print('INSERTING RESULT ERROR: ', str(e))
                    write_error_information(str(datetime.datetime.now()), '-', str(e), 'PY QUERY PARSER - inserting result error')

            # update archive
            try:
                if items_counter > 0:
                    if len(archive_ex) > 0:
                        # get archive len, get items counter
                        # extend archive results with elements in the front (new list extend old list)
                        for t in items_titles:
                            if t not in archive_data:
                                archive_data.append(t)
                        if len(archive_data) > 300:
                            archive_data.reverse()
                            archive_data = archive_data[:200]

                        # rebuild archive json
                        data_list = {'archive': archive_data}
                        # and rewrite
                        with conn.cursor() as cursor:
                            cursor.execute("UPDATE archive_results SET data_list = %s WHERE user_id = '%s' AND setting_id = '%s'" % (jj(data_list), user_id, setting_id))
                    else:
                        # user_id | setting_id | data_list | record_date
                        data_list = {'archive': items_titles}
                        with conn.cursor() as cursor:
                            cursor.execute("INSERT INTO archive_results (user_id, setting_id, data_list, record_date) VALUES ('%s', '%s', %s, '%s')" % (user_id, setting_id, jj(data_list), datetime.datetime.now()))
            except Exception as e:
                print('update error: ', str(e))
                write_error_information(str(datetime.datetime.now()), '-', str(e), 'PY QUERY PARSER - update error')

        elif full_state == 'empty':
            try:
                # add empty dict
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO test_subs_results (user_id, sub, setting_id, send_status, text_note) VALUES ('%s', '{}', '%s', 0, 'Ми знайшли 0 оголошень')" % (str(user_id), str(setting_id)))
            except Exception as e:
                print('Inserting results error: ', str(e))
                write_error_information(str(datetime.datetime.now()), '-', str(e), 'PY QUERY PARSER - INSERTING RESULT ERROR')
    except Exception as e:
        print('Main block returned error: ', str(e))
        write_error_information(str(datetime.datetime.now()), '-', str(e), 'PY QUERY PARSER - Main block error')


process_one_filter(url, '1', '2')
