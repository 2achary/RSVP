from data_access import insert_guest


def test_insert_guest_saves_new_guest():
    result = insert_guest('Rick', 'Grimes')
    expected = {'firstName': 'Rick', 'lastName': 'Grimes'}
    assert result == expected
