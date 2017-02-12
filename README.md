# Simple guest management and RSVP system
## Installation
Works with python 3.4
```bash
$ git clone https://github.com/2achary/rsvp.git
$ cd rsvp
$ pip3 install flask
$ python3 app.py
```
Navigate to `127.0.0.1` for the RSVP form and `127.0.0.1/#/guest_list` for the guest management page.

## To Run the tests
```bash
$ pip3 install requests pytest
$ python3 -m pytest -qq tests
```
## To use
From the guest management page `127.0.0.1/#/guest_list`, you can add and delete names of guests that are allowed to submit an RSVP. Once the name is added to the guest list, the guest can enter their name into the RSVP form and choose to accept or decline the invitation. Once a guest has submitted their RSVP, you can see the state of their RSVP and how many total guests have chosen to accept the invitation.

