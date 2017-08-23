#!python3

from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.request import urlopen, quote
import requests
import json
import csv
import time
import re
import os,sys
from math import *  

center_address = {'lat':31.253998, 'lng':121.618554}
homepage_filter_condition = 18 #18km from company
max_from_center = 5
max_from_bus_stop = 1
bus_stop = []
city_bus_stop = []
ak_list = ['GqiA7PxqUc1gKWi979eklStdjI9eh9Kw', 'h8XB8T1z541Tsy5bbAKU0OiGquvAuXKq']
ak_index = 0

house_num = 0
homepage_selected_house_num = 0
selected_house_num = 0
room_list = []

file_name = time.strftime("%Y-%m-%d", time.localtime()) + ".csv"
temp_file_name = "zuber_homepage.html"
csv_file = open(file_name, "a+", encoding="utf-8") 
csv_writer = csv.writer(csv_file, delimiter=';')
driver = webdriver.Chrome(executable_path="E:\Download\python\chromedriver_win32\chromedriver.exe")


def get_lat_and_lng(address):
    global ak_list, ak_index
    url = 'http://api.map.baidu.com/place/v2/suggestion'
    output = 'json'
    ak = ak_list[ak_index]
    add = quote(address) 
    uri = url + '?' + 'query=' + add + '&region=' + quote('上海') + '&city_limit=true' + '&output=' + output + '&ak=' + ak 
    print(uri)
    req = urlopen(uri)
    res = req.read().decode() 
    temp = json.loads(res)
    #print(temp)
    if temp['message'] == "request over":
        ak_index = ak_index + 1
        if ak_index < len(ak_list):
            get_lat_and_lng(address)
        else:
            print('baidu api ak request over')
            exit(0)
    if(len(temp['result']) == 0):
        return 0, 0
    if 'location' in temp['result'][0].keys():
        lat=temp['result'][0]['location']['lat']
        lng=temp['result'][0]['location']['lng']
        return lat, lng
    else:
        return 0, 0

def calcDistance(Lat_A, Lng_A, Lat_B, Lng_B):  
    ra = 6378.140  # 赤道半径 (km)  
    rb = 6356.755  # 极半径 (km)  
    flatten = (ra - rb) / ra  # 地球扁率  
    rad_lat_A = radians(Lat_A)  
    rad_lng_A = radians(Lng_A)  
    rad_lat_B = radians(Lat_B)  
    rad_lng_B = radians(Lng_B)  
    pA = atan(rb / ra * tan(rad_lat_A))  
    pB = atan(rb / ra * tan(rad_lat_B))  
    xx = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(rad_lng_A - rad_lng_B))  
    c1 = (sin(xx) - xx) * (sin(pA) + sin(pB)) ** 2 / cos(xx / 2) ** 2  
    c2 = (sin(xx) + xx) * (sin(pA) - sin(pB)) ** 2 / sin(xx / 2) ** 2  
    dr = flatten / 8 * (c1 - c2)  
    distance = ra * (xx + dr)  
    return distance 

def scroll_to_buttom(times):
    while(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        times = times - 1

def get_rent_house_modified_since_(modified_days):
    while(1):
        time_hints = driver.find_elements_by_css_selector('.room-time.hint')
        #print(time_hints)
        print(time_hints[-1].text)
        if(modified_days == 1):
            if(time_hints[-1].text[:2] == "昨天"):
                break
        else:
            print("not supported yet")
        scroll_to_buttom(10)
    return driver.page_source

def analyze_home_html_file(content):
    soup=BeautifulSoup(content,'lxml')
    house_list = soup.select(".search-list")
    for house in house_list[0].children:
        global house_num
        house_num = house_num + 1

        link = "http://www.zuber.im"+house["href"]
        base_info = house.select(".room-base-info")[0]
        extra_info = house.select(".room-extra-info")[0]
        titile = "".join(base_info.select("h4")[0].stripped_strings)
        address = "".join(base_info.select(".hint")[0].stripped_strings)

        #lat,lng = get_lat_and_lng(address)
        #distance = calcDistance(center_address['lat'], center_address['lng'], lat, lng)   
        #if distance > homepage_filter_condition:
            #continue   

        global homepage_selected_house_num 
        homepage_selected_house_num = homepage_selected_house_num + 1
        rent_type = "".join(base_info.select(".room-base-info-item")[0].select("span")[0].stripped_strings)
        #rent_time = "".join(base_info.select(".room-base-info-item")[0].select("span")[2].stripped_strings)
        price = "".join(extra_info.select(".room-price")[0].stripped_strings)
        if(extra_info.select(".room-type")):
            room_type = "".join(extra_info.select(".room-type")[0].stripped_strings)
        else:
            room_type = " "

        print(titile, address, rent_type, price, room_type, link)
        room_list.append([titile, address, rent_type, price, room_type, link])


def wait_room_address_display(url, try_count):
    global driver
    try_count = try_count + 1
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "room-address")))
    except exceptions.TimeoutException:
        try:
            driver.find_element(By.XPATH, "//*[text()='你查看的租房信息已下架或不存在']")
        except exceptions.NoSuchElementException:
            if(try_count < 3):
                print("刷新页面")
                time.sleep(2)
                driver.refresh()
                return wait_room_address_display(url, try_count)
            elif(try_count < 5):
                print("重启浏览器")
                driver.close()
                time.sleep(5)
                driver = webdriver.Chrome(executable_path="E:\Download\python\chromedriver_win32\chromedriver.exe")
                try:
                    driver.get(url)
                except exceptions.TimeoutException:
                    driver.refresh()
                return wait_room_address_display(url, try_count)
            else:
                print("不存在")
                return "不存在"
        else:
            print("不存在")
            return "不存在"
    else:
        try:
            driver.find_element_by_class_name("room-address")
        except exceptions.NoSuchElementException:
            address = "不存在"
        else:
            address = driver.find_element_by_class_name("room-address").find_elements_by_xpath("span")[1].text
        return address

