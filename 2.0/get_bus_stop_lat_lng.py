from urllib.request import urlopen, quote
import requests
import json
import csv

filter_time = '7:20'

def get_lat_and_lng(address):
    url = 'http://api.map.baidu.com/place/v2/suggestion'
    output = 'json'
    ak = 'h8XB8T1z541Tsy5bbAKU0OiGquvAuXKq'
    add = quote(address) 
    uri = url + '?' + 'query=' + add + '&region=' + quote('上海') + '&city_limit=true' + '&output=' + output + '&ak=' + ak 
    print(uri)
    req = urlopen(uri)
    res = req.read().decode() 
    temp = json.loads(res)
    print(temp['result'][0])
    lat=temp['result'][0]['location']['lat']
    lng=temp['result'][0]['location']['lng']
    print(lat, ' ', lng)
    return lat,lng

if __name__ == "__main__":
    file = open('regular_bus.csv', 'r', encoding="utf-8")
    file_save = open('bus_stop_lat_lng.csv', 'w',  encoding="utf-8")
    csv_writer = csv.writer(file_save, delimiter=',')
    for line in file.readlines():
        print (line)
        if len(line) < 3 :
            continue
        bus_line = line.split(',')[0]
        time = line.split(',')[1]
        print (bus_line, ' ', time)
        if time.startswith('7') and int(time[2:]) > int(filter_time[2:]):
            print(bus_line, 'selected')

            address = line.split(',')[3].strip()
            print(address)
            lat,lng = get_lat_and_lng(address)
            print(bus_line, ' ', time, ' ', address, ' ', lat, ' ', lng)
            csv_writer.writerow([bus_line, time, address, lat, lng])
    file.close()
    file_save.close()

    file = open('city_bus.csv', 'r', encoding="utf-8")
    file_save = open('city_bus_stop_lat_lng.csv', 'w',  encoding="utf-8")
    csv_writer = csv.writer(file_save, delimiter=',')
    for line in file.readlines():
        print (line)
        if len(line) < 3 :
            continue
        bus_line = line.split(',')[0]
        address = line.split(',')[2].strip()
        print(address)
        lat,lng = get_lat_and_lng(address)
        print(bus_line, ' ', address, ' ', lat, ' ', lng)
        csv_writer.writerow([bus_line, address, lat, lng])
    file.close()
    file_save.close()