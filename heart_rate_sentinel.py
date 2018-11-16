from flask import Flask, jsonify, request
from datetime import datetime
import sendgrid
import os
from sendgrid_api_key import SENDGRID_API_KEY
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

# ***************************************************************************
# ****POST NEW PATIENT ******************************************************
# ***************************************************************************


def add_new_patient(patient, age, email):
    """Adds a new patient to the dictionary of patients

    Args:
        patient: (string) ID of patient
        age: (int) age of patient
        email: (string) doctor's email

    Returns:
        Returns None
    """
    patient_dictionary[patient] = \
        {
            "AGE": age,
            "EMAIL": email,
            "HEART_RATES": [],
            "HR_TIMES": [],
            "HEART_RATE_AVERAGE_SINCE": []
        }
    return


def validate_new_patient(r):
    """Validates that the client POSTed the correct request for new patient
    Tests
    1. That patient_id, user_age, and attending_email are present
    2. The values are string, int, string respectively
    3. That the email is kinda valid
    Raises errors for any issues. These errors are caught by the server

     Args:
        r: The POST request JSON

     Returns:
         Returns None
     """
    # r["patient_id"] needs to be a string
    # r["user_age"] needs to be an int
    # r["attending_email"] needs to be a string
    if not (bool(r.get('patient_id'))
            & bool(r.get('user_age'))
            & bool(r.get('attending_email'))):
        raise TypeError
    if (not isinstance(r["patient_id"], str)) \
            or (not isinstance(r["user_age"], int)) \
            or (not isinstance(r["attending_email"], str)):
        raise ValueError
    if '@' not in r["attending_email"]:
        raise NameError
    return


@app.route("/api/new_patient", methods=["POST"])
def new_patient():
    """POST method: Accepts new patients to the server

    Args:
        {
        "patient_id": "1", # usually this would be the patient MRN
        "attending_email": "EMAIL",
        "user_age": 50, # in years
        }

    Returns:
        Returns updated JSON file of dictionary of all current patients
    """
    r = request.get_json()
    try:
        validate_new_patient(r)
    except TypeError:
        return jsonify('POST missing patient id, age, or email')
    except ValueError:
        return jsonify('Patient ID needs to be a string, user_age needs '
                       'to be an integer, email needs to be a string')
    except NameError:
        return jsonify('Email needs to be someone@something')
    print("Accepting new patient: ")
    print(r)
    add_new_patient(r["patient_id"], r["user_age"], r["attending_email"])
    return jsonify(patient_dictionary)


# ***************************************************************************
# ****POST NEW HEART RATE****************************************************
# ***************************************************************************


def add_heart_rate(patient, heart_rate):
    """Adds a new heart rate measurement for a patient

    Args:
        patient: (string) ID of patient to add to
        heart_rate: (int) Heart rate to be added

    Returns:
        Returns None
    """
    patient_dictionary[patient]["HEART_RATES"].append(heart_rate)
    return


def email(patient, heart_rate, age):
    """Emails the doctor if the patient is tachycardic
    The email is sent to the email provided in the patient database
    The subject line tells the doctor which patient is tachycardic

    Args:
        patient: (string) ID of patient
        heart_rate: (int) newest heart rate measurement
        age: (int) age of the patient

    Returns:
        Returns None
    """
    if is_tac(heart_rate, age) == 'TACHYCARDIC':
        sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
        from_email = Email("howards_sentinel_server@donotreply.com")
        doctor_email = patient_dictionary[patient]["EMAIL"]
        to_email = Email(doctor_email)
        subject = "Patient {} is Tachycardic!".format(patient)
        content = Content("text/plain", "Go save your patient")
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)


def add_timestamp(patient_id):
    """Adds a time stamp when a heart beat is added

    Args:
        patient_id: (string) ID of patient

    Returns:
        Returns None
    """
    time_stamp = datetime.now()
    patient_dictionary[patient_id]["HR_TIMES"].append(time_stamp)
    return


