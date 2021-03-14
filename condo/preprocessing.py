import csv
import collections

"""
mappings ={
  location: {
    year : {
      avg,
      count
    }
  }
}
"""
mappings = collections.defaultdict(dict)

def process():
  with open('condo_transactions.csv') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
      data = mappings.get(row['location_query'], {}).get(row['year'], {})
      data['total_transaction_price'] = data.get('total_transaction_price', 0) + float(row['transaction_price'])
      data['number_of_transaction'] = data.get('number_of_transaction', 0) + 1
      data['price_per_sqm'] = data.get('price_per_sqm', 0) + float(row['transaction_price']) / float(row['floor_area'])
      mappings[row['location_query']][row['year']] = data
  
  with open('condo_transactions_by_year.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["location_query", "year", "avg_transaction_price", "avg_price_per_sqm", "number_of_transaction"])
    
    for location, yearly_data in mappings.items():
      for year, txn_data in yearly_data.items():
        avg = round(txn_data['total_transaction_price'] / txn_data['number_of_transaction'])
        avg_price_per_sqm = round(txn_data['price_per_sqm'] / txn_data['number_of_transaction'])
        writer.writerow([location, year, avg, avg_price_per_sqm, txn_data['number_of_transaction']])


if __name__ == "__main__":
    process()
