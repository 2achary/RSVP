"""
Simple guest and RSVP management API for a single event

Uses python shelve for local object persistence. Edit `guest_list_backup.json`
to include names you want auto-populated in the shelf. If you delete the
shelve file `guest_list.shelf.db` and re-run the API directly, the json file
will be used to populate the shelf.

Navigate to 127.0.0.1 to get to the RSVP form
Navigate to 127.0.0.1/#/guest_list to get to the guest management page
"""

from flask import Flask, make_response, request
import json
import os
import shelve


shelf_name = 'guest_list.shelf'
guest_list_key = 'guest_list'
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


def get_guest_from_args(args):
    guest =  {
        'firstName': args.get('firstName'),
        'lastName': args.get('lastName')
    }
    if len(guest) == 2 and all(v is not None for k, v in guest.items()):
        return guest
    else:
        raise KeyError


def find_guest_in_list(guest, guest_list):
    for g in guest_list:
        if all(g[k] == v for k, v in guest.items()):
            return g
    else:
        raise ValueError

# -----------------------------------------------------------------------------
# API
# -----------------------------------------------------------------------------


@app.route('/guest', methods=['POST'])
def insert_guest():
    try:
        guest_dict = get_guest_from_args(request.args)
    except KeyError:
        # Return 406 Unacceptable status code
        return json.dumps({"response": "First and last name required"}), 406

    # Insert the guest dict into the shelf
    with shelve.open(shelf_name) as shelf:
        guest_list = shelf[guest_list_key]
        guest_list.append(guest_dict)
        shelf[guest_list_key] = guest_list
    return json.dumps({'response': "Successfully added guest"}), 201


@app.route('/guest', methods=['DELETE'])
def delete_guest():
    try:
        guest_dict = get_guest_from_args(request.args)
    except KeyError:
        # Return 406 Unacceptable status code
        return json.dumps({"response": "First and last name required"}), 406

    with shelve.open(shelf_name) as shelf:
        # Get a copy of the current guest list
        guest_list = shelf[guest_list_key]
        try:
            # Try to remove the dict from the guest list
            guest_list.remove(guest_dict)
        except ValueError:
            # Return a not found status code
            return json.dumps({'response': "Guest not found"}), 404
        shelf[guest_list_key] = guest_list
        return json.dumps({"response": "Successfully deleted"})


@app.route('/guest', methods=['GET'])
def get_guest_list():
    with shelve.open(shelf_name) as shelf:
        guest_list = shelf[guest_list_key]
        try:
            guest_dict = get_guest_from_args(request.args)
        except KeyError:
            # Return the  whole list if the args aren't there
            return json.dumps(guest_list)

        try:
            # Return the matching guest dict in a list
            return json.dumps([find_guest_in_list(guest_dict, guest_list)])
        except ValueError:
            return json.dumps({"response": "Guest not found"}), 404


@app.route('/rsvp', methods=['POST'])
def rsvp():
    try:
        guest_dict = get_guest_from_args(request.args)
        answer = True if request.args['answer'] == 'true' else False
    except KeyError:
        return json.dumps({
            "response": "First name, last name and answer required"
        }), 406
    with shelve.open(shelf_name) as shelf:
        guest_list = shelf[guest_list_key]
        try:
            # Update the rsvp status
            matching_guest = find_guest_in_list(guest_dict, guest_list)
            matching_index = guest_list.index(matching_guest)
        except ValueError:
            return json.dumps({"response": "Guest not found"}), 404

        guest_list[matching_index]['RSVP'] = answer
        shelf[guest_list_key] = guest_list
        return json.dumps({"response": "Successfully submitted RSVP"})


if __name__ == '__main__':
    make_shelf_if_needed()
    app.run(debug=True)
