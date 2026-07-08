import signal
import subprocess
import sys
import time
from collections.abc import Sequence

from backend.infrastructure.config.settings import get_settings


def main() -> None:
    settings = get_settings()
    commands = [
        (
            "api",
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.main:app",
                "--host",
                settings.host,
                "--port",
                str(settings.port),
            ],
        ),
        ("telegram", [sys.executable, "-m", "backend.telegram_bot.runner"]),
        ("scheduler", [sys.executable, "-m", "backend.infrastructure.scheduler.runner"]),
    ]

    processes: list[tuple[str, subprocess.Popen[bytes]]] = []

    try:
        for name, command in commands:
            process = subprocess.Popen(command)
            processes.append((name, process))
            print(f"[start-all] {name} iniciado con PID {process.pid}")

        while True:
            for name, process in processes:
                return_code = process.poll()
                if return_code is not None:
                    raise RuntimeError(
                        f"El proceso '{name}' termino inesperadamente con codigo {return_code}."
                    )
            time.sleep(1)
    except KeyboardInterrupt:
        print("[start-all] Deteniendo servicios...")
    finally:
        _stop_processes(processes)


def _stop_processes(processes: Sequence[tuple[str, subprocess.Popen[bytes]]]) -> None:
    for _, process in processes:
        if process.poll() is None:
            process.terminate()

    deadline = time.time() + 10
    for _, process in processes:
        if process.poll() is None:
            remaining = max(deadline - time.time(), 0.1)
            try:
                process.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, lambda _signum, _frame: sys.exit(0))
    main()
