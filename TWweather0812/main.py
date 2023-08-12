import requests
import csv
from datetime import datetime
import pytz
import os
import pandas as pd
import streamlit as st

def download_data()->dict:
    url = 'https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/F-C0032-001?Authorization=rdec-key-123-45678-011121314&format=JSON'

    response = requests.get(url)
    if response.status_code == 200:
        print("下載成功")
    return response.json()

def jsonDict_csvList(json)->list[dict]:
    '''
    - 傳入josn的資料結構
    - 取出需要的資料
    - 組合成list[dict]
    '''
    location = json['cwbopendata']['dataset']['location']
    weather_list = []
    for item in location:
        city_item = {}
        city_item['城市'] = item['locationName']
        city_item['啟始時間'] = item['weatherElement'][1]['time'][0]['startTime']
        city_item['結束時間'] = item['weatherElement'][1]['time'][0]['endTime']
        city_item['最高溫度'] = float(item['weatherElement'][1]['time'][0]['parameter']['parameterName'])
        city_item['最低溫度'] = float(item['weatherElement'][2]['time'][0]['parameter']['parameterName'])
        city_item['感覺'] = item['weatherElement'][3]['time'][0]['parameter']['parameterName']
        weather_list.append(city_item)
    return weather_list

def save_csv(data:list[dict],fileName) -> bool:
    '''
    - 將list[dict]儲存
    - 參數fileName要儲存的檔案名
    '''    
    with open(fileName,mode='w',encoding='utf-8',newline='') as file:
        fieldnames = ['城市', '啟始時間','結束時間','最高溫度','最低溫度','感覺']
        writer = csv.DictWriter(file,fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    return True

def get_csvName()->str:
    '''
    - 取得台灣目前year-month-day.csv
    '''
    taiwan_timezone = pytz.timezone('Asia/Taipei')
    current_date = datetime.now(taiwan_timezone)    
    fileName = f"{current_date.year}-{current_date.month}-{current_date.day}.csv"
    return fileName

def  get_fileName_path()->str:
    csvFileName = get_csvName()
    current_cwd = os.path.abspath(os.getcwd())
    abs_file_path = os.path.join(current_cwd,'data',csvFileName)
    return abs_file_path


def check_file_exist()->bool:
    abs_file_path = get_fileName_path()    
    if os.path.exists(abs_file_path):
        return True
    else:
        return False

if not check_file_exist():
    print("不存在")
    json_data = download_data()
    csv_list = jsonDict_csvList(json_data)
    is_save = save_csv(csv_list,get_fileName_path())
    if is_save:
        print("存檔成功")  

file_path = get_fileName_path()
dataFrame = pd.read_csv(file_path)
# 把原本 dataFrame 裡面輸出的 object 轉成時間物件 (從字串轉成 series)

# google: pandas.Series.dt.strftime
dataFrame['啟始時間'] = pd.to_datetime(dataFrame['啟始時間'])
dataFrame['結束時間'] = pd.to_datetime(dataFrame['結束時間'])
dataFrame['啟始時間'] = dataFrame['啟始時間'].dt.strftime('%Y-%m-%d日-%H點')
dataFrame['結束時間'] = dataFrame['結束時間'].dt.strftime('%Y-%m-%d日-%H點')
dataFrame['Tmax'] = dataFrame['Tmax'].astype(int)
dataFrame['Tmin'] = dataFrame['Tmin'].astype(int)

# 更改 streamlit 外觀樣式: dataFrame.style.highlight_max -> subset
style = dataFrame.style.highlight_max(subset=['最高溫度'],axis=0) # 黃色預設
style = dataFrame.style.highlight_max(subset=['最高溫度'],axis=0,props="color:white;background-color:red;")
style = style.highlight_max(subset=['最低溫度'],axis=0,props="color:white;background-color:blue;")

# style 裡面: props= -> 是 css 的語法
style = dataFrame.style.highlight_max(subset=['最高溫度'],axis=0) # background color, font coloer



# 顯示標題
st.title("台灣各縣市氣候:")
st.subheader("攝氏")

# DataFrame
st.dataframe(dataFrame,width=800,height=900)        
st.line_chart(dataFrame,x='城市',y=['最高溫度','最低溫度'])
st.area_chart(dataFrame,x='城市',y=['最高溫度','最低溫度'])