from flask import Flask, jsonify, request
from datetime import datetime, timedelta
app = Flask(__name__)


patient_dictionary = dict()
# DICTIONARY IS STRUCTURED LIKE THIS:
# {
#   "patient_id": {
#               "AGE":age
#               "EMAIL":email
#               "Heart_rates": [HR1, HR2, HR3...]
#               "HR Times":[datetime1, datetime2 ...]
#               }
#   "patient_id2": {
#               "AGE":age
#               "EMAIL":email
#               "Heart_rates": [HR1, HR2, HR3...]
#               "HR Times":[datetime1, datetime2 ...]
#               }
# etc


@app.route("/api/new_patient", methods=["POST"])
def new_patient():
    r = request.get_json()
    print("Accepting new patient: ")
    print(r)
    patient_dictionary[r["patient_id"]] = \
        {
            "AGE": r["user_age"],
            "EMAIL": r["attending_email"],
            "HEART_RATES": [],
            "HR_TIMES": []
        }
    return jsonify(patient_dictionary)


@app.route("/api/heart_rate", methods=["POST"])
def heart_rate():
    r = request.get_json()
    print("Adding heart rate to patient: {}".format(r["patient_id"]))
    print(r)
    patient_dictionary[r["patient_id"]]["HEART_RATES"].append(r["heart_rate"])
    time_stamp = datetime.now()
    patient_dictionary[r["patient_id"]]["HR_TIMES"].append(time_stamp)
    return jsonify(patient_dictionary)


def determine_patient_type(age):
    if age <= 2:
        return "infant"
    if age <= 15 & age > 2:
        return "child"
    if age > 15:
        return "adult"


def is_tac_infant(hr):
    if hr >= 179:
        return 'TACHYCARDIC'
    elif hr < 179:
        return 'Not tachycardic'


def is_tac_child(hr):
    if hr >= 119:
        return 'TACHYCARDIC'
    elif hr < 119:
        return 'Not tachycardic'


def is_tac_adult(hr):
    if hr >= 100:
        return 'TACHYCARDIC'
    elif hr < 100:
        return 'Not tachycardic'


@app.route("/api/status/<patient_id>", methods=["GET"])
def status(patient_id):
    # should return whether this patient is currently tachycardic based
    # on the previously available heart rate, and should also return
    # the timestamp of the most recent heart rate.
    # CURRENT TIME STAMP *********************************************
    print("Testing if patient is tachycardic...")
    patient_type = determine_patient_type(patient_dictionary[patient_id]["AGE"])
    if patient_type == "infant":
        output = is_tac_infant(patient_dictionary[patient_id]["HEART_RATES"][-1])
    elif patient_type == "child":
        output = is_tac_child(patient_dictionary[patient_id]["HEART_RATES"][-1])
    elif patient_type == "adult":
        output = is_tac_adult(patient_dictionary[patient_id]["HEART_RATES"][-1])
    output = output + ". Time of last measurement: " \
                    + str(patient_dictionary[patient_id]["HR_TIMES"][-1])
    return jsonify(output)


def all_heart_rates(patient_id):
    output = patient_dictionary[patient_id]["HEART_RATES"]
    return output


@app.route("/api/heart_rate/<patient_id>", methods=["GET"])
def prev_heart_rates(patient_id):
    # return all the previous heart rate measurements for that patient
    print("Output all heart rates for patient {}".format(patient_id))
    heart_rates = all_heart_rates(patient_id)
    return jsonify(heart_rates)


def average(input_list):
    output = sum(input_list)/len(input_list)
    return output


@app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
def average_heart_rates(patient_id):
    # return the patients's average heart rate over all measurements
    print("Output average heart rate for patient {}".format(patient_id))
    heart_rates = all_heart_rates(patient_id)
    avg_heart_rate = round(average(heart_rates), 2)
    return jsonify(avg_heart_rate)


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
