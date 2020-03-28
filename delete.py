import json

dic = {}
#Reset the data recorded
for i in range(8,25):
    dic[i] = {"total":0,"count":0}

print(dic)

with open('data.json', 'w') as f:
    json.dump(dic, f)
