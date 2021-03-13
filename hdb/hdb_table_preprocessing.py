import csv
import os
import requests
import pyproj as proj

def readRawDataFromFile(filePath):
	rows = []
	with open(filePath) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			line_count = 0
			for row in csv_reader:
					if line_count == 0:
							print(f'Column names are {", ".join(row)}')
							line_count += 1
					else:
					#     print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')

							# row[0] format: 2015-01
							year = row[0].split('-')[0]
							month = row[0].split('-')[1]

							# assemble location query
							location_query = "{town} {blk}".format(town = row[4], blk = row[3])

							# floor area in sqm
							floor_area = row[6]

							# tenure_type 
							tenure_type = '99'

							# remaining_tenure 
							remaining_tenure = row[9]

							# transaction_price 
							transaction_price = row[10]

							# property_type
							property_type = 'HDB'

							# no_of_bedroom: 
							# 3 ROOM - 2 | 4, 5 ROOM - 3 | Executive - 4

							no_of_bedroom = '1'
							if row[2] == '3 ROOM':
								no_of_bedroom = '2'
							elif row[2] == '4 ROOM' or row[2] == '5 ROOM':
								no_of_bedroom = '3'
							elif row[2] == 'EXECUTIVE':
								no_of_bedroom = '4'
							
							rows.append([
									year, 
									month, 
									location_query, 
									floor_area, 
									tenure_type, 
									remaining_tenure, 
									transaction_price, 
									property_type, 
									no_of_bedroom
								])

							line_count += 1

			print(f'Processed {line_count} lines.')
	return rows

# execute the following to load the hdb csv to our desired data format.
# python -c 'import hdb_table_preprocessing; hdb_table_preprocessing.parseRawData()'

def parseRawData(): 

	# rows = [
	# 	[
	# 		'year', 
	# 		'month', 
	# 		'location_query', 
	# 		'floor_area', 
	# 		'tenure_type', 
	# 		'remaining_tenure', 
	# 		'transaction_price', 
	# 		'property_type', 
	# 		'no_of_bedroom'
	# 		]
	# ]

	rows = []

	rows += readRawDataFromFile('./source/resale-flat-prices-based-on-registration-date-from-jan-2015-to-dec-2016.csv')
	rows += readRawDataFromFile('./source/resale-flat-prices-based-on-registration-date-from-jan-2017-onwards.csv')

	if os.path.exists("hdb_transactions.csv"):
		os.remove("hdb_transactions.csv")

	with open('hdb_transactions.csv', 'w', newline='') as file:
		writer = csv.writer(file)
		writer.writerows(rows)

# execute the function below to get a detailed location infor based on 'location_query' params
# python -c 'import hdb_table_preprocessing; hdb_table_preprocessing.resolveLocationInfo()'

def resolveLocationInfo():

	locationInfo = []
	with open("hdb_transactions.csv") as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			line_count = 0
			for row in csv_reader:
				if line_count > 0:
					if row[2] not in locationInfo:
						locationInfo.append(row[2])
				line_count += 1

	existingQueries = []
	with open('hdb_location_query.csv') as file:
			csv_reader = csv.reader(file, delimiter=',')
			for row in csv_reader:
				existingQueries.append(row[0])

	pendingQueries = []
	for info in locationInfo:
		if info not in existingQueries:
			pendingQueries.append(info)
	
	with open('hdb_location_query.csv', 'a', newline='') as file:
			csv_writer = csv.writer(file)
			for info in pendingQueries:
				try:
					ploads = {'searchVal':info, 'returnGeom':'Y', 'getAddrDetails':'Y'}
					r = requests.get('http://developers.onemap.sg/commonapi/search',params=ploads).json()
					if r['found'] > 0:
						result = r['results'][0]
						csv_writer.writerow([info, result['POSTAL'], result['LATITUDE'], result['LONGITUDE']])
						print('success in execution query: %s' % info)
					else:
						print('error in execution query: %s' % info)
				except:
					print('exception in execution query: %s' % info)

# covert lon, lat to cartesian location
# python -c 'import hdb_table_preprocessing; hdb_table_preprocessing.appendCartesianCoordinate()'
def appendCartesianCoordinate():

	existingQueries = []
	with open('hdb_location_query.csv') as file:
			csv_reader = csv.reader(file, delimiter=',')
			for row in csv_reader:
				existingQueries.append(row)

	# # setup your projections
	crs_wgs = proj.Proj('epsg:4326') # assuming you're using WGS84 geographic
	crs_bng = proj.Proj('epsg:3414') # use a locally appropriate projected CRS

	with open('hdb_location_query_with_cartesian.csv', 'w', newline='') as file:
			csv_writer = csv.writer(file)

			for line in existingQueries:
				input_lon = line[2]
				input_lat = line[3]
				print('transform %s' % line)
				x, y = proj.transform(crs_wgs, crs_bng, input_lon, input_lat)
				line.append(x)
				line.append(y)
				csv_writer.writerow(line)

# python -c 'import hdb_table_preprocessing; hdb_table_preprocessing.getAverageTransactions()'
def getAverageTransactions():
	# {{location_query}_#{year}_#{no_of_bedroom}:row}
	existingQueries = {}
	with open('hdb_transactions.csv') as file:
			csv_reader = csv.reader(file, delimiter=',')
			for row in csv_reader:
				index = "{unit}_{year}_{type}".format(unit = row[2], year = row[0], type= row[8])
				if index not in existingQueries:
					existingQueries[index] = row
					existingQueries[index][6] = float(row[6])
					existingQueries[index].append(1)
				else:
					existingQueries[index][9] += 1
					existingQueries[index][6] += float(row[6])
	
	with open('hdb_transactions_average.csv', 'w', newline='') as file:
			csv_writer = csv.writer(file)

			for index in existingQueries:
				existingQueries[index][6] = round(existingQueries[index][6]/existingQueries[index][9],1)
				existingQueries[index].pop(1)
				csv_writer.writerow(existingQueries[index])


			


