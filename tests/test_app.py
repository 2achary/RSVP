import random
import shelve
import os
import json
from app import app
import pytest

# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------

invalid_args_list = [
    'guest/firstName/Sonny/lastName/',
    'guest/firstName/lastName/Hanback',
    'guest/firstName',
    ''
]

guest_dicts = [
    {'firstName': 'James', 'lastName': 'Fox'},
    {'firstName': 'Lisa', 'lastName': 'Miller'},
    {'firstName': 'Jessica', 'lastName': 'Van Meter'},
    {'firstName': 'Sonny', 'lastName': 'Hanback'}
]

guest_urls = [
    '/guest/firstName/James/lastName/Fox',
    '/guest/firstName/Lisa/lastName/Miller',
    '/guest/firstName/Jessica/lastName/Van%20Meter',
    '/guest/firstName/Sonny/lastName/Hanback'
]

guest_url_lookup = dict(zip(guest_urls, guest_dicts))

insert_guest_success = "Successfully added guest"
delete_guest_success = "Successfully deleted"
insert_guest_fail = "First and last name required"
shelf_name = os.path.join('guest_list.shelf')
guest_list_key = 'guest_list'

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------


def load_n_decode(b):
    return json.loads(b.decode('utf-8'))

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def insert_guest(app_tc):
    """Insert guest and return the function to insert the guest again"""
    def inner(url=None):
        if url is None:
            # Use the last item in the list
            url = guest_urls[random.choice([0, 1, 2, 3])]
        app_tc.post(url)
        return url
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


# -----------------------------------------------------------------------------
# Insert Guest Tests
# -----------------------------------------------------------------------------

def test_insert_guest(app_tc, clean_db):

    # Post to the guest endpoint with valid args
    response = app_tc.post(guest_urls[0])

    # Assert that we got correct response and status code
    assert response.status_code == 201
    loaded_response = load_n_decode(response.data)['response']
    assert insert_guest_success == loaded_response

    # Let's make sure what we inserted is actually still there
    response = app_tc.get('/guest')
    assert guest_dicts[0] in load_n_decode(response.data)


# -----------------------------------------------------------------------------
# Delete Guest Tests
# -----------------------------------------------------------------------------

def test_delete_guest(clean_db, app_tc, insert_guest):
    # Test-data is inserted with the insert_guest fixture
    # Assert that it inserted successfully
    guest_url = insert_guest()
    response = app_tc.get(guest_url)
    assert load_n_decode(response.data) == guest_url_lookup[guest_url]

    # Delete it
    response = app_tc.delete(guest_url)
    assert load_n_decode(response.data)['response'] == delete_guest_success
    assert response.status_code == 200

    # Get the guest list and assert it is not found
    response = app_tc.get('/guest')
    assert load_n_decode(response.data) == []


def test_delete_guest_returns_404_if_not_found(clean_db, app_tc):
    # Try to delete a guest that's not present in the data
    response = app_tc.delete(guest_urls[0])
    # Assert it's a 404
    assert response.status_code == 404
    assert load_n_decode(response.data)['response'] == "Guest not found"


# -----------------------------------------------------------------------------
# Get Guest Tests
# -----------------------------------------------------------------------------

def test_get_guest(clean_db, insert_guest, app_tc):
    guest_query_string = insert_guest()

    # Test that we can get the guest that was inserted
    response = app_tc.get(guest_query_string)
    assert load_n_decode(response.data) == guest_url_lookup[guest_query_string]
    assert response.status_code == 200


def test_guest_not_found_returns_404(clean_db, app_tc):
    # No guest was inserted so anything should return 404
    response = app_tc.get(guest_urls[0])
    assert response.status_code == 404
    expected = "Guest not found"
    observed = load_n_decode(response.data)['response']
    assert expected == observed
