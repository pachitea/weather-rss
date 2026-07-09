import os
import requests
from datetime import datetime, timezone
from email.utils import format_datetime

# Yahoo! 気象情報APIのClient ID
# GitHub Secrets に YAHOO_APPID という名前で登録しておく
APPID = os.environ["YAHOO_APPID"]

# 浜松町駅の座標
# Yahoo! APIは 「緯度,経度」の順
COORDINATES = "139.75694,35.6550"

# Yahoo! 気象情報API
URL = "https://map.yahooapis.jp/weather/V1/place"

# APIリクエストパラメータ
params = {
    "coordinates": COORDINATES,
    "appid": APPID,
    "output": "json",
    "interval": "5"
}

# APIを呼び出す
response = requests.get(URL, params=params, timeout=10)

# HTTPエラーがあれば停止
response.raise_for_status()

# JSONをPythonの辞書型へ変換
data = response.json()

# Weather配列を取得
weather_list = data["Feature"][0]["Property"]["WeatherList"]["Weather"]

# 先頭は現在の観測値 observation
current = weather_list[0]

# 必要な値を取得
weather_type = current["Type"]          # observation / forecast
date_raw = current["Date"]              # 例: 202607091100
rainfall = current["Rainfall"]          # 降水強度 mm/h

# 日時を見やすい形へ変換
date_text = (
    f"{date_raw[0:4]}-{date_raw[4:6]}-{date_raw[6:8]} "
    f"{date_raw[8:10]}:{date_raw[10:12]}"
)

# 現在雨が降っているか判定
is_raining = rainfall > 0

# 表示用メッセージ
message = "現在、雨が降っています" if is_raining else "現在、雨は降っていません"

# Power AutomateのRSSトリガー用
# 毎回GUIDを変えることで、新しいRSS項目として認識させる
guid = datetime.now(timezone.utc).isoformat()

# RSSの公開日時
pub_date = format_datetime(datetime.now(timezone.utc))

# RSSを作成
rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>

    <title>Tokyo Station Rainfall</title>

    <link>https://developer.yahoo.co.jp/webapi/map/openlocalplatform/v1/weather.html</link>

    <description>
      Rainfall information for Tokyo Station
    </description>

    <item>

      <title>{message}</title>

      <description><![CDATA[
Date={date_text}
Type={weather_type}
Rainfall={rainfall}
IsRaining={str(is_raining).lower()}
Message={message}
]]></description>

      <guid>{guid}</guid>

      <pubDate>{pub_date}</pubDate>

    </item>

  </channel>
</rss>
"""

# feed.xmlとして保存
with open("feed.xml", "w", encoding="utf-8") as f:
    f.write(rss)

print("feed.xml を作成しました。")
print(message)
print(f"Rainfall={rainfall}")
