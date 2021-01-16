import requests
r = requests.get('https://www.python.org')
r.status_code
print(r.text)