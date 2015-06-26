from collections import Counter

import csv
import matplotlib.pyplot as plt
import numpy as np
import parse


MY_FILE = "../data/sample_sfpd_incident_all.csv"


def visualize_days(data_file):
	"""Visualize data by day of the week"""
	#data_file = parse(MY_FILE, ",")
	# Returns a dict where it sums the total values of each key.
	# In this case, the keys are the DaysOfWeek, and the values 
	# a count of incidents
	counter = Counter(item["DayOfWeek"] for item in data_file)

	# Separate out the counter to order it correctly when plotting
	data_list = [counter["Monday"],
				 counter["Tuesday"],
				 counter["Wednesday"],
				 counter["Thursday"],
				 counter["Friday"],
				 counter["Saturday"],
				 counter["Sunday"]
				 ]
	day_tuple = tuple(["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"])

	# Assign the data to a plot 
	plt.plot(data_list)

	# Assign labels to the plot 
	plt.xticks(range(len(day_tuple)), day_tuple)

	# Save the plot!
	plt.savefig("Days.png")

	# Close figure
	plt.clf()


def visualize_type(data_file):
	"""Visualize data by type"""

	# Grab parsed data

	# Make a new variable, 'counter', from iterating through each line
	# of data in the parsed data, and count how many incidents happened
	# by category
	counter = Counter(item["Category"] for item in data_file)

	# Set the labels which are based on the keys of our counter
	# Since order doesn't matter, we can just use counter.keys()
	labels = tuple(counter.keys())

	# Set exactly where the labesl hit the x-axis
	xlocations = np.arange(len(labels)) + 0.5

	# Width of each bar that will be plotted
	width = 0.5

	# Assign data to a bar plot (similar to plt.plot()!)
	plt.bar(xlocations, counter.values(), width=width)

	# Assign labels and tick location to x-axis
	plt.xticks(xlocations + width / 2, labels, rotation=90)

	# Give some more room so the x-axis labels aren't cut off in the graph
	plt.subplots_adjust(bottom = 0.4)

	# Make the overall graph/figure larger
	plt.rcParams['figure.figsize'] = 12, 8

	# Save the graph!
	plt.savefig("Type.png")

	# Close plot figure
	plt.clf()


def main():
	parsed_data = parse.parse(MY_FILE, ",")
	visualize_days(parsed_data)
	visualize_type(parsed_data)


if __name__ == "__main__":
	main()