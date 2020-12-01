import requests
import io
import pandas as pd

header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Length": "18",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "usr=48527; pwd=93fd3060131f8f9e8410775809f0a231"
}

data = {
    "status": "1",
    "id": "2"
}

r = requests.post('https://ulinc.co/5676186/campaigns/2/?do=campaigns&act=export', headers=header, data=data)

if r.ok:
    data = r.content.decode('utf-8')
    # print(data)
    df = pd.read_csv(io.StringIO(data))

    print(df.iloc[0])