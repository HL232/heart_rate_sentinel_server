# Heart Rate Sentinel Server

Author: Howard Li

Version: 1.0.0

License: GNU General Public License v3.0

## Introduction
This repo is for the heart_rate_sentinel_server project. It is basically a remote server that takes heart rate measurements from hypothetical patients and records the data. It outputs if the patient becomes tachycardic or not and emails the doctor in charge of the patient. 

## What's included in this repo
 + `docs, Makefile, conf.py, index.rst, make.bat` - these files are used to produce auto generated sphinx documentation
 + `.gitignore` - files that Git should not upload to github
 + `.travis.yml` - Travis CI/CD setup
 + `README.md` - this file is the readme
 + `Test Code` - This is a text document that I used to store some test code. You can ignore this for grading purposes. I have it here in case I need it in the future again.
 + `example_client.py` - This is a premade example client python program. Run this program for a basic walkthrough of how my heart rate sentinel program works. This program is already pre-coded to reference the VCM running my server. It is a program that is BEST CASE SCENERIO.
 + `heart_rate_sentinel.py` - This python program is the actual setinel program that is running on my VCM. 
 + `requirements.txt` - Requirements for this program to set up your virtual environment
 + `test_heart_rate_sentinel.py` - This is the unit tests for the sentinel.
 
## How to run this project
 1. Cllone this repo or download the contents
 2. Run `example_client.py` - This is a premade client program. It will walk through the POST and GET commands and briefly explain what's happening in the background. It is already connected to my VCM server
 3. You can also hit my server with your own GET and POST commands. **My server is running at http://vcm-7254.vm.duke.edu:5000/ BLAH BLAH BLAH**
 4. If anything in the server breaks, and you don't want to email me to restart the server, you can also run the program locally. Go into the `heart_rate_sentinel.py` program and go to the last line. Uncomment the `app.run(host="127.0.0.1")` line and run the sentinel locally instead of using the 0.0.0.0 host. 
 5. My server should handle all the POST and GET requests that are described in the original assignment below. 

## Other Notes and Future Works
 + This sentinel server is not running on a MongoDB database. It is using a locally created dictionary to store patient information. Therefore, every time you restart `heart_rate_sentinel.py`, the dictionary resets. 
 + There is an extra GET route. I added `GET /api/dictionary/` This allows you to see the dictionary database of all the patients. I used this for development purposes but decided it might be useful for debugging so I left it in. That's a major privacy concern if this was a real server though cause anyone would be able to see all patient data...
 + POST input validation is poorly handled. Right now I am only throwing and catching random exceptions and then returning error messages to the client. This was to prevent errors from crashing the server. Only a few validation cases are handled:
   - POST /api/new_patient validations:
     1. That patient_id, user_age, and attending_email are present
     2. The values are string, int, string respectively
     3. That the email has a @ symbol in it. 
   - POST /api/heart_rate validations:
     1. That patient_id, heart_rate_ are present
     2. That heart_rate is an integer
     3. That the patient_id exists in the database
   - POST /api/heart_rate/interval_average validations:
     1. That patient_id, interval_average are present
     2. That the patient exists in the database
     3. The time input is correctly formatted
   - **There is a strong likelihood that errors outside of these validations will not work, and worst case crash the server**
 + My first Sendgrid account was suspended because I exposed the API on Github. I made a second account, hopefully that one doesn't get suspended. `example_client.py` is hardcoded to send emails to my personal email, but this program *should* be able to send emails to the "doctor's email" whenever you POST a new patient with new info.
 + Travis currently shows up as failing. But this is because I have the `sendgrid_api_key` file locally for the server only, not on Github. Otherwise all the unit tests should pass if you run `pytest -v` command in Anaconda or your terminal.
 
 
 

# Original Assignment

