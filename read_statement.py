import os
import sys
import csv
import argparse

import pandas as pd
from termcolor import colored

from logs import setup_logging
import db

setup_logging()

INSTITUTIONS = [
    'amex',
    'halifax'
]

CATEGORIES_KEYMAP = {
    'q': 'Groceries',
    'w': 'Rent',
    'e': 'Bills',
    'a': 'Travel',
    's': 'Material Items',
    'd': 'Entertainment',
    'z': 'Savings',
    'x': 'Eating Out/Drinks',
    'v': 'Earnings',
    't': 'Transfers',
    'f': 'Cash Withdrawal',
    'c': 'Miscellaneous',
    'r': 'Not Applicable'
}


def get_halifax_record(row):
    return {
        'date': row[0],
        'reference': row[4],
        'debit': row[5],
        'credit': row[6],
        'institution': 'halifax'
    }


def get_amex_record(row):
    amount = float(row[2])

    return {
        'date': row[0],
        'reference': row[3],
        'debit': amount if amount > 0 else None,
        'credit': abs(amount) if amount < 0 else None,
        'institution': 'amex'
    }


INSTITUTION_RECORDS = {
    'halifax': get_halifax_record,
    'amex': get_amex_record,
}


def read_csv(csv_file, institution):
    # read in a csv file. Format depends on the source institution
    return [
        INSTITUTION_RECORDS[institution](row)
        for row
        in csv.reader(csv_file)
    ]


def print_record(record, suffix=''):
    # format a record to display in the terminal

    result = '{date}  {reference:50}{debit:7} {credit:7}{suffix}'.format(
        suffix=suffix,
        date=record['date'],
        reference=colored(
            record['reference'],
            'yellow'
        ),
        debit=colored(
            record['debit'] if record['debit'] else '',
            'red'
        ),
        credit=colored(
            record['credit'] if record['credit'] else '',
            'green'
        ),
    )
    return print(result)


def categorise_record(record, records):
    '''
    Clear the terminal and display the record with
    options for categorisation.
    '''
    os.system('clear')
    print()
    print(colored(
        'Transactions:',
        attrs=['bold', 'underline']
    ))
    print()

    index = records.index(record)

    print_record(record, suffix=colored('   <-', 'green'))

    for _record in records[index + 1:index + 15]:
        print_record(_record)

    print()
    print(colored('Categories:', attrs=['bold']))
    print()

    for key, category in CATEGORIES_KEYMAP.items():
        print('{:20} {}'.format(category + ':', key))
    print()

    category_choice = input(
        colored('Choose and press enter:', 'cyan')
    )

    while category_choice not in CATEGORIES_KEYMAP:
        category_choice = input(
            colored('Unknown category, try again:', 'red')
        )

    record['category'] = CATEGORIES_KEYMAP[category_choice]

    return record


if __name__ == '__main__':
    db.set_up_db()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'infile',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin
    )
    parser.add_argument(
        '--source',
        '-s',
        default='amex',
        choices=INSTITUTIONS
    )

    args = parser.parse_args()

    records = read_csv(args.infile, args.source)
    dates = [record['date'] for record in records]

    records_with_categories = [
        categorise_record(record, records)
        for record
        in records
    ]

    pd.DataFrame(records_with_categories).to_csv(
        '{}-{}-{}.csv'.format(dates[0].replace('/', ''), dates[-1].replace('/', ''), args.source),
        index=False,
        header=False
    )
