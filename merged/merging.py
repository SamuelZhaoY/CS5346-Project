import csv
import os
import requests
import pyproj as proj

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
				str(average_transaction_history[7]),
				average_transaction_history[5],
				average_transaction_history[2],
				round( float(average_transaction_history[5]) / float(average_transaction_history[2]), 1),
				convertPostalCodeToAreaCode(postal_code),
				'HDB',
				hdb_location_queries[average_transaction_history[1]][2],
				hdb_location_queries[average_transaction_history[1]][3],
				hdb_location_queries[average_transaction_history[1]][4],
				hdb_location_queries[average_transaction_history[1]][5]
			]
			writer.writerow(record)
	
# execute the following to load the hdb csv to our desired data format.
# python -c 'import merging; merging.mergeTransactionDataFromHDBAndCondo()'

def mergeTransactionDataFromHDBAndCondo(): 

	# target row fields 
	# property_name, year, tenture_type, postal_code, year_of_completion, number_of_bedroom, remaining_tenures, floor_area, avg_price_psm, district, property_type, lat, long, x, y

	# extract and merge hdb data
	extractAndMergeHDBData()