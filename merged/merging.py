import csv
import os
import requests
import pyproj as proj
import math

def convertPostalCodeToAreaCode(postalCode):
	topTwoDigit = postalCode[:2]
	if topTwoDigit in ['01', '02', '03', '04', '05', '06']:
		return 'Raffles Place, Cecil, Marina, People’s Park'
	elif topTwoDigit in ['07', '08']:
		return 'Anson, Tanjong Pagar'
	elif topTwoDigit in ['14', '15', '16']:
		return 'Queenstown, Tiong Bahru'
	elif topTwoDigit in ['09', '10']:
		return 'Telok Blangah, Harbourfront'
	elif topTwoDigit in ['11', '12', '13']:
		return 'Pasir Panjang, Hong Leong Garden, Clementi New Town'
	elif topTwoDigit in ['17']:
		return 'High Street, Beach Road'
	elif topTwoDigit in ['18', '19']:
		return 'Middle Road, Golden Mile'
	elif topTwoDigit in ['20', '21']:
		return 'Little India'
	elif topTwoDigit in ['22', '23']:
		return 'Orchard, Cairnhill, River Valley'
	elif topTwoDigit in ['24', '25', '26', '27']:
		return 'Ardmore, Bukit Timah, Holland Road, Tanglin'
	elif topTwoDigit in ['28', '29', '30']:
		return 'Watten Estate, Novena, Thomson'
	elif topTwoDigit in ['31', '32', '33']:
		return 'Balestier, Toa Payoh, Serangoon'
	elif topTwoDigit in ['34', '35', '36', '37']:
		return 'Macpherson, Braddell'
	elif topTwoDigit in ['38', '39', '40', '41']:
		return 'Geylang, Eunos'
	elif topTwoDigit in ['42', '43', '44', '45']:
		return 'Katong, Joo Chiat, Amber Road'
	elif topTwoDigit in ['46', '47', '48']:
		return 'Bedok, Upper East Coast, Eastwood, Kew Drive'
	elif topTwoDigit in ['49', '50', '81']:
		return 'Loyang, Changi'
	elif topTwoDigit in ['51', '52']:
		return 'Tampines, Pasir Ris'
	elif topTwoDigit in ['53', '54', '55', '82']:
		return 'Serangoon Garden, Hougang, Punggo'
	elif topTwoDigit in ['56', '57']:
		return 'Bishan, Ang Mo Kio'
	elif topTwoDigit in ['58', '59']:
		return 'Upper Bukit Timah, Clementi Park, Ulu Pandan'
	elif topTwoDigit in ['60', '61', '62', '63', '64']:
		return 'Jurong'
	elif topTwoDigit in ['65', '66', '67', '68']:
		return 'Hillview, Dairy Farm, Bukit Panjang, Choa Chu Kang'
	elif topTwoDigit in ['69', '70', '71']:
		return 'Lim Chu Kang, Tengah'
	elif topTwoDigit in ['72', '73']:
		return 'Kranji, Woodgrove'
	elif topTwoDigit in ['77', '78']:
		return 'Upper Thomson, Springleaf'
	elif topTwoDigit in ['75', '76']:
		return 'Yishun, Sembawang'
	elif topTwoDigit in ['79', '80']:
		return 'Seletar'
	return 'unkown'


