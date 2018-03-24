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
    'halifax',
    'firstdirect'
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
    'g': 'Clothing',
    'v': 'Earnings',
    't': 'Transfers',
    'f': 'Cash Withdrawal',
    'c': 'Miscellaneous',
    'r': 'Not Applicable'
}

CSV_COLUMNS = [
    'category',
    'credit',
    'date',
    'debit',
    'institution',
    'reference',
]


def get_halifax_record(row):
    return {
        'date': row[0],
        'reference': row[4],
        'debit': row[5] or 0,
        'credit': row[6] or 0,
        'institution': 'halifax'
    }


def get_amex_record(row):
    amount = float(row[2])

    return {
        'date': row[0],
        'reference': row[3],
        'debit': amount if amount > 0 else 0,
        'credit': abs(amount) if amount < 0 else 0,
        'institution': 'amex'
    }


def get_firstdirect_record(row):
    amount = float(row[2])

    return {
        'date': row[0],
        'reference': row[1],
        'debit': abs(amount) if amount < 0 else 0,
        'credit': amount if amount > 0 else 0,
        'institution': 'firstdirect'
    }


INSTITUTION_RECORDS = {
    'halifax': get_halifax_record,
    'amex': get_amex_record,
    'firstdirect': get_firstdirect_record,
}


def read_csv(csv_file, institution):
    # read in a csv file. Format depends on the source institution
    return [
        INSTITUTION_RECORDS[institution](row)
        for row
        in csv.reader(csv_file)
    ]


def print_record(record, suffix='', display_category=False):
    # format a record to display in the terminal

    result = '{date}  {reference:50}{debit:15} {credit:15} {category:30}{suffix}'.format(  # noqa
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
        category=colored(
            record['category'],
            'blue'
        )
        if display_category else ''
    )
    return print(result)


def choose_category(record):
    category_choice = input(
        colored('Choose and press enter:', 'cyan')
    )

    while category_choice.lower() not in CATEGORIES_KEYMAP:
        category_choice = input(
            colored('Unknown category, try again:', 'red')
        )

    record['category'] = CATEGORIES_KEYMAP[category_choice.lower()]

    if category_choice.isupper():
        # chosen to save this transaction category
        db.write_record(record)

    return record


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
    print('Capitalise choice to save the category for this transaction.')
    print(
        'Whenever this combination of reference and debit/credit is seen '
        'again, the category you chose will be automatically applied.'
    )  # noqa
    print()

    for key, category in CATEGORIES_KEYMAP.items():
        print('{:20} {}'.format(category + ':', key))
    print()

    record_with_category = choose_category(record)

    return record_with_category


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

    records_already_categorised = []

    for record in records:
        record['category'] = db.get_record_category(record)

        if record['category']:
            records_already_categorised.append(record)

    uncategorised_records = [
        record
        for record
        in records
        if record not in records_already_categorised
    ]

    records_manually_categorised = [
        categorise_record(record, uncategorised_records)
        for record
        in uncategorised_records
    ]

    csv_filename = '{}-{}-{}.csv'.format(
        dates[0].replace('/', ''),
        dates[-1].replace('/', ''),
        args.source
    )

    os.system('clear')

    print()
    print(colored(
        'Automatically categorised:',
        attrs=['bold']
    ))
    print()

    for record in records_already_categorised:
        print_record(record, display_category=True)

    print()
    print(colored(
        'Manually categorised:',
        attrs=['bold']
    ))
    print()

    for record in records_manually_categorised:
        print_record(record, display_category=True)

    print()
    print(f'Writing to {csv_filename}...')
    print()

    pd.DataFrame(
        records_manually_categorised + records_already_categorised
    )[CSV_COLUMNS].to_csv(
        csv_filename,
        index=False,
        header=False
    )
