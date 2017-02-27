import shelve


shelf_name = 'guest_list.shelf'
guest_list_key = 'guest_list'

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------


def make_guest_dict(first_name, last_name):
    return {
        'firstName': first_name,
        'lastName': last_name
    }


def find_guest_in_list(guest_filter, guest_list):
    for g in guest_list:
        if all(g[k] == v for k, v in guest_filter.items()):
            return g
    else:
        raise ValueError


# -----------------------------------------------------------------------------
# Data access functions
# -----------------------------------------------------------------------------


def insert_guest(first_name, last_name):
    guest_dict = make_guest_dict(first_name, last_name)
    # Insert the guest dict into the shelf
    with shelve.open(shelf_name, writeback=True) as shelf:
        try:
            guest_list = shelf[guest_list_key]
        except KeyError:
            guest_list = []

        guest_list.append(guest_dict)
    return guest_dict


def delete_guest(first_name, last_name):
    """
    Removes guest from shelf with matching first and last name or a ValueError
    is raised. Returns None if successful.
    """
    guest_dict = make_guest_dict(first_name, last_name)

    with shelve.open(shelf_name, writeback=True) as shelf:
        # Get a copy of the current guest list
        guest_list = shelf[guest_list_key]

        # Try to remove the dict from the guest list. Will throw ValueError
        # if not found
        guest_record = find_guest_in_list(guest_dict, guest_list)
        guest_list.remove(guest_record)
        shelf[guest_list_key] = guest_list


def get_guest(first_name, last_name):
    """
    Returns a tuple of matching guest and list index of the guest or a
    ValueError is raised if no matching guest
    """
    with shelve.open(shelf_name) as shelf:
        try:
            guest_list = shelf[guest_list_key]
        except KeyError:
            guest_list = []

        guest_dict = make_guest_dict(first_name, last_name)

        # Return the matching guest dict in a list if found, or a ValueError
        # will be raised if the dict isn't in the list
        matching_guest = find_guest_in_list(guest_dict, guest_list)
        return matching_guest


def get_guest_list():
    with shelve.open(shelf_name) as shelf:
        try:
            guest_list = shelf[guest_list_key]
        except KeyError:
            guest_list = []

        return guest_list


def rsvp(first_name, last_name, answer):
    guest_dict = make_guest_dict(first_name, last_name)
    with shelve.open(shelf_name, writeback=True) as shelf:
        try:
            guest_list = shelf[guest_list_key]
        except KeyError:
            guest_list = []

        # Find the guest matching the query string and its index
        # in the guest list. This could raise a ValueError if not found
        matching_guest = find_guest_in_list(guest_dict, guest_list)

        # Update the rsvp status
        matching_guest['RSVP'] = answer
        return matching_guest