def extractAndMergeHDBData():
	# 2015,BT BATOK ST 32 311,84,99,72,350000.0,HDB,3,1
	# year, name, foor area, tenure, remaining, avg transaction price, type, number_of_bedroom, number of transaction
	average_transaction_histories = []
	
	# name, postal code, lat, long, x, y
	hdb_location_queries = {}

	with open('../hdb/hdb_transactions_average.csv') as file:
			csv_reader = csv.reader(file, delimiter=',')
			for row in csv_reader:
				average_transaction_histories.append(row)

	with open('../hdb/hdb_location_query_with_cartesian.csv') as file:
			csv_reader = csv.reader(file, delimiter=',')
			for row in csv_reader:
				hdb_location_queries[row[0]] = row

	with open('merging.csv', 'w', newline='') as file:
		writer = csv.writer(file)

		writer.writerow(['property_name', 'year', 'tenture_type', 'postal_code', 'year_of_completion', 'number_of_bedroom', 'remaining_tenures', 'avg_price_psm', 'district', 'property_type', 'long', 'lat', 'x', 'y'])

		for average_transaction_history in average_transaction_histories:

			if average_transaction_history[1] not in hdb_location_queries:
				continue

			postal_code = hdb_location_queries[average_transaction_history[1]][1]
			remaining_tenure = int(average_transaction_history[4].split(" ")[0])

			year_of_completion = int(average_transaction_history[0]) - (99 - remaining_tenure)
			record = [
				average_transaction_history[1],
				average_transaction_history[0],
				'99',
				postal_code,
				year_of_completion,
				str(average_transaction_history[7]), # number of bedroom
				remaining_tenure, # remaining tenure
				round( float(average_transaction_history[5]) / float(average_transaction_history[2]), 1),
				convertPostalCodeToAreaCode(postal_code),
				'HDB',
				hdb_location_queries[average_transaction_history[1]][2],
				hdb_location_queries[average_transaction_history[1]][3],
				hdb_location_queries[average_transaction_history[1]][4],
				hdb_location_queries[average_transaction_history[1]][5]
			]
			writer.writerow(record)
	

def extractAndMergeCondoData():
 	# location_key,location_query,postal_code,latitude,longitude
	condo_location_queries = {}

	# location_query,year,no_of_bedroom,tenure_type,remaining_tenure,property_type,avg_transaction_price,avg_price_per_sqm,number_of_transaction
	average_transaction_histories = []

	with open('../condo/condo_transactions_by_year.csv') as file:
			csv_reader = csv.reader(file, delimiter=',')
			count = 0
			for row in csv_reader:
				# skip header
				count +=1 
				if count == 1:
					continue
				average_transaction_histories.append(row)

	with open('../condo/condo_location_query.csv') as file:
			csv_reader = csv.reader(file, delimiter=',')
			count = 0
			for row in csv_reader:
				# skip header
				count +=1 
				if count == 1:
					continue
				condo_location_queries[row[0]] = row

	# # setup your projections
	crs_wgs = proj.Proj('epsg:4326') # assuming you're using WGS84 geographic
	crs_bng = proj.Proj('epsg:3414') # use a locally appropriate projected CRS

	for key in condo_location_queries:
		condo_location_query = condo_location_queries[key]
		input_lon = condo_location_query[3]
		input_lat = condo_location_query[4]
					
		x, y = proj.transform(crs_wgs, crs_bng, input_lon, input_lat)
		condo_location_query.append(x)
		condo_location_query.append(y)
		print('transform %s' % condo_location_query)

	with open('merging.csv', 'a', newline='') as file:
			writer = csv.writer(file)
			for average_transaction_history in average_transaction_histories:

					if average_transaction_history[0] not in condo_location_queries:
						continue
					
					postal_code = condo_location_queries[average_transaction_history[0]][2]
			
					# year_of_completion = int(average_transaction_history[0]) - (99 - remaining_tenure)

					input_lon = condo_location_queries[average_transaction_history[0]][3]
					input_lat = condo_location_queries[average_transaction_history[0]][4]
					
					x, y = proj.transform(crs_wgs, crs_bng, input_lon, input_lat)

					record = [
						average_transaction_history[0],
						average_transaction_history[1],
						average_transaction_history[3], # tenure
						postal_code,
						"-", # completion year
						average_transaction_history[2], # number of bedroom
						average_transaction_history[4], # remaining tenure
						average_transaction_history[7], # psm
						convertPostalCodeToAreaCode(postal_code),
						average_transaction_history[5],
						condo_location_queries[average_transaction_history[0]][3],
						condo_location_queries[average_transaction_history[0]][4],
						condo_location_queries[average_transaction_history[0]][5],
						condo_location_queries[average_transaction_history[0]][6],
					]
					writer.writerow(record)


