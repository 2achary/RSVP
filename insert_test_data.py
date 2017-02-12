import json
import shelve


def insert_test_data():
    with open('guest_list_backup.json', 'r') as f:
        with shelve.open('guest_list.shelf') as shelf:
            shelf['guest_list'] = json.load(f)

if __name__ == '__main__':
    insert_test_data()
