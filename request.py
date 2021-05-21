import requests

users = {'fstadmin@localhost': {'password': 'P@ssw0rdJames'}}  
print(requests.get('http://127.0.0.1:5000/login', auth=('fstadmin@localhost','P@ssw0rdJames')).text)