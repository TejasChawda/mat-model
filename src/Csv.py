import csv

import pandas as pd


def copy_csv(source_file, destination_file):
    with open(source_file, 'r', newline='') as source_csvfile:
        with open(destination_file, 'w', newline='') as destination_csvfile:
            # Create CSV reader and writer objects
            csv_reader = csv.reader(source_csvfile)
            csv_writer = csv.writer(destination_csvfile)

            # Copy rows from source to destination
            for row in csv_reader:
                csv_writer.writerow(row)


def filter_csv(all_scales, selected_rows, source_csv, destination_csv):
    copy_csv(source_csv, destination_csv)

    dest_df = pd.read_csv(destination_csv)

    # Create an empty DataFrame to accumulate filtered rows
    filtered_df = pd.DataFrame()

    for scale in all_scales:
        if scale in selected_rows:
            mask = dest_df["Scale_Id"] == scale
            filtered_df = pd.concat([filtered_df, dest_df[mask]], ignore_index=True)

    filtered_df.to_csv(destination_csv, index=False)


def clear_csv(csv_file):
    with open(csv_file, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow('')
