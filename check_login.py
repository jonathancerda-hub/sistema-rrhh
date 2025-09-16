import urllib.request

try:
    with urllib.request.urlopen('http://127.0.0.1:8000/login/', timeout=5) as r:
        status = r.getcode()
        body = r.read().decode('utf-8', errors='ignore')
        print('status', status)
        print(body[:400])
except Exception as e:
    print('ERROR', e)
