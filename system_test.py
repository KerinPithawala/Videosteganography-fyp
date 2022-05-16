from hello import app

def test_hello():
    response = app.test_client().get('/')

    if response.status_code != 200:
        raise AssertionError
    #assert response.data == b'Hello, World!'