This assignment will have you build a simple centralized heart rate sentinel server. This server will be built to receive POST requests from mock patient heart rate monitors that contain patient heart rate information over time. If a patient exhibits a tachycardic heart rate, the physician should receive an email warning them. So if a new heart rate is received for a patient that is tachycardic, the email should be sent out at that time. This calculation should be based on age (more info [here](https://en.wikipedia.org/wiki/Tachycardia)). This can be sent using the free [Sendgrid API](https://sendgrid.com/) (there is also a [Sendgrid python package](https://github.com/sendgrid/sendgrid-python) that wraps the API).

Name your repository: `heart_rate_sentinel_server`. Note: for this assignment, you do not have to use a database. You can choose to store patient information using in memory data structures like python lists and dictionaries. 

Your Flask web service should implement the following API routes:

* `POST /api/new_patient` with
  ```sh
  {
      "patient_id": "1", # usually this would be the patient MRN
      "attending_email": "suyash.kumar@duke.edu", 
      "user_age": 50, # in years
  }
  ```
  This will be called when the heart rate monitor is checked out to be attached to a particular patient, the system emits this event to register the patient with your heart rate server. This will allow you to initialize a patient, and accecpt future heart rate measurements for this patient. 
* `POST /api/heart_rate` with
  ```sh
  {
      "patient_id": "1", # usually this would be the patient MRN
      "heart_rate": 100
  }
  ```
  which should store this heart rate measurement for the user with that email. Be sure to include the [current time stamp](https://stackoverflow.com/questions/415511/how-to-get-current-time-in-python) in your database or your program cache.
* `GET /api/status/<patient_id>` should return whether this patient is currently tachycardic based on the previously available heart rate, and should also return the timestamp of the most recent heart rate. 
* `GET /api/heart_rate/<patient_id>` should return all the previous heart rate measurements for that patient
* `GET /api/heart_rate/average/<patient_id>` should return the patients's average heart rate over all measurements you have stored for this user. 
* `POST /api/heart_rate/interval_average` with 
  ```
  {
      "patient_id": "1",
      "heart_rate_average_since": "2018-03-09 11:00:36.372339" // date string
  }
  ```
  
For this assignment, be sure to write modular code. This means your handler functions for routes should be calling other independent functions in different modules as frequently as possible. All of those other independant functions should be tested. You should also remember to validate user inputs that come from (`request.get_json()`) to ensure the right fields exist in the data and that they are the right type. You can write independant, testable `validate_heart_rate_request(r)` functions. You do not have to test the flask handler functions directly (the functions associated with the `@app.route` decorator), but all other functions should be tested.  

## Submission Notes
- __As always in this class, be sure to follow all best practice conventions (unit testing, git practices, Travis CI, testing, PEP8, docstrings, etc)__
- Please git tag the final version of your repository as done previously in this class
- Ensure your repository is called `heart_rate_sentinel_server`
- __The SendGrid part of this assignment will not be worth the majority of points, so focus on that part after the rest of the functionality has been completed.__
- Please deploy this on your VCM and submit the hostname and port that your server is running on to the Sakai assignment posting (`vcm-1000.vm.duke.edu:5000`). Remember to follow the emailed instructions about ensuring your server does not restart (there is a check box on the vcm control panel. It will ask you for a reason, just say you are running a web server assignment for BME590 Medical Software Design). __Please do this deployment step last, it is most important to complete the rest of the assignment first (that is where most of the points are)__.

## More information about SendGrid
You need to create a free account at [sendgrid.com](https://sendgrid.com) and then [create an API key](https://sendgrid.com/docs/ui/account-and-settings/api-keys/#creating-an-api-key) which is a key that authenticates you to use the SendGrid API. Note that SendGrid has a nice [python API](https://github.com/sendgrid/sendgrid-python) that you can install using pip. In the [example code shown there](https://github.com/sendgrid/sendgrid-python#quick-start), you need to set the `SENDGRID_API_KEY` environment variable to your API key you created earlier. Try not to commit your key to github as that will expose it for others to use. 

### Special note for Mac users
:eyes: Apparently python 3.6 for Mac does not come configured to use the standard root certificate authorities, so some folks may get a ssl error when using the SendGrid client. To fix this, run the following command:

```sh
/Applications/Python\ 3.6/Install\ Certificates.command
```

If you installed Python 3.7, change 3.6 to 3.7 in the command above.

If you're getting an error like this in conda, try 
```sh
conda remove certifi
conda install certifi
```
