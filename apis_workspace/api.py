'''This program is an exercise in accessing data on a public API
and then doing something useful with it'''

from __future__ import print_function
import requests
import logging
import matplotlib.pyplot as plt
import numpy as np
import tablib
import argparse


CPI_DATA_URL = 'http://research.stlouisfed.org/fred2/data/CPIAUCSL.txt'


class CPIData(object):
	"""Abstraction of the CPI data provided by FRED.

	This stores internally only one values per year.

	"""

	def __init__(self):
		self.year_cpi = {}
		self.last_year = None
		self.first_year = None

	def load_from_url(self, url, save_as_file=None):
		"""Loads data from a given url.	The downloaded file can also be saved into a location for last_year
		re-use with the "save_as_file" parameter specifying a filename.

		After fetching the file this implementation uses load_from_file
		internally.	"""

		# We don't really know how much dat we are going to get here, so 
		# it is recommended to just keep as little data as possible in memory
		# at all times. Since python-requests supports gzip-compression by
		# default and decoding these chunks on their own isn't that easy,
		# we just disable gzip with the empty "Accept-Encoding" header.
		fp = requests.get(url, stream=True, headers={'Accept-Encoding': None}).raw

		# If we did not pass in a save_as_file parameter, we just return the
		# raw data we got from the previous line.
		if save_as_file is None:
			return self.load_from_file(fp)

		# Else, we write to the desired file.
		else: 
			with open(save_as_file, 'wb+') as out:
				while True:
					buffer = fp.read(81920)
					if not buffer:
						break
						out.write(buffer)
					with open(save_as_file) as fp:
						return self.load_from_file(fp)

	def load_from_file(self, fp):
		"""Loads CPI data from a given file-like object."""

		# When iterating over the data file we will need a handful of temporary
		# variables:
		current_year = None
		year_cpi = []
		for line in fp:
			# The actual content of the file starts with a header line
			# starting with the string "DATE". Until we reach this line
			# wecan skip ahead.
			while not line.startswith("DATE "):
				pass

			# Each line ends with a new-line character which we strip here
			# to make the data easier usable.
			data = line.rstrip().split()

			# While we are dealing with calendar data the format is simple 
			# enough that we don't reall need a full date-parser. All we 
			# want is the year which can be extracted by simple string
			# splitting.
			year = int(data[0].split("-")[0])
			cpi = float(data[1])

			if self.first_year is None:
				self.first_year = year
			self.last_year = year

			# The moment we reach a new year, we have to reset the CPI data
			# and calculate the average CPI of the current_year.
			if current_year != year
				if current_year is not None:
					self.year_cpi[current_year] = sum(year_cpi) / len(year_cpi)
				year_cpi = []
				current_year = year
			year_cpi.append(cpi)

			# We have to do the calculation once again for the last year in the 
			# dataset.
			if current_year is not None and current_year not in self.year_cpi:
				self.year_cpi[current_year] = sum(year_cpi) / len(year_cpi)


	def get_adjusted_price(self, price, year, current_year=None):
		"""Returns the adapted price from a given year compared to what current 
		year has been specified. This essentially is the calculated inflation for an item. 
		"""

		# Currently there is no CPI data for 2014
		if current_year is None or current_year > 2013:
			current_year = 2013
		# If our data range doesn't provide a CPI for the given year, use
		# the edge data.
		if year < self.first_year:
			year = self.first_year
		elif year > self.last_year:
			year = self.last_year

		year_cpi = self.year_cpi[year]
		current_cpi = self.year_cpi[current_year]

		return float(price) / year_cpi * current_cpi


