def create_map(data_file):
	# Defile type of GeoJSON we're creating
	geo_map = {"type": "FeatureCollection"}

	# Define empty list to collect each point to graph
	item_list = []

	# Iterate over our data to create GeoJSON document.
	# We're using enumerate() so we get the line, as well 
	# as the index, which is the line number.

		# Skip any zero coordinates as this will throw off our map.

		# Setup a new dictionary for each iteration

		# Assign line items to appropriate GeoJSON fields.

		# Add data dictionary to our item_list

	# For each point in our item_list, we add the point to our dictionary.
	# setdefault creates a key called 'features' that
	# has a value tyoe of an empty list. With each iteration, we
	# are appending our point to that list. 

	# now that all data is parsed in GeoJSON write to a file so we
	# can upload it to gist.github.com