def get_detail_address(url):
    print(url)
    global driver
    try:
        driver.get(url)
    except exceptions.TimeoutException:
        driver.refresh()
    return wait_room_address_display(url, 0)

def load_bus_stop_address():
    bus_file = open('bus_stop_lat_lng.csv', 'r', encoding="utf-8")
    for line in bus_file.readlines():
        if len(line) > 3:
            bus_stop.append([line.split(',')[0].strip(), line.split(',')[3].strip(), line.split(',')[4].strip()])
    bus_file.close()
    bus_file = open('city_bus_stop_lat_lng.csv', 'r', encoding="utf-8")
    for line in bus_file.readlines():
        if len(line) > 3:
            city_bus_stop.append([line.split(',')[0].strip(), line.split(',')[2].strip(), line.split(',')[3].strip()])
    bus_file.close()

def filter_room_base_detail_address(lat, lng):
    print('房源地址： ', lat, lng)
    if lat == 0:
        return False
    distance = calcDistance(center_address['lat'], center_address['lng'], lat, lng)
    #print('距离公司：', distance)
    if distance < max_from_center:
        return "bike"
    for stop in bus_stop:
        distance = calcDistance(float(stop[1]), float(stop[2]), lat, lng)
        #print('距离班车', stop[0], ': ', distance)
        if distance < max_from_bus_stop:
            return stop[0]
    for stop in city_bus_stop:
        distance = calcDistance(float(stop[1]), float(stop[2]), lat, lng)
        #print('距离公交车', stop[0], ': ', distance)
        if distance < max_from_bus_stop:          
            return stop[0]
    return False

if __name__ == "__main__":
    start_time = time.time() # 开始时间
    start_from_index = 0
    if len(sys.argv) < 2 or sys.argv[1] == "1":
        driver.get("http://www.zuber.im")
        assert "zuber" in driver.title
        html_content = get_rent_house_modified_since_(1)
        temp_file = open(temp_file_name, "w", encoding="utf-8")
        temp_file.write(html_content)
        temp_file.close()

    else:
        if len(sys.argv) == 3:
            start_from_index = int(sys.argv[2])

        temp_file = open(temp_file_name, "r", encoding="utf-8")
        html_content = temp_file.read()
        temp_file.close()

    analyze_home_html_file(html_content)    
    index = 0
    print("共 %d 房源" %(house_num))
    print("第一次筛选出 %d 个房源" %(homepage_selected_house_num))
    load_bus_stop_address()
    for room in room_list:
        index = index + 1
        if index < start_from_index:
            continue
        print("分析第 %d 个房源" %(index))
        address = get_detail_address(room[5])
        print(address) 
        if not (address == "不存在"):
            lat,lng = get_lat_and_lng(address)
            bus_line = filter_room_base_detail_address(lat, lng)
            if(bus_line):
                print('找到一个符合条件的房源')
                selected_house_num = selected_house_num + 1
                room.extend([address, lat, lng, bus_line])
                print(room)
                csv_writer.writerow(room)
                csv_file.flush()
    csv_file.close()
    end_time = time.time() #结束时间
    print(" 程序耗时%f秒.共 %d 房源.第一次筛选出 %d 个房源.最终筛选到%d个房源" % 
        ((end_time - start_time), house_num, homepage_selected_house_num, selected_house_num))