# execute the following to load the hdb csv to our desired data format.
# python -c 'import merging; merging.mergeTransactionDataFromHDBAndCondo()'

def mergeTransactionDataFromHDBAndCondo(): 

	# target row fields 
	# property_name, year, tenture_type, postal_code, year_of_completion, number_of_bedroom, remaining_tenures, avg_price_psm, district, property_type, long, lat, x, y

	# extract and merge hdb data.
	extractAndMergeHDBData()

	# extract and merge condo data.
	extractAndMergeCondoData()


# execute the following to load the hdb csv to our desired data format.
# python -c 'import merging; merging.calculateCondoCompletionYear()'

def calculateCondoCompletionYear():
	with open('merging.csv') as file:
		csv_reader = csv.reader(file, delimiter=',')
		with open('merging_condo_completion_year.csv', 'w', newline='') as targetFile:
			csv_writer = csv.writer(targetFile)
			count = 0
			for line in csv_reader:
				count += 1
				if count == 1:
					continue
				
				if line[9] == 'HDB':
					csv_writer.writerow(line)
					continue

				if line[2] == '99' or line[2] == '999': 
					completion_year = int(line[1]) - (int(line[2]) - int(line[6]))
					line[4] = completion_year
					csv_writer.writerow(line)
					continue

				csv_writer.writerow(line)

def _parse_room(room):
	if room != "" and room[0] == "5":
		return "5"
	return room

# Visualization for 03/04/05 in the doc.
def processWithConstructionHistory():
	with open('merging_condo_completion_year.csv') as file:
		csv_reader = csv.reader(file, delimiter=',')
		with open('visual_345.csv', 'w', newline='') as targetFile:
			csv_writer = csv.writer(targetFile, delimiter=',')
			for line in csv_reader:
				record = [
					# Name
					line[0],
					# Completion Year
					line[4], # ?: need to group years into a new column?
					# Room (1,2,3,4,5)
					_parse_room(line[5]),
					# Tenure remaining
					line[6],
					# Avg_price_psm
					line[7],
					# Region / District
					line[8],
					# Type
					line[9]
				]
				csv_writer.writerow(record)

# processWithConstructionHistory()

# calculate short term/ long term trends

# python -c 'import merging; merging.calculatePriceTriend()'
def calculatePriceTriend():
	with open('merging_condo_completion_year.csv') as file:
		csv_reader = csv.reader(file, delimiter=',')
		with open('pricing_trends.csv', 'w', newline='') as targetFile:
			csv_writer = csv.writer(targetFile)
	
			'''
			# 
			{
				property_name: {
					room_type: {
						 recent: { total: xxx, count: xxx}   2019-21,
						 shorterm: { total: xxx, count: xxx} 2017-2019,
						 longterm: { total: xxx, count: xxx} 2015-2017
					}
				}
			}
			'''

			count = 0
			pricing_dict = {}
			for line in csv_reader:
				
				if line[0] not in pricing_dict:
					pricing_dict[line[0]] = {}
				
				if line[5] not in pricing_dict[line[0]]:
					pricing_dict[line[0]][line[5]] = {
						'recent': { 'total' : 0, 'count': 0},
						'shorterm': { 'total' : 0, 'count': 0},
						'longterm': { 'total' : 0, 'count': 0},
					}
				
				if line[1] in ['2020', '2021']:
					pricing_dict[line[0]][line[5]]['recent']['total'] += float(line[7])
					pricing_dict[line[0]][line[5]]['recent']['count'] += 1
				
				if line[1] in ['2017', '2018', '2019']:
					pricing_dict[line[0]][line[5]]['shorterm']['total'] += float(line[7])
					pricing_dict[line[0]][line[5]]['shorterm']['count'] += 1
				
				if line[1] in ['2015', '2016']:
					pricing_dict[line[0]][line[5]]['longterm']['total'] += float(line[7])
					pricing_dict[line[0]][line[5]]['longterm']['count'] += 1
			
			for property_record in pricing_dict:
				for unit in pricing_dict[property_record]:
					record_unit = pricing_dict[property_record][unit]
					recent_change = 0.0
					long_term_change = 0.0
					recent_price = 0.0

					if record_unit['longterm']['total'] > 0:
						recent_price = (float(record_unit['longterm']['total']) / record_unit['longterm']['count'])

					if record_unit['shorterm']['total'] > 0:
						recent_price = (float(record_unit['shorterm']['total']) / record_unit['shorterm']['count'])

					if record_unit['recent']['total'] > 0:
						recent_price = (float(record_unit['recent']['total']) / record_unit['recent']['count'])
					
					if record_unit['longterm']['total'] > 0 and record_unit['recent']['total'] > 0:
						long_term_change = 100 * ( (float(record_unit['recent']['total']) / record_unit['recent']['count'])  / (float(record_unit['longterm']['total']) / record_unit['longterm']['count']) - 1.0)
						long_term_change = round(long_term_change, 1)
					
					if record_unit['shorterm']['total'] > 0 and record_unit['recent']['total'] > 0:
						recent_change = 100 * ( (float(record_unit['recent']['total']) / record_unit['recent']['count'])  / (float(record_unit['shorterm']['total']) / record_unit['shorterm']['count']) - 1.0)
						recent_change = round(recent_change, 1)

					csv_writer.writerow([property_record, unit, recent_change, long_term_change, round(recent_price, 1)])


