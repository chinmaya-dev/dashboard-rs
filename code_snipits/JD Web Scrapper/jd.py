from bs4 import BeautifulSoup
import urllib.parse, urllib.error
from urllib.request import Request, urlopen
import requests
import csv
import ssl

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = input('Enter - ')
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urlopen(req).read()

soup = BeautifulSoup(html, 'lxml')

csv_file = open('cms_scrape.csv', 'w')

csv_writer = csv.writer(csv_file)
csv_writer.writerow(['name', 'address'])

for li in soup.find_all('li', class_='cntanr'):
    name = li.h2.span.a['title']
    print(name)


    address = li.find('p', class_='address-info tme_adrssec').a.find('span', class_='cont_fl_addr').text
    print(address)

    print()

    csv_writer.writerow([name, address])

csv_file.close()