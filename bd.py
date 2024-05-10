import psycopg2
import config
from datetime import datetime

#Класс для подключения к базе данных
class BDRequests():

    #Установка соединения
    def __init__(self):
        self.connection = psycopg2.connect(
            host=config.HOST,
            database=config.DATABASE,
            user=config.USER,
            password=config.PASSWORD,
            client_encoding='utf8'
        )

    def __del__(self):
        self.connection.close()

    def insert_task(self, date, text, image_id, sticker_id, job_id):
        cursor = self.connection.cursor()
        insert_query = f'INSERT INTO public."{config.TABLENAME}" (date_post, text_post, image_id, sticker_id, job_id) VALUES (%s, %s, %s, %s, %s);'
        cursor.execute(insert_query, (date, text, image_id, sticker_id, job_id))
        self.connection.commit()

    def update_job_id(self, id, job_id):
        cursor = self.connection.cursor()
        update_query = f'UPDATE public."{config.TABLENAME}" SET job_id = %s WHERE id = %s;'
        cursor.execute(update_query, (job_id, id))
        self.connection.commit()

    def delete_old(self):
        cursor = self.connection.cursor()
        delete_query = f'DELETE FROM public."{config.TABLENAME}" WHERE date_post < %s;'
        cursor.execute(delete_query, (datetime.now(), ))
        self.connection.commit()

    def delete_by_id(self, id):
        cursor = self.connection.cursor()
        delete_query = f'DELETE FROM public."{config.TABLENAME}" WHERE id = %s;'
        cursor.execute(delete_query, (id, ))
        self.connection.commit()

    def select_by_id(self, id):
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT date_post, job_id FROM public."{config.TABLENAME}" WHERE id = %s;', (id,))
        result = cursor.fetchall()[0]
        return result

    def select_all(self):
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT * FROM public."{config.TABLENAME}" ORDER BY date_post')
        result = cursor.fetchall()
        return result
