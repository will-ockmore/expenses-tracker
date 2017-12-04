import sqlite3
from uuid import uuid4

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
    # create table if it doesn't already exist
    try:
        with conn:
            conn.execute(
                f'''
                CREATE TABLE IF NOT EXISTS {table_name}
                (
                    {pk_column} text PRIMARY KEY,
                    {date} date NOT NULL,
                    {reference} text NOT NULL,
                    {institution} text NOT NULL,
                    {debit} real,
                    {credit} real
                )
                '''
            )

    except sqlite3.Error as e:
        logger.exception('Error creating the database table')


def write_record(record):
    # write a record to the transactions table
    try:
        with conn:
            conn.execute(
                'INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?)',
                (
                    str(uuid4()),
                    record['date'],
                    record['reference'],
                    record['institution'],
                    record['debit'],
                    record['credit'],
                )
            )

    except sqlite3.Error as e:
        logger.exception('Error writing to the database')


def get_records():
    try:
        c.execute(
            'SELECT * FROM transactions'
        )
        return c.fetchall()

    except sqlite3.Error as e:
        logger.exception('Error reading the table')
