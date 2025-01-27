from src.app import say_hello

def test_app():
    assert say_hello("Dan") == "Hello Dan!"