import requests
from datetime import datetime, timezone
from email.utils import format_datetime

# Open-Meteo API（東京駅）
URL = "https://api.open-meteo.com/v1/forecast?latitude=35.6812&longitude=139.7671&current=rain,precipitation,is_day"

# APIを呼び出す
response = requests.get(URL, timeout=10)

# HTTPステータスコードが200番台以外の場合はエラーとする
# （API障害や404などを早く検知できる）
response.raise_for_status()

# レスポンス(JSON)をPythonの辞書型へ変換
data = response.json()

# currentオブジェクトを取得
current = data["current"]

# 必要な値を取得
rain = current["rain"]                     # 雨量(mm)
precipitation = current["precipitation"]   # 降水量(mm)
is_day = current["is_day"]                 # 昼:1 夜:0
weather_time = current["time"]             # APIが保持する観測時刻

# RSSのGUID
# Power AutomateのRSSトリガーはGUIDが変わると新しい記事として認識する。
# 毎回現在時刻を設定することで、RSS更新のたびにフローを起動できる。
guid = datetime.now(timezone.utc).isoformat()

# RSSの公開日時
# RFC2822形式（例: Wed, 08 Jul 2026 02:20:31 GMT）へ変換
pub_date = format_datetime(datetime.now(timezone.utc))

# RSS(XML)を作成
rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>

    <title>Tokyo Station Weather</title>

    <link>https://open-meteo.com/</link>

    <!-- RSSチャンネルの説明 -->
    <description>
      Weather information for Tokyo Station
    </description>

    <!-- Open-Meteoのライセンス表記 -->
    <copyright>
      Weather data © Open-Meteo.com (CC BY 4.0)
    </copyright>

    <item>

      <title>Tokyo Station Weather</title>

      <!--
      CDATAで囲むことでXML特殊文字(<、>、&)を
      エスケープせずそのまま記載できる。
      Power Automateでも取得しやすい。
      -->
      <description><![CDATA[
API Time={weather_time}
Rain={rain}
Precipitation={precipitation}
Day={is_day}
]]></description>

      <!--
      GUIDはRSS記事を一意に識別するID。
      毎回変更することでPower Automateが
      新しいRSS記事として認識する。
      -->
      <guid>{guid}</guid>

      <!-- RSSの公開日時 -->
      <pubDate>{pub_date}</pubDate>

    </item>

  </channel>
</rss>
"""

# feed.xmlとして保存
with open("feed.xml", "w", encoding="utf-8") as f:
    f.write(rss)

# ログ出力
print("feed.xml を作成しました。")