def validate_heart_rate(r):
    """Validates that the client POSTed the correct request
    Tests
    1. That patient_id, heart_rate_ are present
    2. That heart_rate is an integer
    3. That the patient_id exists in the database
    Raises errors for any issues. These errors are caught by the server

     Args:
        r: The POST request JSON

     Returns:
         Returns None
     """
    if not (bool(r.get('patient_id')) & bool(r.get('heart_rate'))):
        raise TypeError
    if not isinstance(r["heart_rate"], int):
        raise ValueError
    if patient_dictionary.get(r['patient_id']) is None:
        raise KeyError
    return


@app.route("/api/heart_rate", methods=["POST"])
def heart_rate():
    """POST method: Accepts a new heart rate measurement

     Args:
        {
            "patient_id": "1", # usually this would be the patient MRN
            "heart_rate": 100
        }

     Returns:
         Returns updated JSON file of dictionary of all current patients
         Unless an error is detected, in which case the appropriate message
          is returned
     """
    r = request.get_json()
    try:
        validate_heart_rate(r)
    except TypeError:
        return jsonify('POST missing patient id or heart_rate')
    except ValueError:
        return jsonify('Posted heart_rate must be an integer')
    except KeyError:
        return jsonify('Patient not found. Please add new patient')
    print("Adding heart rate to patient: {}".format(r["patient_id"]))
    print(r)
    add_heart_rate(r["patient_id"], r["heart_rate"])
    email(r["patient_id"], r["heart_rate"],
          patient_dictionary[r["patient_id"]]["AGE"])
    add_timestamp(r["patient_id"])
    return jsonify(patient_dictionary)


# ***************************************************************************
# ****GET PATIENT STATUS*****************************************************
# ***************************************************************************


def age_based_tac(age):
    """Switch statement of which heart rates count as tachycardic

    Args:
        age: (int) age of patient

    Returns:
        Returns the heart rate considered tachycardic for that age
    """
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
    """Determines if patient is tachycardic based on age and heart rate

    Args:
        heart_rate: (int) patient's current heart rate
        age: (int) age of patient

    Returns:
        Returns 'TACHYCARDIC' or 'not tachycardic'
    """
    if heart_rate >= age_based_tac(age):
        return 'TACHYCARDIC'
    elif heart_rate < age_based_tac(age):
        return 'not tachycardic'


@app.route("/api/status/<patient_id>", methods=["GET"])
def status(patient_id):
    """GET method: Tells client what the status of patient is

     Args:
        patient_id: ID of the patient

     Returns:
         Returns statement of if the patient is tachycardic, and heart rate
     """
    print("Testing if patient is tachycardic...")
    output = is_tac(patient_dictionary[patient_id]["HEART_RATES"][-1],
                    patient_dictionary[patient_id]["AGE"])
    output = "Patient {} is ".format(patient_id) + output \
             + ". Time of last measurement: " \
             + str(patient_dictionary[patient_id]["HR_TIMES"][-1])
    return jsonify(output)


# ***************************************************************************
# ****GET PATIENT HRs ******************************************************
# ***************************************************************************


def all_heart_rates(patient):
    """Reports a list of the patient's recorded heart rates

     Args:
        patient: ID of the patient

     Returns:
         Returns list of patient heart rates
     """
    output = patient_dictionary[patient]["HEART_RATES"]
    return output


@app.route("/api/heart_rate/<patient_id>", methods=["GET"])
def prev_heart_rates(patient_id):
    """GET method: return all the heart rate measurements of patient to client

     Args:
        patient_id: ID of the patient

     Returns:
         Returns statement of all past heart rate measurements
     """
    print("Output all heart rates for patient {}".format(patient_id))
    heart_rates = all_heart_rates(patient_id)
    output = "The heart rate measurements " \
             "for Patient {}: ".format(patient_id) + str(heart_rates)
    return jsonify(output)


# ***************************************************************************
# ****GET HR AVG ************************************************************
# ***************************************************************************


