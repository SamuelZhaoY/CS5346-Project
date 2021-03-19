import json
import csv

def convertPostalDistrictToDistrictDisplay(district):
	if district == '01':
		return 'Raffles Place, Cecil, Marina, People’s Park'
	elif district == '02':
		return 'Anson, Tanjong Pagar'
	elif district == '03':
		return 'Queenstown, Tiong Bahru'
	elif district == '04':
		return 'Telok Blangah, Harbourfront'
	elif district == '05':
		return 'Pasir Panjang, Hong Leong Garden, Clementi New Town'
	elif district == '06':
		return 'High Street, Beach Road'
	elif district == '07':
		return 'Middle Road, Golden Mile'
	elif district == '08':
		return 'Little India'
	elif district == '09':
		return 'Orchard, Cairnhill, River Valley'
	elif district == '10':
		return 'Ardmore, Bukit Timah, Holland Road, Tanglin'
	elif district == '11':
		return 'Watten Estate, Novena, Thomson'
	elif district == '12':
		return 'Balestier, Toa Payoh, Serangoon'
	elif district == '13':
		return 'Macpherson, Braddell'
	elif district == '14':
		return 'Geylang, Eunos'
	elif district == '15':
		return 'Katong, Joo Chiat, Amber Road'
	elif district == '16':
		return 'Bedok, Upper East Coast, Eastwood, Kew Drive'
	elif district == '17':
		return 'Loyang, Changi'
	elif district == '18':
		return 'Tampines, Pasir Ris'
	elif district == '19':
		return 'Serangoon Garden, Hougang, Punggo'
	elif district == '20':
		return 'Bishan, Ang Mo Kio'
	elif district == '21':
		return 'Upper Bukit Timah, Clementi Park, Ulu Pandan'
	elif district == '22':
		return 'Jurong'
	elif district == '23':
		return 'Hillview, Dairy Farm, Bukit Panjang, Choa Chu Kang'
	elif district == '24':
		return 'Lim Chu Kang, Tengah'
	elif district == '25':
		return 'Kranji, Woodgrove'
	elif district == '26':
		return 'Upper Thomson, Springleaf'
	elif district == '27':
		return 'Yishun, Sembawang'
	elif district == '28':
		return 'Seletar'
	return 'unkown'

hdb_town_mapping = {"SEMBAWANG": '27',
  "WOODLANDS": '25',
  "YISHUN": '27',
  "ANG MO KIO" : "20",
  "HOUGANG" : "19",
  "PUNGGOL" : "19",
  "SENGKANG" : "19",
  "SERANGOON" : "12",
  "BEDOK" : "16",
  "PASIR RIS" : "18",
  "TAMPINES" : "18",
  "BUKIT BATOK" : "23",
  "BUKIT PANJANG" : "23",
  "CHOA CHU KANG" : "23",
  "CLEMENTI" : "05",
  "JURONG EAST" : "22",
  "JURONG WEST" : "22",
  "TENGAH" : "24",
  "BISHAN" : "20",
  "BUKIT MERAH" : "04",
  "BUKIT TIMAH" : "10",
  "CENTRAL" : "02",
  "GEYLANG" : "14",
  "KALLANG/WHAMPOA" : "14",
  "MARINE PARADE" : "15",
  "QUEENSTOWN" : "03",
  "LIM CHU KANG": "24",
  "TOA PAYOH" : "12",}

def hdb_town_to_district(town_name):
  if (town_name in hdb_town_mapping):
    return hdb_town_mapping.get(town_name)
  print('unknown HDB town: %s' % town_name)
  return 'unkown'


def process_condo():
  # output: quarter, district, district_display, project, median_rent
  with open('condo.json') as input, open('condo_processed.csv', 'w', newline='') as output:
      csvwriter = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      data = json.load(input)
      csvwriter.writerow(['quarter', 'district', 'district_display', 'project', 'median_rent'])
      for entry in data['Result']:
          for record in entry["rentalMedian"]:
            csvwriter.writerow([record['refPeriod'], record['district'], convertPostalDistrictToDistrictDisplay(record['district']), entry["project"], record['median']])


def get_valid_quarter(quarter):
  split_q = quarter.split('-')
  if int(split_q[0]) < 2018:
    return False, ''
  return True, quarter.replace('-', '')
  
def amount_to_int(price):
  try:
    return int(price)
  except ValueError:
    return 0

def process_hdb():
  # output: quarter, district, district_display, flat_type, median_rent
  with open('hdb_raw.csv') as input, open('hdb_processed.csv', 'w', newline='') as output:
      csvreader = csv.reader(input, delimiter=',')
      csvwriter = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      line_count = 0
      csvwriter.writerow(['quarter', 'district', 'district_display', 'flat_type', 'median_rent'])
      # input row: "quarter,town,flat_type,median_rent"
      for row in csvreader:
        if line_count == 0:
            line_count += 1
        else:
            is_valid, quarter_str = get_valid_quarter(row[0])
            if not is_valid:
              continue
            district = hdb_town_to_district(row[1])
            district_display = convertPostalDistrictToDistrictDisplay(district)
            csvwriter.writerow([quarter_str, district, district_display, row[2], amount_to_int(row[3])])



if __name__ == '__main__':
  process_hdb()
