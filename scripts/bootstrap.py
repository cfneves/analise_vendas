#!/usr/bin/env python3
"""
bootstrap.py — prepara o ambiente local e sobe o Jupyter. Multiplataforma
(Windows, macOS, Linux). O Claude roda via: uv run --no-project scripts/bootstrap.py

É IDEMPOTENTE: pode rodar quantas vezes quiser. Reusa o que já existe.
No final, imprime o bloco que o Claude lê para conectar:
    JUPYTER_URL=http://localhost:PORTA
    JUPYTER_TOKEN=...

Só depende de: uv (no PATH) + a própria stdlib. Não usa bash nem python3 do
sistema — por isso funciona numa máquina "zerada" com apenas Claude Code + uv.
"""
import os, sys, socket, secrets, subprocess, time, urllib.request
from pathlib import Path

PROJ = Path(__file__).resolve().parent.parent
VENV = PROJ / ".venv"
RT = PROJ / ".runtime"
PIN_PY = "3.12"  # versão fixa para reprodutibilidade entre máquinas

IS_WIN = os.name == "nt"
VENV_PY = VENV / ("Scripts/python.exe" if IS_WIN else "bin/python")
JUPYTER = VENV / ("Scripts/jupyter.exe" if IS_WIN else "bin/jupyter")

def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)

def pid_alive(pid):
    if IS_WIN:
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                             capture_output=True, text=True)
        return str(pid) in out.stdout
    try:
        os.kill(pid, 0); return True
    except OSError:
        return False

def free_port():
    for p in (8888, 8889, 8890, 8891):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", p)); return p
            except OSError:
                continue
    with socket.socket() as s:
        s.bind(("", 0)); return s.getsockname()[1]

def main():
    RT.mkdir(exist_ok=True)
    print("🔧 Preparando o ambiente...\n")

    # 1. Ambiente virtual (uv busca/baixa o Python se a máquina não tiver)
    if not VENV.exists():
        run(["uv", "venv", "--python", PIN_PY, str(VENV)])
        print("✅ Ambiente virtual criado")
    else:
        print("✅ Ambiente virtual pronto (reaproveitado)")

    # 2. Dependências (uma vez; sentinela marca)
    sentinel = RT / ".deps_ok"
    if not sentinel.exists():
        print("   Instalando pandas, matplotlib e Jupyter (1ª vez leva ~1 min)...")
        run(["uv", "pip", "install", "--python", str(VENV_PY),
             "-r", str(PROJ / "requirements.txt")])
        # kernel com nome claro, local ao venv (sobrescreve o "python3" padrão)
        run([str(VENV_PY), "-m", "ipykernel", "install", "--prefix", str(VENV),
             "--name", "python3", "--display-name", "🤖 Análise de Dados (Claude Code)"])
        sentinel.write_text("ok")
        print("✅ Dependências instaladas")
    else:
        print("✅ Dependências prontas (reaproveitadas)")

    # 3. Servidor Jupyter: reusa se vivo, senão sobe
    pidf, portf, tokenf = RT / "jupyter.pid", RT / "jupyter.port", RT / "jupyter.token"
    alive = pidf.exists() and pid_alive(int(pidf.read_text()))
    if alive:
        port, token = int(portf.read_text()), tokenf.read_text().strip()
        print(f"✅ Servidor Jupyter no ar — porta {port} (reaproveitado)")
    else:
        port, token = free_port(), secrets.token_hex(24)
        portf.write_text(str(port)); tokenf.write_text(token)
        log = open(RT / "jupyter.log", "w")
        args = [str(JUPYTER), "lab", "--port", str(port), "--no-browser",
                "--allow-root",
                "--IdentityProvider.token", token, f"--ServerApp.root_dir={PROJ}"]
        kw = dict(stdout=log, stderr=subprocess.STDOUT, cwd=str(PROJ))
        if IS_WIN:
            kw["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | 0x00000008  # DETACHED
        else:
            kw["start_new_session"] = True
        proc = subprocess.Popen(args, **kw)
        pidf.write_text(str(proc.pid))
        print(f"✅ Servidor Jupyter no ar — porta {port}")

    # 4. Espera responder
    url = f"http://localhost:{port}"
    ready = False
    for _ in range(40):
        try:
            with urllib.request.urlopen(f"{url}/api?token={token}", timeout=2) as r:
                if r.status == 200:
                    ready = True; break
        except Exception:
            pass
        time.sleep(1)
    if not ready:
        print(f"❌ O servidor não respondeu a tempo. Veja {RT/'jupyter.log'}", file=sys.stderr)
        sys.exit(1)

    print()
    print("🔭 Abra o notebook ao vivo no navegador:")
    print(f"   {url}/lab?token={token}")
    print()
    print("---")
    print(f"JUPYTER_URL={url}")
    print(f"JUPYTER_TOKEN={token}")

if __name__ == "__main__":
    main()