def average(input_list):
    """Average of the list

     Args:
        input_list: a list of heart rates
     Returns:
         Returns average heart rate of the list rounded to 2 decimals
     """
    output = sum(input_list)/len(input_list)
    return round(output, 2)


@app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
def average_heart_rates(patient_id):
    """GET method: Tells client the patient's avg heart rate

     Args:
        patient_id: ID of the patient

     Returns:
         Returns statement of the patient's average heart rate
         Unless an error is detected, in which case the appropriate message
          is returned
     """
    print("Output average heart rate for patient {}".format(patient_id))
    heart_rates = all_heart_rates(patient_id)
    avg_heart_rate = average(heart_rates)
    output = "The average heart rate for Patient {} is ".format(patient_id) \
             + str(avg_heart_rate) + "bpm"
    return jsonify(output)


# ***************************************************************************
# ****POST INTERVAL HR AVG***************************************************
# ***************************************************************************


def add_time_interval(patient, time_interval):
    """Adds a time interval to the patient's dictionary

     Args:
        patient: the patient's ID
        time_interval: the time to record

     Returns:
         Returns datetime object of the time
     """
    datetime_object_time_interval = \
        datetime.strptime(time_interval, '%Y-%m-%d %H:%M:%S.%f')
    patient_dictionary[patient]["HEART_RATE_AVERAGE_SINCE"]\
        = datetime_object_time_interval
    return datetime_object_time_interval


def hr_since_time(patient, date_time):
    """Average heart rate since the time interval

     Args:
        patient: the patient's ID
        date_time: the datetime object

     Returns:
         Returns list of heart rates since the date_time
     """
    list_count = 0
    for time in patient_dictionary[patient]["HR_TIMES"]:
        if date_time < time:
            list_count = list_count + 1
    list_of_hr = patient_dictionary[patient]["HEART_RATES"][-list_count:]
    return list_of_hr


def validate_interval_average(r):
    """Validates that the client POSTed the correct interval avg request
     Tests
     1. That patient_id, interval_average are present
     2. That the patient exists in the database
     Raises errors for any issues. These errors are caught by the server

      Args:
         r: The POST request JSON

      Returns:
          Returns None
      """
    if not (bool(r.get('patient_id'))
            & bool(r.get('heart_rate_average_since'))):
        raise TypeError
    if patient_dictionary.get(r['patient_id']) is None:
        raise KeyError
    return


@app.route("/api/heart_rate/interval_average", methods=["POST"])
def interval_average():
    """POST method: Tells client the patient's avg heart rate on an interval

      Args:
        {
            "patient_id": "1",
            "heart_rate_average_since": "2018-03-09 11:00:36.372339" // date
        }
      Returns:
          Returns statement of the patient's average heart rate on interval
          Unless an error is detected, in which case the appropriate message
          is returned
      """
    r = request.get_json()
    try:
        validate_interval_average(r)
    except TypeError:
        return jsonify('POST missing patient id or heart_rate_interval_average')
    except KeyError:
        return jsonify('Patient not found. Please add new patient')
    print('Determining average heart rate after time interval:')
    print(r)
    # Heart_rate_average since the given time
    try:
        added_time = add_time_interval(r["patient_id"],
                                       r["heart_rate_average_since"])
    except ValueError:
        return jsonify('Time interval format incorrect. Should be something like '
                       '2018-03-09 11:00:36.372339')
    list_of_hr = hr_since_time(r["patient_id"], added_time)
    avg_interval_heart_rate = average(list_of_hr)
    output = "The average heart rate since {}".format(str(added_time)) \
             + " is {} bpm".format(avg_interval_heart_rate)
    return jsonify(output)


# ***************************************************************************
# ****SEE THE DICTIONARY*****************************************************
# ***************************************************************************


@app.route("/api/dictionary/", methods=["GET"])
def dictionary():
    """GET method: Used to see the list of all current patients
     """
    return jsonify(patient_dictionary)


if __name__ == "__main__":
    app.run(host="127.0.0.1")
    # Deploy on VCM later and include the VCM address
