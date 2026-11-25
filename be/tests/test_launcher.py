import be
import be.chat
import uvicorn


def test_main_dispatches_to_each_application(monkeypatch):
    choices = iter(["1", "2", "3", "q"])
    calls = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))
    monkeypatch.setattr(be, "run_notes_cli", lambda: calls.append("cli"))
    monkeypatch.setattr(
        uvicorn,
        "run",
        lambda app, **kwargs: calls.append(("api", app, kwargs)),
    )
    monkeypatch.setattr(be.chat, "main", lambda: calls.append("chat"))

    be.main()

    assert calls == [
        "cli",
        (
            "api",
            "be.api:app",
            {"host": "127.0.0.1", "port": 8000},
        ),
        "chat",
    ]
