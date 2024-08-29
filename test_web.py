import requests
data = {'name': 'John Doe', 'age': '30'}
response = requests.post('http://127.0.0.1:5000/', data=data)
print(response.text)