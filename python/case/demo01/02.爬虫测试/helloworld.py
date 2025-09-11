import requests

resp = requests.get("http://app.nifdc.org.cn/jianybz/jybzTwoGj.do?formAction=listBcjy")


print(resp.status_code)
print(resp.text)



