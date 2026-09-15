from __future__ import annotations

import argparse
import json
import threading
import uuid
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

from chat import (
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
WEB_DIR = ROOT / "web"

SESSIONS: dict[str, dict[str, Any]] = {}
SESSIONS_LOCK = threading.Lock()
PROVIDER_LOCK = threading.Lock()

CONFIG: dict[str, Any] = {}


def new_session() -> dict[str, Any]:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([
        safe_slug(CONFIG["version"]),
        safe_slug(CONFIG["provider_name"]),
        "web",
        timestamp,
    ])
    transcript_path = CONFIG["transcripts_dir"] / f"{transcript_id}.transcript.json"
    transcript: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(CONFIG["artifact_version"]),
        "provider": CONFIG["provider_name"],
        "model": CONFIG["selected_model"],
        "system_prompt": str(CONFIG["system_prompt_path"]),
        "tools": str(CONFIG["tools_path"]),
        "history_window": CONFIG["history_window"],
        "max_tool_rounds": CONFIG["max_tool_rounds"],
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    session = {
        "session_id": uuid.uuid4().hex,
        "history": [],
        "turn_index": 0,
        "transcript_path": transcript_path,
        "transcript": transcript,
    }
    with SESSIONS_LOCK:
        SESSIONS[session["session_id"]] = session
    return session


def session_meta(session: dict[str, Any]) -> dict[str, Any]:
    return {
        "session_id": session["session_id"],
        "provider": CONFIG["provider_name"],
        "model": CONFIG["selected_model"],
        "artifact_version": CONFIG["artifact_version"].artifact_version,
        "version": CONFIG["artifact_version"].version,
    }


def run_turn(session: dict[str, Any], user_text: str) -> dict[str, Any]:
    session["turn_index"] += 1
    messages = [
        {"role": "system", "content": CONFIG["system_prompt"]},
        *trim_history(session["history"], CONFIG["history_window"]),
        {"role": "user", "content": user_text},
    ]

    turn_record: dict[str, Any] = {
        "turn_index": session["turn_index"],
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    try:
        with PROVIDER_LOCK:
            result = run_model_tool_loop(
                provider=CONFIG["provider"],
                messages=messages,
                tools=CONFIG["openai_tools"],
                model=CONFIG["model_arg"],
                max_tool_rounds=CONFIG["max_tool_rounds"],
            )
        turn_record.update(result)
        assistant_text = result["assistant_text"]
        session["history"].append({"role": "user", "content": user_text})
        session["history"].append({"role": "assistant", "content": assistant_text})
    except Exception as exc:  # keep the UI alive; surface the error in the transcript and response
        turn_record.update({
            "status": "provider_error",
            "assistant_text": f"{type(exc).__name__}: {exc}",
        })

    turn_record["ended_at"] = now_iso()
    session["transcript"]["turns"].append(turn_record)
    write_transcript(session["transcript_path"], session["transcript"])
    return turn_record


class Handler(BaseHTTPRequestHandler):
    server_version = "MedAdherenceUI/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:  # quieter console
        print("[web] " + (fmt % args))

    def _send_json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return {}

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            html = (WEB_DIR / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        self._send_json({"error": "not_found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/session":
            session = new_session()
            self._send_json(session_meta(session))
            return

        if self.path == "/api/chat":
            body = self._read_json()
            session_id = body.get("session_id", "")
            message = (body.get("message") or "").strip()
            with SESSIONS_LOCK:
                session = SESSIONS.get(session_id)
            if session is None:
                self._send_json({"error": "unknown_session"}, status=404)
                return
            if not message:
                self._send_json({"error": "empty_message"}, status=400)
                return
            turn_record = run_turn(session, message)
            self._send_json(turn_record)
            return

        self._send_json({"error": "not_found"}, status=404)


def build_config(args: argparse.Namespace) -> None:
    system_prompt_path: Path = args.system_prompt
    tools_path: Path = args.tools
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(args.provider)
    selected_model = args.model or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(args.version, system_prompt_path, tools_path)

    CONFIG.update({
        "provider": provider,
        "provider_name": args.provider,
        "model_arg": args.model,
        "selected_model": selected_model,
        "system_prompt": system_prompt,
        "system_prompt_path": system_prompt_path,
        "tools_path": tools_path,
        "openai_tools": openai_tools,
        "history_window": args.history_window,
        "max_tool_rounds": args.max_tool_rounds,
        "transcripts_dir": args.transcripts_dir,
        "version": args.version,
        "artifact_version": artifact_version,
    })


def main() -> None:
    parser = argparse.ArgumentParser(description="Local web UI for the medication-adherence agent.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", required=True, help="Student-chosen artifact version label, e.g. v0, v1, v2.")
    parser.add_argument("--system-prompt", type=Path, default=ARTIFACTS_DIR / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ARTIFACTS_DIR / "tools.yaml")
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    build_config(args)

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}/"
    print(f"Medication Adherence Assistant UI running at {url}")
    print(f"artifact_version={CONFIG['artifact_version'].artifact_version}")
    print("Press Ctrl+C to stop.")

    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
