from app.core.security import hash_password, verify_password


def test_hash_password_is_not_plaintext():
    hashed = hash_password("MySecret123")
    assert hashed != "MySecret123"


def test_verify_password_success():
    hashed = hash_password("MySecret123")
    assert verify_password("MySecret123", hashed) is True


def test_verify_password_failure():
    hashed = hash_password("MySecret123")
    assert verify_password("WrongPassword", hashed) is False


def test_hash_password_handles_long_input_without_error():
    long_password = "a" * 200
    hashed = hash_password(long_password)
    assert verify_password(long_password, hashed) is True
