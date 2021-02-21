import csv
import os

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
							location_query = "{town}, blk {blk}".format(town = row[1], blk = row[3])

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

	rows = [
		[
			'year', 
			'month', 
			'location_query', 
			'floor_area', 
			'tenure_type', 
			'remaining_tenure', 
			'transaction_price', 
			'property_type', 
			'no_of_bedroom'
			]
	]

	rows += readRawDataFromFile('./HDB/resale-flat-prices-based-on-registration-date-from-jan-2015-to-dec-2016.csv')
	rows += readRawDataFromFile('./HDB/resale-flat-prices-based-on-registration-date-from-jan-2017-onwards.csv')

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

	locationInfo = list(map(lambda x: [x], locationInfo))

	print('pending execution of %d' %  len(locationInfo))
	if os.path.exists("hdb_location_query.csv"):
		os.remove("hdb_location_query.csv")

	with open('hdb_location_query.csv', 'w', newline='') as file:
		writer = csv.writer(file)
		writer.writerows(locationInfo)