from flask import Flask, jsonify, request
from datetime import datetime
import sendgrid
import os
from sendgrid.helpers.mail import *

app = Flask(__name__)

patient_dictionary = dict()
# DICTIONARY IS STRUCTURED LIKE THIS:
# {
#   "patient_id": {
#               "AGE":age
#               "EMAIL":email
#               "Heart_rates": [HR1, HR2, HR3...]
#               "HR Times":[datetime1, datetime2 ...]
#               "HEART_RATE_AVERAGE_SINCE":[datetime]
#               }
#   "patient_id2": {
#               "AGE":age
#               "EMAIL":email
#               "Heart_rates": [HR1, HR2, HR3...]
#               "HR Times":[datetime1, datetime2 ...]
#               "HEART_RATE_AVERAGE_SINCE":[datetime]
#               }
# etc


def add_new_patient(patient, age, email):
    patient_dictionary[patient] = \
        {
            "AGE": age,
            "EMAIL": email,
            "HEART_RATES": [],
            "HR_TIMES": [],
            "HEART_RATE_AVERAGE_SINCE": []
        }
    return


@app.route("/api/new_patient", methods=["POST"])
def new_patient():
    r = request.get_json()
    print("Accepting new patient: ")
    print(r)
    add_new_patient(r["patient_id"], r["user_age"], r["attending_email"])
    return jsonify(patient_dictionary)


def add_heart_rate(patient, heart_rate):
    patient_dictionary[patient]["HEART_RATES"].append(heart_rate)
    return


def email(patient, heart_rate, age):
    if is_tac(heart_rate, age) == 'TACHYCARDIC':
        return  # **************************************I need email here


def add_timestamp(patient_id):
    time_stamp = datetime.now()
    patient_dictionary[patient_id]["HR_TIMES"].append(time_stamp)
    return


@app.route("/api/heart_rate", methods=["POST"])
def heart_rate():
    r = request.get_json()
    print("Adding heart rate to patient: {}".format(r["patient_id"]))
    print(r)
    add_heart_rate(r["patient_id"], r["heart_rate"])
    email(r["patient_id"], r["heart_rate"],
          patient_dictionary[r["patient_id"]]["AGE"])
    add_timestamp(r["patient_id"])
    return jsonify(patient_dictionary)


def age_based_tac(age):
    if age < 1:
        return 160
    elif (age < 3) & (age >= 1):
        return 151
    elif (age < 5) & (age >= 3):
        return 137
    elif (age < 8) & (age >= 5):
        return 133
    elif (age < 12) & (age >= 8):
        return 130
    elif (age < 15) & (age >= 12):
        return 119
    elif age >= 15:
        return 100


def is_tac(heart_rate, age):
    if heart_rate >= age_based_tac(age):
        return 'TACHYCARDIC'
    elif heart_rate < age_based_tac(age):
        return 'Not tachycardic'


@app.route("/api/status/<patient_id>", methods=["GET"])
def status(patient_id):
    # should return whether this patient is currently tachycardic based
    # on the previously available heart rate, and should also return
    # the timestamp of the most recent heart rate.
    print("Testing if patient is tachycardic...")
    output = is_tac(patient_dictionary[patient_id]["HEART_RATES"][-1],
                    patient_dictionary[patient_id]["AGE"])
    output = "Patient {} is ".format(patient_id) + output \
             + ". Time of last measurement: " \
             + str(patient_dictionary[patient_id]["HR_TIMES"][-1])
    return jsonify(output)


def all_heart_rates(patient):
    output = patient_dictionary[patient]["HEART_RATES"]
    return output


@app.route("/api/heart_rate/<patient_id>", methods=["GET"])
def prev_heart_rates(patient_id):
    # return all the previous heart rate measurements for that patient
    print("Output all heart rates for patient {}".format(patient_id))
    heart_rates = all_heart_rates(patient_id)
    output = "The heart rate measurements " \
             "for Patient {}: ".format(patient_id) + str(heart_rates)
    return jsonify(output)


def average(input_list):
    output = sum(input_list)/len(input_list)
    return round(output, 2)


@app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
def average_heart_rates(patient_id):
    # return the patients's average heart rate over all measurements
    print("Output average heart rate for patient {}".format(patient_id))
    heart_rates = all_heart_rates(patient_id)
    avg_heart_rate = average(heart_rates)
    output = "The average heart rate for Patient {} is ".format(patient_id) \
             + str(avg_heart_rate) + "bpm"
    return jsonify(output)


def add_time_interval(patient, time_interval):
    datetime_object_time_interval = \
        datetime.strptime(time_interval, '%Y-%m-%d %H:%M:%S.%f')
    patient_dictionary[patient]["HEART_RATE_AVERAGE_SINCE"]\
        = datetime_object_time_interval
    return datetime_object_time_interval


def hr_since_time(patient, date_time):
    list_count = 0
    for time in patient_dictionary[patient]["HR_TIMES"]:
        if date_time < time:
            list_count = list_count + 1
    list_of_hr = patient_dictionary[patient]["HEART_RATES"][-list_count:]
    return list_of_hr


@app.route("/api/heart_rate/interval_average", methods=["POST"])
def interval_average():
    r = request.get_json()
    print('Determining average heart rate after time interval:')
    print(r)
    # Heart_rate_average since the given time
    added_time = add_time_interval(r["patient_id"],
                                   r["heart_rate_average_since"])
    list_of_hr = hr_since_time(r["patient_id"], added_time)
    avg_interval_heart_rate = average(list_of_hr)
    output = "The average heart rate since {}".format(str(added_time)) \
             + " is {} bpm".format(avg_interval_heart_rate)
    return jsonify(output)


@app.route("/api/dictionary/", methods=["GET"])
def dictionary():
    return jsonify(patient_dictionary)


if __name__ == "__main__":
    app.run(host="127.0.0.1")
    # Deploy on VCM later and include the VCM address
