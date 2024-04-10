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
            password=config.PASSWORD
        )

    def __del__(self):
        self.connection.close()

    def insert_task(self, date, text):
        cursor = self.connection.cursor()
        insert_query = f'INSERT INTO public."{config.TABLENAME}" (date_post, text_post) VALUES (%s, %s);'
        cursor.execute(insert_query, (date, text))
        self.connection.commit()

    def delete_old(self):
        cursor = self.connection.cursor()
        delete_query = f'DELETE FROM public."{config.TABLENAME}" WHERE date_post < %s;'
        cursor.execute(delete_query, (datetime.now(), ))
        self.connection.commit()

    def select_all(self):
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT * FROM public."{config.TABLENAME}"')
        result = cursor.fetchall()
        return result
