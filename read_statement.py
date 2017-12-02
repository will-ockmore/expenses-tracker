import csv
import argparse
import pandas as pd
import json
import sys

INSTITUTIONS = [
    'amex',
    'halifax'
]


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument(
        '--source',
        '-s',
        default='amex',
        choices=INSTITUTIONS
    )

    args = parser.parse_args()

    records = read_csv(args.infile, args.source)

    for record in records:
        pass