# Reduce Flats To Recent And Combine The Pricing Trend Data
# python -c 'import merging; merging.reduceToRemoveYears()'
def reduceToRemoveYears():
    
		# key: property-number_of_bedroom
		# value: property_name, tenture_type, postal_code, year_of_completion, number_of_bedroom, remaining_tenures, avg_price_psm, district, property_type, long, lat, x, y
		property_transaction_data = {}

		# {property-number_of_bedroom: [recent_change, long_term_change, most_recent_price]}
		price_trending_data = {}
		with open('merging_condo_completion_year.csv') as file:
			csv_reader = csv.reader(file, delimiter=',')
			for line in csv_reader:
				key = "{property}-{no_bed}".format(property = line[0], no_bed = line[5])

				if key not in property_transaction_data:
					if line[2] != 'Freehold':
						remaining_tenures = int(line[6]) - (2021 - int(line[1]))
						line[6] = remaining_tenures # remaining tenture for 2021
					else:
						line[6] = '-' 
					line.pop(1)
					property_transaction_data[key] = line
		
		with open('pricing_trends.csv') as file:
			csv_reader = csv.reader(file, delimiter=',')
			for line in csv_reader:
				key = "{property}-{no_bed}".format(property = line[0], no_bed = line[1])
				price_trending_data[key] = [line[2], line[3], line[4]]

		with open('merged_data_with_pricing_trend.csv', 'w', newline='') as targetFile:
			csv_writer = csv.writer(targetFile)
			for key in property_transaction_data:
				line = property_transaction_data[key]
				line += price_trending_data[key]

				if price_trending_data[key][0] != '0.0' or price_trending_data[key][1] != '0.0':
					csv_writer.writerow(line)

# Clean localization data 
# python -c 'import merging; merging.cleanResourceData()'
def cleanResourceData():
		# setup your projections
		crs_wgs = proj.Proj('epsg:4326') # assuming you're using WGS84 geographic
		crs_bng = proj.Proj('epsg:3414') # use a locally appropriate projected CRS

		# write hawker center
		with open('../etc/hawker-centres-kml.csv') as file:
			csv_reader = csv.reader(file, delimiter=',')
			with open('hawker-center-location.csv', 'w', newline='') as targetFile:
				csv_writer = csv.writer(targetFile)
				count = 0
				for line in csv_reader:
					count += 1
					if count == 1:
						continue
				
					input_lon = line[1]
					input_lat = line[0]
					
					x, y = proj.transform(crs_wgs, crs_bng, input_lon, input_lat)
					csv_writer.writerow([line[2], x, y])

		# write car park
		with open('../etc/hdb-carpark-information.csv') as file:
			csv_reader = csv.reader(file, delimiter=',')
			with open('car-park-location.csv', 'w', newline='') as targetFile:
				csv_writer = csv.writer(targetFile)
				count = 0
				for line in csv_reader:
					count += 1
					if count == 1:
						continue
					csv_writer.writerow([line[0], line[2], line[3]])