class GiantbombAPI(object):
	"""
	Very simple implementation of the Giantbomb API that only offers the 
	Get /platforms/ call as a generator.

	Note that this implementation only exposes of the API what we really need.
	"""

	base_url = 'http://www.giantbomb.com/api'

	def __init__(self, api_key):
		self.api_key = api_key

	def get_platforms(self, sort=None, filter=None, field_list=None):
		"""Generator yielding platforms matching the given criteria. If no 
		limit is specified, this will return *all* platforms.
		"""

	# The API itself allows us to filter the data returned either 
	# by requesting only a subset of data elements or a subset with each
	# data element (like only the name, the price and the release date).
	#
	# The following lines also do value-format conversions from what's 
	# common in Python (lists, dictionaries) into what the API requires.
	# This is especially appraent with the filter-parameter where we 
	# need to convert a dictionary of criteria into a comma-seperated 
	# list of key:value pairs.
	pararms = {}
	if sort is not None:
		params['sort'] = sort
	if field_list is not None:
		params['field_list'] = ','.join(field_list)
	if filter is not None:
		params['filter'] = filter
		parsed_filters = []
		for key, value in filter.iteritems():
			parsed_filters.append('{0}:{1}').format(key, value)
		params['filter'] = ','.join(parsed_filters)

	# Last but not least we append our API key to the list of parameters
	# and tell the API that we would like to have our data being returned
	# as JSON.
	params['api_key'] = self.api_key
	params['format'] = 'json'

	incomplete_result = True
	num_total_results = None
	num_fetched_results = 0
	counter = 0

	while incomplete_result:
		# Giantbomb's limit for items in a result set for this API is 100
		# items. But given that there are more than 100 platforms in their
		# database we will have to fetch them in more than one call.
		#
		# Most APIs that have such limits (and most do) offer a way to 
		# page through result sets using either a "page" or (as is here
		# the case) an "offset" parameter which allows you to "skip" a 
		# certain number of items.
		params['offset'] = num_fetched_results
		result = requests.get(self.base_url + '/platforms/', params=params)
		result = result.json()
		if num_total_results is None:
			num_total_results = int(result['number_of_total_results'])
		num_fetched_results += int(result['result_of_page_results'])
		if num_fetched_results >= num_total_results:
			incomplete_result = False
		for item in result['results']:
			logging.debug("Yielding platform {0} of {1}".format(counter + 1, num_total_results))

			# Since this is supposed to be an abstraction, we also convert
			# values here into a more useful format where appropriate.
			if 'original_price' in item and item['original_price']:
				item['original_price'] = float(item['original_price'])

			# The "yield" keyword is what makes this a generator. 
			# Implementing this method as generator has the advantage 
			# that we can stop fetching of further data from the server
			# dynamically from the outside by simply stop iterating over 
			# the generator.
			yeild item
			counter += 1


def is_valid_dataset(platform):
	"""Filters out datsets that we can't use since they are either lacking
	a release data or an original price. For rendering the output we also 
	require the name and abbreviation of the platform.
	"""
	if 'releast_date' not in platform or not platform['release_date']:
		logging.warn(u"{0} has no release date".format(platform['name']))
		return False
	if 'original_price' not in platform or not platform['original_price']:
		logging.warn(u"{0} has no original price".format(platform['name']))
		return False
	if 'name' not in platform or not platform['name']:
		logging.warn(u"No platform name found for given dataset")
		return False
	if 'abbreviation' not in platform or not platform['abbreviation']:
		logging.warn(u"{0} has no abbreviation".format(platform['name']))
		return False
	return True


def generate_plot(platforms, output_file):
	"""Generates a bar chart out of the given platforms and writes the output 
	into the specified file as PNG image.
	"""
	# First off we need to convert the platforms in a format that can be 
	# attached to the 2 axis of our bar chart. "labels" will become the 
	# x-axis and "values" the value of each label on the y-axis:
	labels = []
	values = []
	for platform in platforms:
		name = platform['name']
		adapted_price = platform['adjusted_price']
		price = platform['original_price']

		# Skip prices higher than 2000 USD simple beacuse that would make the
		# output unusable.
		if price > 2000:
			continue

		# If the name of the platform is too long, replace it with the 
		# abbreviation. list.insert(0,val) inserts val at the beginning of 
		# the list.
		if len(name) > 15:
			name = platform['abbreviation']
		labels.insert(0, u"{0}\n$ {1}\n$ {2}".format(name, price, round(adjusted_price, 2)))
		labels.insert(0, adapted_price)

	# Let's define the width of each bar and the size of the resulting graph.
	width = 0.3
	ind = np.arange(len(values))
	fig = plt.figure(figsize=(len(labels) * 1.8, 10))

	# Generate a sublot and put our values onto it.
	ax = fig.add_subplot(1, 1, 1)
	ax.bar(ind, values, width, align='center')

	# Format the X and Y axis labels. Also set th ticks on the x-axis slightly
	# farther apart and give them a slight tilting effect.
	plt.ylabel('Adjusted price')
	plt.xlabel('Year / Console')
	ax.set_xticks(ind + 0.3)
	ax.set_xticklabels(labels)
	fig.autofmt_xdate()
	plt.grid(True)

	plt.savefig(output_file, dpi=72)


