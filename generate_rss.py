import datetime
import requests
from bs4 import BeautifulSoup
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# 目标频道：可改为 https://www.ssydt.com/sszk (时事周刊)
TARGET_URL = "https://www.ssydt.com/article"
BASE_URL = "https://www.ssydt.com"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def build_rss():
    resp = requests.get(TARGET_URL, headers=headers, timeout=15)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = "时事一点通 - 时政日报与热点"
    SubElement(channel, "link").text = TARGET_URL
    SubElement(channel, "description").text = "自动抓取自 ssydt.com 的最新中国时政考点与资讯"

    # 匹配文章列表中的链接（兼容常见的文章详情页路径）
    seen_links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        title = a_tag.get_text(strip=True)

        # 过滤出有效的文章详情链接（排除导航栏和过短的无意义按钮）
        if ("/article/" in href or "/sszk/" in href or "detail" in href) and len(title) > 8:
            full_url = href if href.startswith("http") else BASE_URL + (href if href.startswith("/") else "/" + href)
            if full_url in seen_links:
                continue
            seen_links.add(full_url)

            item = SubElement(channel, "item")
            SubElement(item, "title").text = title
            SubElement(item, "link").text = full_url
            SubElement(item, "guid").text = full_url
            SubElement(item, "pubDate").text = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    xml_str = minidom.parseString(tostring(rss, "utf-8")).toprettyxml(indent="  ", encoding="utf-8")
    with open("ssydt_rss.xml", "wb") as f:
        f.write(xml_str)

if __name__ == "__main__":
    build_rss()
