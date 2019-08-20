import pytest
import request
import json

url = "https://staging.autographamt.com/signup"

file = open ('//home//kavitha//Documents//API codes//AGMT//userd.json','r')
json_input = file.read()
request_json = json.loads(json_input)

response = request.post(url,request_json)
print(resnse.content)

assert response_status_code == 201