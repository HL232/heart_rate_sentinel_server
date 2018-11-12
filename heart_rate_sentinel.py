from flask import Flask, jsonify, request
app = Flask(__name__)


patient_dictionary = dict()
# DICTIONARY IS STRUCTURED LIKE THIS:
# {
#   "patient_id": ["EMAIL", AGE, HR1, HR2, HR3...],
#   "patient_id2": ["EMAIL", AGE, HR1, HR2, HR3...],
# etc


@app.route("/api/new_patient", methods=["POST"])
def new_patient():
    r = request.get_json()
    print(r)
    patient_dictionary[r["patient_id"]] = [r["attending_email"], r["user_age"]]
    return jsonify(patient_dictionary)


@app.route("/api/heart_rate", methods=["POST"])
def heart_rate():
    r = request.get_json()
    print(r)
    patient_dictionary[r["patient_id"]].append(r["heart_rate"])
    # CURRENT TIME STAMP **************************************************************************
    return jsonify(patient_dictionary)


@app.route("/api/status/<patient_id>", methods=["GET"])
def status(patient_id):
    # should return whether this patient is currently tachycardic based
    # on the previously available heart rate, and should also return
    # the timestamp of the most recent heart rate.
    return


@app.route("/api/heart_rate/<patient_id>", methods=["GET"])
def prev_heart_rates(patient_id):
    # return all the previous heart rate measurements for that patient
    output = patient_dictionary[patient_id][2:]
    return jsonify(output)


@app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
def average_heart_rates(patient_id):
    # return the patients's average heart rate over all measurements you have stored for this user.
    return


@app.route("/api/heart_rate/interval_average", methods=["POST"])
def interval_average():
    # return jsonify(output)
    # input is something like:
    # r = requests.post("http://127.0.0.1:5000/api/new_patient",
    # json = {
    # "patient_id": "1",
    # "heart_rate_average_since": "2018-03-09 11:00:36.372339"  # date string
    # })
    r = request.get_json()
    print(r)
    # Heart_rate_average since the given time
    return jsonify(r)


if __name__ == "__main__":
    app.run(host="127.0.0.1")
'''
test code:
import requests
r = requests.post("http://127.0.0.1:5000/api/new_patient", json={"patient_id":"one","attending_email":"blah","user_age":10})
r.text
r = requests.post("http://127.0.0.1:5000/api/new_patient", json={"patient_id":"two","attending_email":"BLAH","user_age":20})
r.text
r = requests.post("http://127.0.0.1:5000/api/heart_rate", json = {"patient_id":"two","heart_rate":100})
r.text
r = requests.post("http://127.0.0.1:5000/api/heart_rate", json = {"patient_id":"two","heart_rate":200})
r.text
R = requests.get("http://127.0.0.1:5000/api/heart_rate/two")
R.text
'''