# testurl.py
import requests
from pathlib import Path

url = "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/closeweight/000902closeweight.xlsx"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, "
        "application/vnd.ms-excel, "
        "application/octet-stream, */*"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.csindex.com.cn/",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
}

out = Path("./downloads")
out.mkdir(parents=True, exist_ok=True)

r = requests.get(
    url,
    headers=headers,
    timeout=60,
    stream=True,
    allow_redirects=True,
)

print(r.status_code, r.reason)
r.raise_for_status()

filepath = out / "000902closeweight.xlsx"
with open(filepath, "wb") as f:
    for chunk in r.iter_content(8192):
        if chunk:
            f.write(chunk)

print(f"✅ 下载完成: {filepath}")
