from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
load_lab_env(ROOT)

SYSTEM_PROMPT_PATH = ROOT / "artifacts" / "system_prompt.md"
TOOLS_PATH = ROOT / "artifacts" / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini"]
PROVIDER_ENV_KEYS = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}
TOOL_COLORS = {
    "clarify": "#b8860b",
    "escalate_to_clinician": "#c0392b",
    "notify_caregiver": "#b5651d",
    "confirm_dose_taken": "#2e7d32",
    "record_side_effect": "#6a3ea1",
}
DEFAULT_TOOL_COLOR = "#2b6cb0"

st.set_page_config(page_title="Medication Adherence Assistant", page_icon="💊", layout="wide")


def default_provider() -> str:
    for name in PROVIDERS:
        if os.getenv(PROVIDER_ENV_KEYS[name]):
            return name
    return "openrouter"


@st.cache_resource(show_spinner=False)
def load_artifacts() -> tuple[str, list[dict[str, Any]]]:
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    tool_decls = load_tool_declarations(TOOLS_PATH)
    return system_prompt, to_openai_tools(tool_decls)


system_prompt, openai_tools = load_artifacts()

with st.sidebar:
    st.header("Cấu hình")
    provider_name = st.selectbox("Provider", PROVIDERS, index=PROVIDERS.index(default_provider()))
    model_override = st.text_input("Model override (để trống = mặc định của provider)", value="")
    version_label = st.text_input("Version label", value="v3")
    max_tool_rounds = st.slider("Max tool rounds", 1, 8, 4)
    st.divider()
    if st.button("🔄 Cuộc hội thoại mới", use_container_width=True):
        for key in ("messages", "transcript", "transcript_path"):
            st.session_state.pop(key, None)
        st.rerun()

artifact_ver = build_artifact_version(version_label, SYSTEM_PROMPT_PATH, TOOLS_PATH)

st.title("💊 Medication Adherence Assistant")
st.caption(
    f"Provider: `{provider_name}` · Model: `{model_override or 'default'}` · "
    f"Artifact version: `{artifact_ver.artifact_version}`"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "transcript_path" not in st.session_state:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version_label), safe_slug(provider_name), "streamlit", timestamp])
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_ver),
        "provider": provider_name,
        "model": model_override or None,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def render_tool_events(tool_events: list[dict[str, Any]]) -> None:
    if not tool_events:
        return
    with st.expander(f"🔍 Chi tiết Tool Calling Traces ({len(tool_events)})", expanded=False):
        for event in tool_events:
            color = TOOL_COLORS.get(event["tool"], DEFAULT_TOOL_COLOR)
            st.markdown(
                f'<span style="background:{color}22;color:{color};padding:2px 10px;'
                f'border-radius:999px;font-size:12px;font-weight:700;">{event["tool"]}</span>',
                unsafe_allow_html=True,
            )
            if event.get("args"):
                st.caption(" · ".join(f"`{k}={v!r}`" for k, v in event["args"].items()))
            st.json(event.get("result", {}), expanded=False)


def extract_quick_replies(turn_record: dict[str, Any]) -> list[str] | None:
    if turn_record.get("status") != "waiting_for_user":
        return None
    tool_events = turn_record.get("tool_events") or []
    if not tool_events:
        return None
    last = tool_events[-1]
    if last.get("tool") != "clarify":
        return None
    result = last.get("result") or {}
    if result.get("response_type") == "yes_no":
        return ["Có", "Không"]
    if result.get("response_type") == "choice" and result.get("options"):
        return list(result["options"])
    return None


def handle_user_message(user_text: str) -> None:
    user_text = user_text.strip()
    if not user_text:
        return

    st.session_state.messages.append({"role": "user", "content": user_text})

    provider = make_provider(provider_name)
    messages = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages:
        messages.append({"role": m["role"], "content": m["content"]})

    turn_index = len(st.session_state.transcript["turns"]) + 1
    turn_record: dict[str, Any] = {
        "turn_index": turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
        "provider": provider_name,
        "model": model_override or None,
    }

    try:
        with st.spinner("Agent đang xử lý và kích hoạt tools..."):
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=model_override or None,
                max_tool_rounds=max_tool_rounds,
            )
        turn_record.update(result)
        reply = result["assistant_text"]
    except Exception as exc:  # keep the UI alive; surface the error instead of crashing the app
        reply = f"{type(exc).__name__}: {exc}"
        turn_record.update({"status": "provider_error", "assistant_text": reply})

    turn_record["ended_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "tools": turn_record.get("tool_events", []),
        "status": turn_record.get("status"),
        "quick_replies": extract_quick_replies(turn_record),
    })


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("status") == "provider_error":
            st.error(msg["content"])
        elif msg.get("status") == "max_tool_rounds":
            st.warning(msg["content"])
        else:
            st.markdown(msg["content"])
        render_tool_events(msg.get("tools", []))

last_msg = st.session_state.messages[-1] if st.session_state.messages else None
if last_msg and last_msg["role"] == "assistant" and last_msg.get("quick_replies"):
    st.write("**Trả lời nhanh:**")
    cols = st.columns(len(last_msg["quick_replies"]))
    for col, label in zip(cols, last_msg["quick_replies"]):
        key = f"quick_{len(st.session_state.messages)}_{label}"
        if col.button(label, key=key, use_container_width=True):
            handle_user_message(label)
            st.rerun()

if prompt := st.chat_input("Nhập yêu cầu về tuân thủ thuốc..."):
    handle_user_message(prompt)
    st.rerun()
