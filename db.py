import sqlite3

import logging

logger = logging.getLogger(__name__)

# database constants
db_file = 'transactions_db.sqlite3'
table_name = 'transactions'

pk_column = 'id'  # uuid (text)
date = 'date'  # date
reference = 'reference'  # text
institution = 'institution'  # text
debit = 'debit'  # real
credit = 'credit'  # real


conn = sqlite3.connect(db_file)
c = conn.cursor()


def set_up_db():
    try:
        with conn:
            conn.execute(
                f'''
                create table {table_name}
                (
                    {pk_column} text primary key,
                    {date} date,
                    {reference} text,
                    {institution} text,
                    {debit} real,
                    {credit} real
                )
                '''
            )

    except sqlite3.OperationalError as e:
        logger.exception('Error creating the database table')