# Calculate Adjacent Facilities
# python -c 'import merging; merging.calculateAdjacentFacalaties()'
def calculateAdjacentFacalaties():
	# get hawker center
	hawker_centers = []
	with open('hawker-center-location.csv') as file:
		csv_reader = csv.reader(file, delimiter=',')
		for line in csv_reader:
			hawker_centers.append(line)

	# get carpark 
	carparks = []
	with open('car-park-location.csv') as file:
		csv_reader = csv.reader(file, delimiter=',')
		for line in csv_reader:
			carparks.append(line)

	# get transaction records
	transaction_records = []
	with open('merged_data_with_pricing_trend.csv') as file:
		csv_reader = csv.reader(file, delimiter=',')
		for line in csv_reader:
			transaction_records.append(line)

	with open('merged_data_with_pricing_trend_and_location_filter.csv', 'w', newline='') as targetFile:
		csv_writer = csv.writer(targetFile)
		for record in transaction_records:
			# calculate car park number
			carpark_within_1km = 0
			carpark_within_2km = 0
			hawker_within_1km = 0
			hawker_within_2km = 0

			for carpark in carparks:
				distance = math.sqrt(math.pow(float(carpark[1]) - float(record[11]),2) + math.pow(float(carpark[2]) - float(record[12]),2))
				if distance <= 1000:
					carpark_within_1km += 1
				if distance <= 2000:
					carpark_within_2km += 1

			# calculate hawker center number
			for hawker_center in hawker_centers:
				distance = math.sqrt(math.pow(float(hawker_center[1]) - float(record[11]),2) + math.pow(float(hawker_center[2]) - float(record[12]),2))
				if distance <= 1000:
					hawker_within_1km += 1
				if distance <= 2000:
					hawker_within_2km += 1
			
			record += [carpark_within_1km, carpark_within_2km, hawker_within_1km, hawker_within_2km]
			print(record)
			csv_writer.writerow(record)


def binResourceRange(number):
	if number < 3: 
		return '0 - 2'
	if number <= 5:
		return '3 - 5'
	if number <= 10:
		return '6 - 10'
	
	return ' > 10'
	


# Calculate Adjacent Facilities
# python -c 'import merging; merging.filterInvalidData()'
def filterInvalidData():
	print('filtering invalid data')

	# get raw data
	raw_data = []
	with open('merged_data_with_pricing_trend_and_location_filter.csv') as file:
		csv_reader = csv.reader(file, delimiter=',')
		for line in csv_reader:
			raw_data.append(line)

	# filter and write
	with open('output.csv', 'w', newline='') as targetFile:
		csv_writer = csv.writer(targetFile)
		for record in raw_data:
			if record[2] == 'NIL':
				continue

			if record[3] != '-' and int(record[3]) < 1950:
				continue

			if record[7] == 'unkown':
				continue

			if float(record[15]) >= 30000.0:
				continue

			record[16] = binResourceRange(int(record[16]))
			record[17] = binResourceRange(int(record[17]))
			record[18] = binResourceRange(int(record[18]))
			record[19] = binResourceRange(int(record[19]))

			# filter abnormal pricing trend
			if float(record[13]) > 50.0 or float(record[13]) < -20.0:
				continue

			if float(record[14]) > 50.0 or float(record[14]) < -20.0:
				continue

			# regulate tenure type 
			if record[1] == '9999' or record[1] == '999999':
				record[1] = 'Freehold'
			if record[1] != 'Freehold' and record[1] != '99' and record[1] != '999':
				record[1] = '99'

			if record[3] == '-':
				record[3] = '1950'
				record[5] = '999'

			record[0] = record[0] + '-' + record[4]
			csv_writer.writerow(record)

