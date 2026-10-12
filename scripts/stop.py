#!/usr/bin/env python3
"""
stop.py — encerra o servidor Jupyter deste projeto. Multiplataforma.
Roda sozinho quando o Claude Code fecha (hook SessionEnd) ou na mão:
    uv run --no-project scripts/stop.py
Não apaga o .venv nem as dependências — só derruba o servidor.
"""
import os, signal, subprocess
from pathlib import Path

RT = Path(__file__).resolve().parent.parent / ".runtime"
IS_WIN = os.name == "nt"

def pid_alive(pid):
    if IS_WIN:
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                             capture_output=True, text=True)
        return str(pid) in out.stdout
    try:
        os.kill(pid, 0); return True
    except OSError:
        return False

def main():
    pidf = RT / "jupyter.pid"
    if pidf.exists() and pid_alive(int(pidf.read_text())):
        pid = int(pidf.read_text())
        if IS_WIN:
            subprocess.run(["taskkill", "/PID", str(pid), "/F", "/T"],
                           capture_output=True)
        else:
            os.kill(pid, signal.SIGTERM)
        for f in ("jupyter.pid", "jupyter.port", "jupyter.token"):
            (RT / f).unlink(missing_ok=True)
        print("✅ Servidor Jupyter encerrado.")
    else:
        print("ℹ️  Nenhum servidor Jupyter ativo para encerrar.")

if __name__ == "__main__":
    main()
