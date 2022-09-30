import requests
import json
# url = "https://e.waimai.meituan.com/v2/index/r/businessOverview?ignoreSetRouterProxy=true&optimus_uuid=f4597f79-0705-4263-b485-a5f1fcaf7f98&optimus_risk_level=71&optimus_code=10&optimus_partner=19"

url = "https://e.waimai.meituan.com/api/poi/poiList?ignoreSetRouterProxy=true"


# cookies_str = "device_uuid=!f4597f79-0705-4263-b485-a5f1fcaf7f98; uuid_update=true; uuid=b8d074353a881d315079.1658286877.1.0.0; _lxsdk_cuid=1821999a89dc8-0c0a0fa1fdca6-673b5753-384000-1821999a89dc8; _lxsdk=1821999a89dc8-0c0a0fa1fdca6-673b5753-384000-1821999a89dc8; _ga=GA1.1.1293939431.1660035005; _ga_LYVVHCWVNG=GS1.1.1660035005.1.1.1660035129.0; pushToken=0m1Eh2ETGqu_OxHj5BTEMuly8luXpR8r9om0Z7sbVvNY*; _lx_utm=utm_source%3Dbaidu%26utm_medium%3Dorganic%26utm_term%3D%25E7%25BE%258E%25E5%259B%25A2%25E5%25A4%2596%25E5%258D%2596%25E5%2595%2586%25E5%25AE%25B6; wpush_server_url=wss://wpush.meituan.com; acctId=65908986; token=0Aeq2XfObw9ey4iJCYs3RwXSloo1sg4RqfFw7UFssKNc*; brandId=-1; isOfflineSelfOpen=0; city_id=0; isChain=1; existBrandPoi=true; ignore_set_router_proxy=true; region_id=; region_version=0; newCategory=false; bsid=WXL0xFqSmjMFHsXhkmzQ6sFa1EB8uwXzhn9BE4qpoFVVR-8pr5_ucOqBLzOG3BqBoYK3ryyeAjbXoeEXfC37pw; city_location_id=0; location_id=0; cityId=450900;provinceId=450000; wmPoiName=Bigbear%E9%9F%A9%E5%9B%BD%E7%82%B8%E9%B8%A1%EF%BC%88%E6%B1%89%E5%A0%A1%C2%B7%E9%92%9F%E6%A5%BC%E5%BA%97%EF%BC%89; logistics_support=; shopCategory=food; setPrivacyTime=3_20220925; wmPoiId=8519956; JSESSIONID=1ma5xodbawe4mr5o30946lkb5; set_info=%7B%22wmPoiId%22%3A-1%2C%22ignoreSetRouterProxy%22%3Atrue%7D; logan_session_token=71enhxj1c45r6ezmzkay; _lxsdk_s=18373525fb5-ad5-b32-f42%7C%7C215"

cookies_str = "device_uuid=!f4597f79-0705-4263-b485-a5f1fcaf7f98; uuid_update=true; uuid=b8d074353a881d315079.1658286877.1.0.0; _lxsdk_cuid=1821999a89dc8-0c0a0fa1fdca6-673b5753-384000-1821999a89dc8; _lxsdk=1821999a89dc8-0c0a0fa1fdca6-673b5753-384000-1821999a89dc8; _ga=GA1.1.1293939431.1660035005; _ga_LYVVHCWVNG=GS1.1.1660035005.1.1.1660035129.0; pushToken=0m1Eh2ETGqu_OxHj5BTEMuly8luXpR8r9om0Z7sbVvNY*; _lx_utm=utm_source%3Dbaidu%26utm_medium%3Dorganic%26utm_term%3D%25E7%25BE%258E%25E5%259B%25A2%25E5%25A4%2596%25E5%258D%2596%25E5%2595%2586%25E5%25AE%25B6; wpush_server_url=wss://wpush.meituan.com; acctId=65908986; token=0Aeq2XfObw9ey4iJCYs3RwXSloo1sg4RqfFw7UFssKNc*; brandId=-1; isOfflineSelfOpen=0; city_id=0; isChain=1; existBrandPoi=true; ignore_set_router_proxy=true; region_id=; region_version=0; newCategory=false; bsid=WXL0xFqSmjMFHsXhkmzQ6sFa1EB8uwXzhn9BE4qpoFVVR-8pr5_ucOqBLzOG3BqBoYK3ryyeAjbXoeEXfC37pw; city_location_id=0; location_id=0; cityId=450900; provinceId=450000; logistics_support=; setPrivacyTime=3_20220925; wmPoiName=Bigbear%E9%9F%A9%E5%9B%BD%E7%82%B8%E9%B8%A1%EF%BC%88%E9%93%B6%E9%83%BD%E5%BA%97%EF%BC%89; shopCategory=food; wmPoiId=-1; JSESSIONID=wmam8fl7wxki17aen56v14b5c; _lxsdk_s=18373525fb5-ad5-b32-f42%7C%7C506; logan_session_token=00n29gagh79hqdk6r55s; set_info=%7B%22wmPoiId%22%3A%22-1%22%2C%22ignoreSetRouterProxy%22%3Atrue%7D"

cookies_dict = {}

# cookies_str = cookies_str.replace(" ", "")
# cookies_str_list = cookies_str.split(";")
# for item in cookies_str_list:
#     split_str = item.split("=")
#     cookies_dict[split_str[0]] = split_str[1]

# print(cookies_dict)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Host": "e.waimai.meituan.com",
    "Referer": "https://e.waimai.meituan.com/v2/index?ignoreSetRouterProxy=true"
}

# res = requests.get(url, cookies=cookies_dict, headers=headers)

data_str = "optimus_uuid=f4597f79-0705-4263-b485-a5f1fcaf7f98&optimus_risk_level=71&optimus_code=10&optimus_partner=19"

data_dict = {}

for item in data_str.split("&"):
    split_list = item.split("=")
    data_dict[split_list[0]] = split_list[1]

res = requests.post(url, cookies=cookies_dict, headers=headers, data=data_dict)

print(res.text)


# json_data = json.loads(res.text)


# with open('stores.json','w+', encoding="utf-8") as f:
#     # ensure_ascii=False才能输入中文，否则是Unicode字符
#     # indent=2 JSON数据的缩进，美观
#     f.write(json.dumps(json_data, ensure_ascii=False))

# print(json_data)

# print(json_data["data"]["totalTurnover"])
# print(json_data["data"]["validOrderCount"])