'''
	LENGKONG TIGA 104,
	99,
	410104,
	1989,
	4,
	67,
	5642.1,
	"Geylang, Eunos",
	HDB,
	1.32563496745021,
	103.909815198327,
	34207.62785367015,
	36513.30337842315,
	4.0,
	3.8,
	5913.2,
	13,
	59,
	2,
	5
'''

def estimateRoomNumber(floor_area):
	if floor_area < 50:
		return "1"
	elif floor_area < 70: 
		return "2"
	elif floor_area < 100:
		return "3"
	elif floor_area < 130:
		return "4"
	else:
	 	return "5 or more"

# Calculate Adjacent Facilities
# python -c 'import merging; merging.analyseTradingFrequency()'
def analyseTradingFrequency():
	# get raw data
	# property-name : {property-name, room-number, hdb/condo, district, transactions: { yearxxx: count }} from 2017 - 2021
	raw_data = {}
	with open('merged_data_with_pricing_trend_and_location_filter.csv') as file:
		csv_reader = csv.reader(file, delimiter=',')
		for line in csv_reader:

			if line[7] == 'unkown':
				continue

			propery_type = 'HDB' if line[8] == 'HDB' else 'Condo'
			raw_data[line[0] + '-' + propery_type + '-' + line[4]] = {
				'property-name' : line[0],
				'room-number' : line[4],
				'type' : propery_type,
				'district' : line[7],
				'transactions' : {
					'2017' : [0,0,0,0,0,0,0,0,0,0,0,0],
					'2018' : [0,0,0,0,0,0,0,0,0,0,0,0],
					'2019' : [0,0,0,0,0,0,0,0,0,0,0,0],
					'2020' : [0,0,0,0,0,0,0,0,0,0,0,0],
					'2021' : [0,0,0,0,0,0,0,0,0,0,0,0]
				}
			}
	
	# parse from HDB data and cumulate the yearly frequencies.
	with open('../hdb/hdb_transactions.csv') as file:
		csv_reader = csv.reader(file, delimiter=',')
		for row in csv_reader:
			if int(row[0]) < 2017:
				continue

			key = row[2] + '-' + 'HDB' + '-' + row[8]

			if key not in raw_data:
				continue
			
			raw_data[key]['transactions'][row[0]][int(row[1]) - 1] = raw_data[key]['transactions'][row[0]][int(row[1]) - 1 ] + 1

	# parse from condo data and cumulate the yearly frequencies.
	with open('../condo/condo_transactions.csv') as file:
		csv_reader = csv.reader(file, delimiter=',')
		count = 0
		for row in csv_reader:
			count += 1
			if count == 1:
				continue

			if int(row[0]) < 2017:
				continue

			key = row[2] + '-' + 'Condo' + '-' + estimateRoomNumber(float(row[3]))

			if key not in raw_data:
				continue
			
			raw_data[key]['transactions'][row[0]][int(row[1]) - 1] = raw_data[key]['transactions'][row[0]][int(row[1]) - 1] + 1


	# write to transaction frequence record file.
	with open('transaction_frequency.csv', 'w', newline='') as targetFile:
		csv_writer = csv.writer(targetFile)
		for key in raw_data:
			data = raw_data[key]
			for i in range(12):
				csv_writer.writerow([ data['property-name'], data['room-number'], data['type'], data['district'], data['transactions']['2017'][i], str(i+1)+'/2017' ])
				csv_writer.writerow([ data['property-name'], data['room-number'], data['type'], data['district'], data['transactions']['2018'][i], str(i+1)+'/2018' ])
				csv_writer.writerow([ data['property-name'], data['room-number'], data['type'], data['district'], data['transactions']['2019'][i], str(i+1)+'/2019' ])
				csv_writer.writerow([ data['property-name'], data['room-number'], data['type'], data['district'], data['transactions']['2020'][i], str(i+1)+'/2020' ])
			
