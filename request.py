import requests
from random import seed
from random import random,randint


users = {'fstadmin@localhost': {'password': 'P@ssw0rdJames'}}  
data = dict(
    user='fstadmin',
    password='P@ssw0rdJames'
)

# Test basic Function
s = requests.Session()
respones0 = s.get('http://127.0.0.1:5000/', json=data)
respones01 = s.get('http://127.0.0.1:5000/help', json=data)
response1 = s.get('http://127.0.0.1:5000/login', json=data)
respones2 = s.get('http://127.0.0.1:5000/userHome/view', json=data)
print(respones0, respones0.text)
print(respones01, respones01.text)
print(response1, response1.text)
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
data = dict(
    user='fstuser2',
    password='P@ssw0rdJames'
)

# Test signup function
print("----------Session 2 ------------")

s2 = requests.Session()
# response0 = s2.post('http://127.0.0.1:5000/signup', json=data)
# print(response0, response0.text)
response1 = s2.get('http://127.0.0.1:5000/login', json=data)
print(response1, response1.text)
data = dict(
    user='fstuser2',
    password='P@ssw0rdJames'
)
## Test Buy opeation
cardType = ["pikachu", "bulbasaur", "charmander","squirtle"]
data = {
    "cardType":cardType[0],
    "num":randint(1, 5),
    '$perCard':randint(5, 20)
}
print(data)
response2 = s2.get('http://127.0.0.1:5000/userHome/buy', json=data)
print(response2, response2.text)

print("----------Session 3 ------------")
## New session for a seller

s3 = requests.Session()
data = dict(
    user='fstuser1',
    password='P@ssw0rdJames'
)
response1 = s3.get('http://127.0.0.1:5000/login', json=data)
print(response1, response1.text)
data = {
    "cardType":cardType[0],
    "num":randint(6, 10),
    '$perCard':randint(5, 20)
}
print(data)
response2 = s3.get('http://127.0.0.1:5000/userHome/sell', json=data)
print(response2, response2.text)
## After signup New Login procedure
