import requests

users = {'fstadmin@localhost': {'password': 'P@ssw0rdJames'}}  
params = dict(
    action="view",
    user='fstadmin@localhost',
    password='P@ssw0rdJames'
)

# Test basic Function
s = requests.Session()
respones0 = s.get('http://127.0.0.1:5000/', params=params)
respones01 = s.get('http://127.0.0.1:5000/help', params=params)
respones1 = s.get('http://127.0.0.1:5000/login', params=params)
respones2 = s.get('http://127.0.0.1:5000/view')
print(respones0, respones0.text)
print(respones01, respones01.text)
print(respones1, respones1.text)
print(respones2, respones2.text)

print("-----------------")
data = dict(
    user='fstadmin',
    password='P@ssw0rdJames'
)
data = dict(
    user='fstuser1',
    password='P@ssw0rdJames'
)
# Test signup function
s2 = requests.Session()
# response0 = s2.post('http://127.0.0.1:5000/signup', json=data)
# print(response0, response0.text)
response1 = s2.get('http://127.0.0.1:5000/login', json=data)
print(response1, response1.text)
## After signup New Login procedure
