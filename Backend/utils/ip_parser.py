# utils/ip_parser.py
import requests
import json

def get_province_by_ip(ip: str):
    # 内网返回浙江省用于演示
    if ip in ["127.0.0.1", "localhost", "::1"] or ip.startswith("192.168.") or ip.startswith("10."):
        return "浙江"
    try:
        # 国内IP查询接口
        res = requests.get(f"https://whois.pconline.com.cn/ipJson.jsp?ip={ip}", timeout=5)
        text = res.text
        json_str = text.replace("callBack(", "").replace(");", "")
        data = json.loads(json_str)
        province = data.get("pro", "未知省份")
        return province
    except Exception as e:
        print(f"IP解析失败: {e}")
        return "未知省份"
