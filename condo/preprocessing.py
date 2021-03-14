import csv
import collections

"""
mappings ={
  location: {
			year : {
				room_number: {
					avg,
      		count
				}
    	}
  }
}
"""

mappings = collections.defaultdict(dict)

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

def process():
	with open('condo_transactions.csv') as csv_file:
		csv_reader = csv.DictReader(csv_file)
		for row in csv_reader:
			room_number = estimateRoomNumber(float(row['floor_area']))
			data = mappings.get(row['location_query'], {}).get(row['year'], {}).get(room_number, {})
			data['total_transaction_price'] = data.get('total_transaction_price', 0) + float(row['transaction_price'])
			data['number_of_transaction'] = data.get('number_of_transaction', 0) + 1
			data['price_per_sqm'] = data.get('price_per_sqm', 0) + float(row['transaction_price']) / float(row['floor_area'])

			if row['year'] in mappings[row['location_query']]:
				mappings[row['location_query']][row['year']][room_number] = data
			else:
				mappings[row['location_query']][row['year']] = { room_number: data }
  
	with open('condo_transactions_by_year.csv', 'w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(["location_query", "year", "avg_transaction_price", "avg_price_per_sqm", "number_of_transaction"])
    
		for location, yearly_data in mappings.items():
			for year, unit_data in yearly_data.items():
				for room_type, txn_data in unit_data.items():
					avg = round(txn_data['total_transaction_price'] / txn_data['number_of_transaction'])
					avg_price_per_sqm = round(txn_data['price_per_sqm'] / txn_data['number_of_transaction'])
					writer.writerow([location, year, room_type , avg, avg_price_per_sqm, txn_data['number_of_transaction']])


if __name__ == "__main__":
    process()
