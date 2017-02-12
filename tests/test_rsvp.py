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
    