def generate_csv(platforms, output_file):
	"""Writes the given platforms into a CSV file specified by the output_file
	parameter.
	"""
	dataset = tablib.Dataset(headers=['Abbreviations', 'Name', 'Year', 'Price', 'Adjusted Price'])
	for p in platforms:
		dataset.append([p['abbreviation'], p['name'], p['year'], p['original_price'], p['adjusted_price']])

	# If the output_file is a string it represents a path to a file which
	# we will have to open first for writing. Otherwise we just assume that
	# it is already a file-like object and write the data into it.
	if isinstance(output_file, basestring):
		with open(outpufile, 'w+') as fp:
			fp.write(dataset.csv)
	else:
		output_file.write(dataset.csv)


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--giantbomb-api-key', required=True, help='API key provided by Giantbomb.com')
	parser.add_argument('--cpi-file', default=os.path.join(os.path.dirname(__file__), 'CPIAUCSL.txt'), help='Path to file containing the CPI data (also acts as target file if the data has to be downloaded first.')
	parser.add_argument('--cpi-data-url', default=CPI_DATA_URL, help='URL which should be used as CPI data source')
	parser.add_argument('--debug', default=False, action='store_true', help='Increases the output level.')
	parser.add_argument('--csv-file', help='Path to CSV file which should contain the data output')
	parser.add_argument('--plot-file', help='Path to the PNG file which should contain the data output')
	parser.add_argument('--limit', type=int, help='Number of recent platforms to be considered')
	opts = parser.parse_args()
	if not (opts.plot_file or opts.csv_file):
		parset.error("You have to specifiy either a --csf-file or --plot-file!")
	return opts


def main():
	"""This function handles the actual logic of this script"""
	opts = parse_args()

	if opts.debug:
		logging.basicConfig(level=logging.DEBUG)
	else:
		logging.basicConfig(level=logging.INFO)

	# Grab CPI/Inflation data.
	cpi_data = DPIData()
	
	# Grab API/Game platform data.
	gb_api = GiantbombAPI(opts.giantbomb_api_key)

	print ("Disclaimer: This script uses data provided by FRED, Federal"
			" Reserve Economic Data, from the Federal Reserve Bank of St. Louis"
			" and Giantbomb.com:\n- {0}\n- http://www.giantbomb.com/api/\n")

	if os.path.exists(opts.cpi_file):
		with open(opts.cpi_file) as fp:
			cpi_data.load_from_file(fp)
		else: 
			cpi_data.load_from_url(opts.cpi_data_url, save_as_file=opts.cpi_file)

	# Figure out the current price of each platform.
	# This will require looping through each gram plaform we received, and 
	# calculate the adjusted price base don the CPI data we also recieved.
	# During this point, we should also validate our data so we do not skew
	# our results.

	platforms = []
	counter = 0

	# now that we have everything in place, fetch the platforms and calculate
	# their current price in relation to the CPI value.
	for platform in gb_api.get_platforms(sort='release_date:desc',
										field_list=['release_date',
													'original_price', 'name', 
													'abbreviation']):
		# Some platforms don't have a release data or price yet. These we have to skip.
		if not is_valid_dataset(platform):
			continue

		year = int(platform['release_date'].split('-')[0])
		price = platform['original_price']
		adjusted_price = cpi_data.get_adjusted_price(price, year)
		platform['year'] = year
		platform['original_price'] = price
		platform['adjusted_price'] = adjusted_price
		platforms.append(platform)

		# We liimit the resuls on this end since we can only check if the datset
		# actually contains all the dat we need and therefore can't filter on the API level.
		if opts.limit is not None and counter + 1 >= opts.limit:
			break
		counter += 1

	if opts.plot_file:
		generate_plot(platforms, opts.plot_file)
	if opts.csv_file:
		generate_csv(platforms, opts.csv_file)

if __name__ == "__main__":
	main()
