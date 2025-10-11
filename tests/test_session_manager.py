from src.session_manager import SessionManager


def test_get_session_creates_new():
    manager = SessionManager()
    session = manager.get_session(123)
    assert session == []


def test_add_message():
    manager = SessionManager()
    manager.add_message(123, "user", "Привет")
    session = manager.get_session(123)
    assert len(session) == 1
    assert session[0] == {"role": "user", "content": "Привет"}


def test_add_multiple_messages():
    manager = SessionManager()
    manager.add_message(123, "user", "Привет")
    manager.add_message(123, "assistant", "Здравствуйте")
    session = manager.get_session(123)
    assert len(session) == 2
    assert session[0] == {"role": "user", "content": "Привет"}
    assert session[1] == {"role": "assistant", "content": "Здравствуйте"}


def test_clear_session():
    manager = SessionManager()
    manager.add_message(123, "user", "Привет")
    manager.clear_session(123)
    assert manager.get_session(123) == []


def test_multiple_users():
    manager = SessionManager()
    manager.add_message(123, "user", "Сообщение 1")
    manager.add_message(456, "user", "Сообщение 2")

    session_123 = manager.get_session(123)
    session_456 = manager.get_session(456)

    assert len(session_123) == 1
    assert len(session_456) == 1
    assert session_123[0]["content"] == "Сообщение 1"
    assert session_456[0]["content"] == "Сообщение 2"

