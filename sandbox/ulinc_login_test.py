import requests


header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    # "Accept-Encoding": "gzip, deflate, br",
    # "Accept-Language": "en-US,en;q=0.9",
    # "Cache-Control": "max-age=0",
    # "Connection": "keep-alive",
    # "Content-Length": "54",
    # "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "",
    # "dnt": "1",
    # "Host": "ulinc.co",
    # "Origin": "https://ulinc.co",
    "Referer": ""
    # "Sec-Fetch-Dest": "document",
    # "Sec-Fetch-Mode": "navigate",
    # "Sec-Fetch-Site": "same-origin",
    # "Sec-Fetch-User": "?1",
    # "sec-gpc": "1",
    # "Upgrade-Insecure-Requests": "1",
    # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
}

url = "https://ulinc.co"
login_url = "https://ulinc.co/login/?email=jhawkes20@gmail.com&password=JA12345!&sign=1"

session = requests.Session()
# print(session.cookies.get_dict())

# main = session.get(url=url)
# print(main.cookies.get_dict())
# header['Cookie'] = "PHPSESSID={}".format(main.cookies.get('PHPSESSID'))

login = session.post(url=login_url)
# print(login.cookies.get_dict())
# phpsessid = r.cookies.get('PHPSESSID')

print(len(login.history))
print(login.history[0].cookies.get_dict())

# if r.ok:
#     # print(r.url)
#     # print(r.history)
#     print(r.headers)
#     # print(r.cookies.get('PHPSESSID'))
#     # print(r.text)
