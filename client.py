import requests
import os
BASE = "http://127.0.0.1:5000/"
response = requests.get(BASE+"helloworld")
print(response.json())

def create_file_list(dir_name):
    list_files = []
    for root, dirs, files in os.walk('./static/'+dir_name+'/',topdown=False):
        for name in files:
            list_files.append(os.path.join(root, name))
    return list_files

listb = create_file_list("face");
for file in listb:
    print(file)