import pytest
from heart_rate_sentinel import *


def test_add_new_patient():
    add_new_patient('A', 10, 'blah')
    expected = {"AGE": 10,
                "EMAIL": 'blah',
                "HEART_RATES": [],
                "HR_TIMES": [],
                "HEART_RATE_AVERAGE_SINCE": []
                }
    assert patient_dictionary['A'] == expected


def test_add_heart_rate():
    add_new_patient('A', 10, 'blah')
    add_heart_rate('A', 100)
    assert patient_dictionary['A']['HEART_RATES'] == [100]


def test_add_timestamp():
    add_new_patient('A', 10, 'blah')
    add_timestamp('A')
    assert patient_dictionary['A']["HR_TIMES"] != []


@pytest.mark.parametrize("age, expected", [
    (0.5, 160),
    (2, 151),
    (3.5, 137),
    (7, 133),
    (11.9, 130),
    (14, 119),
    (15, 100),
    (28, 100)
])
def test_age_based_tac(age, expected):
    a = age_based_tac(age)
    b = expected
    assert a == b


@pytest.mark.parametrize("heart_rate, age, expected", [
    (100, 30, "TACHYCARDIC"),
    (75, 30, "Not tachycardic"),
    (135, 8, "TACHYCARDIC"),
    (100, 8, "Not tachycardic")
])
def test_is_tac(heart_rate, age, expected):
    a = is_tac(heart_rate, age)
    b = expected
    assert a == b


def test_all_heart_rates():
    add_new_patient('A', 10, 'blah')
    add_heart_rate('A', 5)
    add_heart_rate('A', 10)
    a = all_heart_rates('A')
    assert a == [5, 10]


def test_average():
    a = average([1,2,4])
    b = 2.33
    assert a == b


def test_add_time_interval():
    add_new_patient('A', 10, 'blah')
    a = add_time_interval('A', "2018-11-14 13:07:39.569444")
    b = datetime.strptime("2018-11-14 13:07:39.569444", '%Y-%m-%d %H:%M:%S.%f')
    assert a == b


def test_hr_since_time():
    add_new_patient('A', 10, 'blah')
    add_heart_rate('A', 5)
    add_heart_rate('A', 10)
    time = datetime.strptime("2018-11-14 13:07:39.569444", '%Y-%m-%d %H:%M:%S.%f')
    a = hr_since_time('A',time)
    b = [5,10]
    assert a == b
