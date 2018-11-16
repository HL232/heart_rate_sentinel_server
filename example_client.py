# test code:

import requests

print("Hi, this is a example of how my sentinel server works.")
input("PRESS ENTER TO CONTINUE.")

print("First I am adding Patient 1 and Patient 2 using POST/api/new_patient")
input("PRESS ENTER TO CONTINUE.")
r = requests.post("http://127.0.0.1:5000/api/new_patient",
                  json={"patient_id": "1",
                        "attending_email": "blah",
                        "user_age": 30})
r = requests.post("http://127.0.0.1:5000/api/new_patient",
                  json={"patient_id": "2",
                        "attending_email": "BLAH",
                        "user_age": 20})

print("Done. I use the BLAH.text command to see them")
input("PRESS ENTER TO CONTINUE.")
print(r.text)

print("Next I add 1 heart beat to Patient 1, and 2 to Patient 2."
      "This is done with POST /api/heart_rate")
input("PRESS ENTER TO CONTINUE.")
r = requests.post("http://127.0.0.1:5000/api/heart_rate",
                  json={"patient_id": "1", "heart_rate": 75})
r = requests.post("http://127.0.0.1:5000/api/heart_rate",
                  json={"patient_id": "2", "heart_rate": 80})
r = requests.post("http://127.0.0.1:5000/api/heart_rate",
                  json={"patient_id": "2", "heart_rate": 150})

print("Done. I use the BLAH.text command to see the updates")
input("PRESS ENTER TO CONTINUE.")
print(r.text)

print("I used the GET/api/heart_rate/<patient_id> to see the "
      "heart beats of patient 2")
input("PRESS ENTER TO CONTINUE.")
HR = requests.get("http://127.0.0.1:5000/api/heart_rate/2")
print(HR.text)

print("I used the GET/api/heart_rate/average/<patient_id> to see the "
      "average heart beat of patient 2")
input("PRESS ENTER TO CONTINUE.")
avg = requests.get("http://127.0.0.1:5000/api/heart_rate/average/2")
print(avg.text)

print("I used the GET/api/status/<patient_id> to see that patient 1 "
      "is not tachycardic")
input("PRESS ENTER TO CONTINUE.")
not_tac = requests.get("http://127.0.0.1:5000/api/status/1")
print(not_tac.text)

print("I used the GET/api/status/<patient_id> to see that patient 2 "
      "is tachycardic")
input("PRESS ENTER TO CONTINUE.")
tac = requests.get("http://127.0.0.1:5000/api/status/2")
print(tac.text)

print("I used the POST/api/heart_rate/interval_average to see the "
      "average heart rates for patient 2 \nsince wednesday 11/14/2018 "
      "So basically all the newly added heart rates")
input("PRESS ENTER TO CONTINUE.")
int_avg = requests.post("http://127.0.0.1:5000/api/"
                        "heart_rate/interval_average",
                        json={"patient_id": "2",
                              "heart_rate_average_since":
                                  "2018-11-14 13:07:39.569444"})
print(int_avg.text)

print("That's all the basic functions. Feel free to break it with whatever "
      "other requests you have \nfor the server. Be gentle, it breaks easy...")
