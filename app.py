"""
Simple guest and RSVP management API for a single event

Uses python shelve for local object persistence. Edit `guest_list_backup.json`
to include names you want auto-populated in the shelf. If you delete the
shelve file `guest_list.shelf.db` and re-run the API directly, the json file
will be used to populate the shelf.

```
pip3 install flask
python3 app.py
```

Navigate to 127.0.0.1 to get to the RSVP form
Navigate to 127.0.0.1/#/guest_list to get to the guest management page
"""
import json
import os

from flask import Flask, make_response

import data_access

shelf_name = 'guest_list.shelf'
guest_list_key = 'guest_list'
guest_route = '/guest/firstName/<string:first_name>/' \
              'lastName/<string:last_name>'
rsvp_route = '/rsvp/firstName/<string:first_name>/' \
              'lastName/<string:last_name>/answer/<string:answer>'
app = Flask(__name__)

# -----------------------------------------------------------------------------
# Serve angular page
# -----------------------------------------------------------------------------


@app.route('/')
def rsvp_form():
    return make_response(open('static/index.html').read())


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def make_shelf_if_needed():
    if not os.path.isfile(shelf_name + '.db'):
        # Insert the test data into a new shelf
        from insert_test_data import insert_test_data
        insert_test_data()


# -----------------------------------------------------------------------------
# API
# -----------------------------------------------------------------------------


@app.route(guest_route, methods=['POST'])
def insert_guest(first_name, last_name):
    data_access.insert_guest(first_name, last_name)
    return json.dumps({'response': "Successfully added guest"}), 201


@app.route(guest_route, methods=['DELETE'])
def delete_guest(first_name, last_name):
    try:
        data_access.delete_guest(first_name, last_name)
    except ValueError:
        return json.dumps({'response': "Guest not found"}), 404

    return json.dumps({"response": "Successfully deleted"})


@app.route(guest_route, methods=['GET'])
def get_guest(first_name, last_name):
    try:
        return json.dumps(data_access.get_guest(first_name, last_name))
    except ValueError:
        return json.dumps({"response": "Guest not found"}), 404


@app.route('/guest', methods=['GET'])
def get_guest_list():
    return json.dumps(data_access.get_guest_list())


@app.route(rsvp_route, methods=['POST'])
def rsvp(first_name, last_name, answer):
    if answer == 'true':
        answer = True
    else:
        answer = False
    try:
        return json.dumps(data_access.rsvp(first_name, last_name, answer))
    except (ValueError, Exception) as e:
        return json.dumps({"response": "Guest not found"}), 404

if __name__ == '__main__':
    make_shelf_if_needed()
    app.run(debug=True)
