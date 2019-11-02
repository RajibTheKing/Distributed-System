import requests

print('\n\nGet Request: http://localhost:8080/')
response = requests.get('http://localhost:8080')
print('Response: ' + response.text)

print('\n\nGet Request: http://localhost:8080/hello')
response = requests.get('http://localhost:8080/hello')
print('Response: ' + response.text)


print('\n\nPost Request: http://localhost:8080/input with parameters')
response = requests.post('http://localhost:8080/input', json={"username": "RajibTheKing", "password": "2384kaOIAlf&%*&^%"})
print('Response: ' + response.text)