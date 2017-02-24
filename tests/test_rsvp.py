import shelve
import os
import json
from app import app
import pytest
# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------

invalid_args_list = [
    '?firstName=Sonny',
    '?lastName=Hanback',
    '?firstName',
    ''
]

guest_dicts = [
    {'firstName': 'James', 'lastName': 'Fox'},
    {'firstName': 'Lisa', 'lastName': 'Miller'},
    {'firstName': 'Jessica', 'lastName': 'Van Meter'},
    {'firstName': 'Sonny', 'lastName': 'Hanback'}
]

guest_query_strings = [
    '?firstName=James&lastName=Fox',
    '?firstName=Lisa&lastName=Miller',
    '?firstName=Jessica&lastName=Van%20Meter',
    '?firstName=Sonny&lastName=Hanback'
]

guest_query_strings_lookup = dict(zip(guest_query_strings, guest_dicts))

insert_guest_success = b"Successfully added guest"
insert_guest_fail = b"First and last name required"
guest_route = '/guest'
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
    def inner(query_string=None):
        if query_string is None:
            # Use the last item in the list
            query_string = guest_query_strings[-1]
            # Rotate the list by moving the last item to the first position
            guest_query_strings.insert(0, guest_query_strings.pop())
        app_tc.post(guest_route + query_string)
        return query_string

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
    response = app_tc.post(guest_route + guest_query_strings[0])

    # Assert that we got correct response and status code
    assert response.status_code == 201
    assert insert_guest_success in response.data

    # Let's make sure what we inserted is actually still there
    response = app_tc.get(guest_route)
    assert guest_dicts[0] in load_n_decode(response.data)


def test_insert_guest_406_if_invalid_args(invalid_arg, clean_db, app_tc):
    response = app_tc.post(guest_route + invalid_arg)
    assert response.status_code == 406
    assert insert_guest_fail in response.data


# -----------------------------------------------------------------------------
# Delete Guest Tests
# -----------------------------------------------------------------------------

def test_delete_guest(clean_db, app_tc, insert_guest):
    # Test-data is inserted with the insert_guest fixture
    # Assert that it inserted successfully
    guest_query_string = insert_guest()
    response = app_tc.get(guest_route + guest_query_string)
    assert load_n_decode(response.data) == [guest_query_strings_lookup[guest_query_string]]

    # Delete it
    response = app_tc.delete(guest_route + guest_query_string)

    # Get the guest list and assert it is not found
    response = app_tc.get(guest_route)
    assert load_n_decode(response.data) == []


def test_delete_guest_returns_404_if_not_found(clean_db, app_tc):
    # Try to delete a guest that's not present in the data
    response = app_tc.delete(guest_route + guest_query_strings[0])
    # Assert it's a 404
    assert response.status_code == 404
    assert load_n_decode(response.data)['response'] == "Guest not found"


# -----------------------------------------------------------------------------
# Get Guest Tests
# -----------------------------------------------------------------------------

def test_get_guest(clean_db, insert_guest, app_tc):
    guest_query_string = insert_guest()

    # Test that we can get the guest that was inserted
    response = app_tc.get(guest_route + guest_query_string)
    assert load_n_decode(response.data)[0] == guest_query_strings_lookup[guest_query_string]
    assert response.status_code == 200


def test_guest_not_found_returns_404(clean_db, app_tc):
    # No guest was inserted so anything should return 404
    response = app_tc.get(guest_route + guest_query_strings[0])
    assert response.status_code == 404
    expected = "Guest not found"
    observed = load_n_decode(response.data)['response']
    assert expected == observed
