import streamlit as st
import time
#import slackweb
import requests
from datetime import datetime  
import pytz

#アクセストークン取得
st.markdown('<a href="https://dev.fitbit.com/build/reference/web-api/troubleshooting-guide/oauth2-tutorial/?clientEncodedId=23PGQV&redirectUri=https://localhost&applicationType=PERSONAL" target="_blank">アクセストークンを取得する</a>', unsafe_allow_html=True)

#Slack_url = st.text_input('SlackのURLを入力してください')
ACCESS_TOKEN = st.text_input('取得したアクセストークンを入力して、分析を開始してください') 

GOOGLE_API_KEY = "AIzaSyAguWH3Q57gYvNx91lbDbOQMEx6QxZ-dgM"

#プログラムを動かす
start_btn = st.button("分析開始")

#現在時刻取得
def get_current_time():
    utc_now = datetime.now(pytz.utc)
    japan_tz = pytz.timezone('Asia/Tokyo')
    japan_time = utc_now.astimezone(japan_tz)
    return japan_time.strftime("%H時%M分")  

#心拍数取得
def fetch_heart_rate():
    url = "https://api.fitbit.com/1/user/-/activities/heart/date/today/1d/1min.json"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    response = requests.get(url, headers=headers)

    if response.ok:
        data = response.json()
        
        try:
            heart_activities = data['activities-heart-intraday']['dataset']
            latest = heart_activities[-3:]  # 最新のデータを取得
            heart_rates = [entry['value'] for entry in latest]
            
            if heart_rates:
                average_heart_rate = sum(heart_rates) / len(heart_rates)
                st.subheader("更新時間:" + get_current_time()) #データ取得時間を表示
                st.text(f"最新の心拍数データ:{[entry['time'] for entry in latest]}")
                st.text(f"平均心拍数:{average_heart_rate:.2f}")
                
                if average_heart_rate > 80:
                    st.text("☆心拍数の平均値が80を超えています! Slackにも通知をしました。")
                    #slack = slackweb.Slack(url=Slack_url)
                    #slack.notify(text="飲みすぎていませんか？？")  # アラート内容
            else:
                st.text("データが見つかりませんでした。")

        except KeyError:
            st.text("Expected data format not found in response.")
    else:
        st.text(f"Request failed: {response.status_code}")

#歩数取得
def fetch_steps():
    url = "https://api.fitbit.com/1/user/-/activities/steps/date/today/1d.json"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    response = requests.get(url, headers=headers)

    if response.ok:
        data = response.json()
        
        try:
            steps = data['activities-steps'][0]['value']
            st.text(f"現在の歩数:{steps}")
        except KeyError:
            st.text("Expected data format not found in response.")
    else:
        st.text(f"Request failed: {response.status_code}")

#現在地取得
def fetch_geolocation():
    url = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + GOOGLE_API_KEY
    payload = {"considerIp": "true"}  # IPによる推定位置を取得

    response = requests.post(url, json=payload)

    if response.ok:
        data = response.json()
        latitude = data['location']['lat']
        longitude = data['location']['lng']
        st.text(f"現在地:緯度 {latitude}, 経度 {longitude}")
    else:
        st.text(f"Failed to fetch geolocation data: {response.status_code}")

def main_loop():
    while True:
        fetch_heart_rate()
        fetch_steps()  
        fetch_geolocation()
        st.text("-------------------------------------------------------")
        time.sleep(60)  # 待機時間

#スタートボタンが押されたらmain_loopを開始
if __name__ == "__main__":
    if start_btn:
        main_loop()
        