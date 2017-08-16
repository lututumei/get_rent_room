#!python3

from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time
import re
import os,sys

driver = webdriver.Chrome(executable_path="E:\Download\python\chromedriver_win32\chromedriver.exe")
#driver.implicitly_wait(10)

filter_address_list = ["12号线金海路", "12号线申江路", "12号线金京路", "12号线杨高北路", "12号线巨峰路", "12号线东陆路", 
"6号线", 
"2号线东昌路", "2号线世纪大道", "2号线上海科技馆", "2号线世纪公园", "2号线龙阳路", "2号线张江高科", "2号线金科路", 
"2号线广兰路", "2号线唐镇", "2号线创新中路", "2号线华夏东路", "2号线川沙",
"7号线花木路", "7号线龙阳路", "7号线芳华路", "7号线锦绣路", "7号线杨高南路", "7号线高科西路", "7号线云台路", "7号线耀华路", "7号线长清路", "7号线后滩",
"11号线御桥", "11号线浦三路", "11号线三林东", "11号线三林"]
house_num = 0
room_list = []
file_name = time.strftime("%Y-%m-%d", time.localtime()) + ".csv"
temp_file_name = "zuber_homepage.html"

csv_file = open(file_name, "w", encoding="utf-8") 
csv_writer = csv.writer(csv_file, delimiter=';')

def scroll_to_buttom(times):
    while(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        times = times - 1

def get_rent_house_modified_since_(modified_days):
    while(1):
        time_hints = driver.find_elements_by_css_selector(".room-time.hint")
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

        link = "http://www.zuber.im"+house["href"]

        base_info = house.select(".room-base-info")[0]
        extra_info = house.select(".room-extra-info")[0]

        titile = "".join(base_info.select("h4")[0].stripped_strings)
        address = "".join(base_info.select(".hint")[0].stripped_strings)

        record_this_info =False
        if(address.find('号线') == -1):
            record_this_info = True
        for filter in filter_address_list:
            if(address.find(filter) != -1):
                record_this_info = True
        if(not record_this_info):
            continue

        global house_num 
        house_num = house_num + 1
        #rent_type = "".join(base_info.select(".room-base-info-item")[0].select("span")[0].stripped_strings)
        #rent_time = "".join(base_info.select(".room-base-info-item")[0].select("span")[2].stripped_strings)
        price = "".join(extra_info.select(".room-price")[0].stripped_strings)
        '''if(extra_info.select(".room-type")):
            room_type = "".join(extra_info.select(".room-type")[0].stripped_strings)
        else:
            room_type = " "
        '''

        #print(titile, address, rent_type, rent_time, price, room_type, link)
        #csv_writer.writerow([titile, address, rent_type, rent_time, price, room_type, link])
        print(titile, address, price, link)
        room_list.append([titile, address, price, link])

def wait_room_address_display(try_count):
    global driver
    try_count = try_count + 1
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "room-address")))
    except exceptions.TimeoutException:
        try:
            driver.findElement(By.xpath("//*[text()='已下架或不存在']"))
        except exceptions.NoSuchElementException:
            if(try_count < 3):
                print("刷新页面")
                time.sleep(2)
                driver.refresh()
                return wait_room_address_display(try_count)
            else:
                print("重启浏览器")
                driver.close()
                time.sleep(5)
                driver = webdriver.Chrome(executable_path="E:\Download\python\chromedriver_win32\chromedriver.exe")
                driver.get(url)
                return wait_room_address_display(try_count)
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
        print(address)
        return address

def get_detail_address(url):
    print(url)
    global driver
    driver.get(url)
    return wait_room_address_display(0)

if __name__ == "__main__":
    start_time = time.time() # 开始时间
    if len(sys.argv) < 2 or sys.argv[1] == "1":
        driver.get("http://www.zuber.im")
        assert "zuber" in driver.title
        html_content = get_rent_house_modified_since_(1)
        temp_file = open(temp_file_name, "w", encoding="utf-8")
        temp_file.write(html_content)
        temp_file.close()

    elif sys.argv[1] == "2":
        temp_file = open(temp_file_name, "r", encoding="utf-8")
        html_content = temp_file.read()
        temp_file.close()

    analyze_home_html_file(html_content)
    index = 0
    print("共 %d 个房源" %(house_num))
    for room in room_list:
        index = index + 1
        print("分析第 %d 个房源" %(index))
        address = get_detail_address(room[3])
        if not (address == "不存在"):
            room.append(address)
            csv_writer.writerow(room)
    csv_file.close()
    end_time = time.time() #结束时间
    print(" 程序耗时%f秒.共抓取到%d个房源" % ((end_time - start_time), house_num))