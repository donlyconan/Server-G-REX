import json
import time

import requests
from bs4 import BeautifulSoup

import common.formatter as fm

BASE_URL = "https://vnweather.net/"
URL_WEBSITE = "https://vnweather.net/?fc_city=%s"
FILTER_DAY = ['Hôm nay', 'Chủ nhật', 'Thứ', 'Ngày mai']
KEY_JSON_WEATHER = ['thoigian', 'dubao', 'nhietdo', 'mua', 'khiap', 'gio']
img_current_weather = None





def read_titles(format_table):
    titles = []
    for child in format_table.children:
        if child.name == 'strong':
            titles.append(child.string)
        if child.name == 'span':
            titles[-1] += child.string

    return titles

"""
Bang du lieu: class_= format-table && id = fc_weather
Thoi gian: strong, span
Table: class_= table table-striped
"""


"""
Dinh dang html
<tbody>
    <tr>
        <td>22:00-00:00</td>
        <td><img src="images/sym/v2016/png/38/03n.png" title="Có mây"/> Có mây</td>
        <td><strong style="color: #FF8C00;" title="Vào lúc: 22:00">28 °C</strong></td>
        <td><span title="Thời gian: 22:00-00:00">0 mm</span></td>
        <td class="info_atmos"> <span title="Vào lúc: 22:00">1005.3 hPa</span></td>
        <td class="info_wind"><i class="wi wi-wind wi-from-ese" title="Vào lúc: 22:00"></i> ĐĐN, 10.08 km/h</td>
    </tr>
</tbody>
"""
def read_data_from_table(data_table):
    global img_current_weather

    tbody = data_table.find("tbody")

    trs = tbody.find_all("tr")
    data = []

    for tr in trs:
        """
        Lay url cua the img: table>tbody>tr>td
        <img src="images/sym/v2016/png/38/04.png" title="Nhiều mây">
        """

        if not img_current_weather:
            img_current_weather = tr.find("img").get("src")

        tds = tr.find_all("td")
        data.append([x.get_text() for x in tds])

    return data

"""
title: 
    ['Hôm nay,Thứ Tư 03/06/2020', 'Ngày mai,Thứ Năm 04/06/2020', 'Thứ Sáu, 05/06/2020']
datatable: 
    [['17:00-18:00', ' Mưa nhỏ', '32 °C', '0.2 mm', '1001.2 hPa', ' ĐN, 10.8 km/h'], ['18:00-00:00', ' Có mưa', '31 °C', '2.3 mm', '1002.0 hPa', ' ĐN, 9.36 km/h']]
"""

def convert_table_to_dict(title ,data_table):
    table = read_data_from_table(data_table)
    json_data = fm.convert_array_tojson(KEY_JSON_WEATHER, table)
    dict = {
        'title': title,
        'info': json_data
    }
    return dict


"""
[['17:00-18:00', ' Có mây', '34 °C', '0 mm', '998.4 hPa', ' NĐN, 12.24 km/h', '18:00-00:00', ' Nhiều mây', '33 °C', '0 mm', '998.7 hPa', ' NĐN, 8.64 km/h']]
[['00:00-06:00', ' Nhiều mây', '29 °C', '0 mm', '1000.1 hPa', ' N, 13.32 km/h', '06:00-12:00', ' Nhiều mây', '29 °C', '0 mm', '1000.3 hPa', ' TN, 9.72 km/h', '12:00-18:00', ' Nhiều mây', '36 °C', '0 mm', '1000.3 hPa', ' TTN, 12.96 km/h', '18:00-00:00', ' Nhiều mây', '34 °C', '0 mm', '997.5 hPa', ' ĐĐN, 8.64 km/h']]
[['00:00-06:00', ' Nhiều mây', '31 °C', '0 mm', '999.5 hPa', ' NTN, 7.56 km/h', '06:00-12:00', ' Nhiều mây', '28 °C', '0 mm', '1001.7 hPa', ' B, 11.16 km/h', '12:00-18:00', ' Nhiều mây', '30 °C', '0 mm', '1003.5 hPa', ' ĐB, 10.8 km/h', '18:00-00:00', ' Mưa to', '31 °C', '6.6 mm', '1002.3 hPa', ' ĐĐB, 6.48 km/h']]
"""

def read_html_from_website(city='HANOI', index=-1):
    global img_current_weather

    img_current_weather = None

    cur = time.time()
    req = requests.get(URL_WEBSITE % city)
    """
        1.Lay html
        2.Lay title va table body chua bang thoi tiet
        3.Loc du lieu cua 3 bang thoi tiet tu 3 bang tren
        4.Ghep cap tra ve dang json
    """
    html = BeautifulSoup(req.content, 'html.parser')
    print(f"End read html: %.5f"%(time.time()-cur))

    # tim phan vung chua id fc_weather
    format_table = html.find(id="fc_weather")

    #doc tieu de
    titles = read_titles(format_table)

    title_place = format_table.find_next('h3').string


    #doc du lieu tu cac bang
    data_tables = format_table.find_all(class_="table table-striped")

    json_arr = []

    if index != -1 and index < len(titles):
        dict = convert_table_to_dict(titles[index], data_tables[index])
        json_arr.append(dict)

    else:
        for x in range(len(titles)):
            dict = convert_table_to_dict(titles[x], data_tables[x])
            json_arr.append(dict)

    return json.dumps({'title-place': title_place ,"img-current-weather": BASE_URL + img_current_weather , 'tables': json_arr})


print(read_html_from_website())