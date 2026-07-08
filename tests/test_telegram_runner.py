from pathlib import Path


def test_telegram_runner_registers_commands() -> None:
    runner_module = Path("backend/telegram_bot/runner.py").read_text(encoding="utf-8")

    assert "BotCommand(" in runner_module
    assert 'CommandHandler("analyze"' in runner_module
    assert 'CommandHandler("scan"' in runner_module
    assert "set_my_commands" in runner_module

