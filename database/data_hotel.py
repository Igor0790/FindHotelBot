import psycopg2
from psycopg2 import OperationalError
from datetime import datetime, date

"""
Класс, отвечающий за работу с SQL
"""

class Database:

    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        try:
            self.connection = psycopg2.connect(
                database=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
            )
            print("Подключение к PostgresSQL серверу - успешно!")
        except OperationalError as e:
            print(f"Ошибка '{e}' нас настигла.")
        self.cursor = self.connection.cursor()

    def execute_query(self, query: str) -> None:
        self.connection.autocommit = True
        try:
            self.cursor.execute(query)
            print('Запрос SQL прошел успешно!')
            #self.cursor.commit()
        except OperationalError as e:
            print(f"Ошибка '{e}' нас настигла.")

    def insert_query(self, insert_query_str: str, object: (list, tuple)) -> None:
        self.connection.autocommit = True
        try:
            self.cursor.execute(insert_query_str, object)
        except OperationalError as e:
            print(f"Ошибка '{e}' нас настигла.")

    def get_lines(self, query: str) -> (None, int, list):
        records = None
        try:
            self.cursor.execute(query)
            records = self.cursor.fetchall()
            print('Данные из класса датабайз', records)
        except OperationalError as e:
            print(f"Ошибка '{e}' нас настигла.")
        finally:
            return records

    def set_temp_data(self, user_id, city, date_in, date_out, command):

        create_new_table = f"""
                CREATE TABLE IF NOT EXISTS temp_data (
                  id SERIAL PRIMARY KEY,
                  user_id TEXT,
                  city TEXT,
                  DATE_IN TEXT,
                  DATE_OUT TEXT,
                  num_days TEXT,
                  COMMAND TEXT
                )
                """
        self.execute_query(create_new_table)
        insert_query_str = (f"INSERT INTO temp_data (user_id, city, DATE_IN, DATE_OUT, num_days, COMMAND) VALUES %s")
        self.insert_query(insert_query_str,
                              [(user_id,city, date_in, date_out, (date_out - date_in).days, command)])

    def delete_all(self):
        text = 'DO $$ DECLARE \n' \
               '  r RECORD;\n' \
               'BEGIN\n' \
               '  FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP\n' \
               '    EXECUTE \'DROP TABLE \' || quote_ident(r.tablename) || \' CASCADE\';\n' \
               '  END LOOP;\n' \
               'END $$;'

        self.execute_query(text)
        print('Очистка БД успешна.')

    def delete_user_table(self, uid) -> list:
        all_table = self.get_lines('SELECT table_name FROM information_schema.tables '
                                 'WHERE table_schema NOT IN (\'information_schema\',\'pg_catalog\');')
        result = []
        for name_table in all_table:
            if str(uid) in name_table[0]:
                if 'history' not in name_table[0]:
                    result.append(name_table)

        return result

    def add_log(self, uid: int, data: tuple) -> None:
        create_new_table = f"""
                CREATE TABLE IF NOT EXISTS history_{uid} (
                  id SERIAL PRIMARY KEY,
                  name_hotel TEXT,
                  address TEXT,
                  price_for_day BIGINT,
                  price_for_all_day BIGINT,
                  landmark TEXT,
                  photo TEXT,
                  date TEXT,
                  command TEXT,
                  id_hotel TEXT
                )
                """

        self.execute_query(create_new_table)

        insert_query_str = (
            f"INSERT INTO history_{uid} (name_hotel, address, price_for_day, price_for_all_day, landmark, photo, date, command, id_hotel) "
            f"VALUES %s")
        self.insert_query(insert_query_str, data)


    def close(self) -> None:
        self.connection.close()

