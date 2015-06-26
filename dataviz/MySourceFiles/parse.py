"""
Data Visualization Project

Parse data from an ugly CSV or Excel file, and render it in
JSON, save to a database, and visualize in graph form.

Part I: Taking data from a CSV/Excel file, and return it into a format
that is easier for Python to play with.

Copyright (c) 2013 E. Lynn Root
Distributed under the zlib png license. See LICENSE for details.
"""

import csv

# Put the full path to your CSV/Excel file here
MY_FILE = "../data/sample_sfpd_incident_all.csv"

def parse(raw_file, delimiter):
	"""Parses a raw CSV files to a JSON-like object"""

	# Open CSV file
	opened_file = open(raw_file)

	# Read the CSV File
	csv_data = csv.reader(opened_file, delimiter=delimiter)

	# Setup an empty list
	parsed_data = []

	# Skip over the first line of the file for the headers
	fields = csv_data.next()

	# Iterate over each row of th csv file, zip together field -> value
	for row in csv_data:
		parsed_data.append(dict(zip(fields, row)))

	# Close the CSV file
	opened_file.close

	return parsed_data


def main():
	# Call our parse function and give the needed parameters
	new_data = parse(MY_FILE, ",")

	# Write parsed data to a new file
	parsed_data_file = open("parsed_data_file.txt", 'w')
	parsed_data_file.write("%s" % new_data)
	parsed_data_file.close()

	# Let's see what the data looks like!
	#print new_data


if __name__ == "__main__":
	main()