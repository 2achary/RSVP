import json
from app import app
import pytest


@pytest.fixture
def app_test_client():
    return app.test_client()


@pytest.fixture
def s():
    class TestStrings:

        class Args:
            sonny = '?firstName=Sonny&lastName=Hanback' 
        
        class Routes:
            guest = '/guest'

        class Msg:
            insert_guest_success = b"Successfully added guest"
            insert_guest_fail = b"First and last name required" 
        args = Args
        routes = Routes
        msg = Msg
        
    return TestStrings



def test_insert_guest(app_test_client, s):
    response = app_test_client.post(s.routes.guest + s.args.sonny)
    assert response.status_code == 201
    assert s.msg.insert_guest_success in response.data
    response = app_test_client.get(s.routes.guest)
    import pdb; pdb.set_trace()

    
def test_insert_guest_406_if_no_args(app_test_client, s):
    response = app_test_client.post(s.routes.guest)
    assert response.status_code == 406
    assert s.msg.insert_guest_fail in response.data




