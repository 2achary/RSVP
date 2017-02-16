import shelve
import os
import json
from app import app
import pytest
# -------------------------------------------------------------------------
# Variables
# -------------------------------------------------------------------------

invalid_args_list = [
    '?firstName=Sonny',
    '?lastName=Hanback',
    '?firstName',
    ''
]
insert_guest_success = b"Successfully added guest"
insert_guest_fail = b"First and last name required"
sonny = '?firstName=Sonny&lastName=Hanback'
sonny_d = {"firstName": "Sonny", "lastName": "Hanback"}
guest = '/guest'
shelf_name = os.path.join('guest_list.shelf')
guest_list_key = 'guest_list'

# -------------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------------


def load_n_decode(b):
    return json.loads(b.decode('utf-8'))

# -------------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------------


@pytest.fixture
def insert_guest(app_tc):
    """Insert guest and return the function to insert the guest again"""
    def inner(guest_arg_string):
        app_tc.post(guest + guest_arg_string)
    inner(sonny)
    return inner


@pytest.fixture(params=invalid_args_list)
def invalid_arg(request):
    return request.param


@pytest.fixture
def app_tc():
    app.config['TESTING'] = True
    return app.test_client()


@pytest.fixture(scope='function')
def clean_db():
    def clean():
        with shelve.open(shelf_name) as shelf:
            shelf[guest_list_key] = []

    # Run clean() before and after each test
    clean()
    yield
    clean()


# -------------------------------------------------------------------------
# Insert Guest Tests
# -------------------------------------------------------------------------

def test_insert_guest(app_tc, clean_db):

    # Post to the guest endpoint with valid args
    response = app_tc.post(guest + sonny)

    # Assert that we got correct response and status code
    assert response.status_code == 201
    assert insert_guest_success in response.data

    # Let's make sure what we inserted is actually still there
    response = app_tc.get(guest)
    assert sonny_d in load_n_decode(response.data)

    
def test_insert_guest_406_if_invalid_args(invalid_arg, clean_db, app_tc):
    response = app_tc.post(guest + invalid_arg)
    assert response.status_code == 406
    assert insert_guest_fail in response.data
    

# -------------------------------------------------------------------------
# Delete Guest Tests
# -------------------------------------------------------------------------

def test_delete_guest(clean_db, app_tc, insert_guest):
    # Test-data is inserted with the insert_guest fixture
    # Assert that it inserted successfully
    response = app_tc.get(guest + sonny)
    assert load_n_decode(response.data) == [sonny_d]

    # Delete it
    response = app_tc.delete(guest + sonny)

    # Get the guest list and assert it is not found
    response = app_tc.get(guest)
    assert load_n_decode(response.data) == []


def test_delete_guest_returns_404_if_not_found(clean_db, app_tc):
    # Try to delete a guest that's not present in the data
    response = app_tc.delete(guest + sonny)
    # Assert it's a 404
    assert response.status_code == 404
    assert load_n_decode(response.data)['response'] == "Guest not found"


# -------------------------------------------------------------------------
# Get Guest Tests
# -------------------------------------------------------------------------

def test_get_guest(clean_db, insert_guest, app_tc):
    # Test-data is inserted with insert_guest fixture
    # Test that we can get the guest that was inserted
    response = app_tc.get(guest + sonny)
    assert load_n_decode(response.data)[0] == sonny_d 

