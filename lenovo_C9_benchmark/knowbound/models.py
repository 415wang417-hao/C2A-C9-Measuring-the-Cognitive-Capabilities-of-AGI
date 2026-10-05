"""Local model client for Ollama + robust JSON extraction.

Design notes
------------
* ``requests`` is used when installed, ``urllib.request`` otherwise.
* Calls are **serial** (the target machine has 8 GB VRAM and little free RAM).
* Every call is timed and the raw response is kept verbatim so that failures can
  be audited after the fact -- nothing is silently swallowed.
* ``"think": false`` is sent in the request body; if the server rejects the field
  the client retries without it and additionally hardens the system prompt.
* ``extract_json`` implements three escalating strategies (strict load -> fenced
  / first balanced object -> regex key/value salvage) so a malformed reply never
  crashes the run.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple

try:  # pragma: no cover - trivial import guard
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None

try:  # pragma: no cover
    from urllib import request as _urlreq
    from urllib.error import URLError
except Exception:  # pragma: no cover
    _urlreq = None
    URLError = Exception  # type: ignore

CHAT_PATH = "/api/chat"


# ---------------------------------------------------------------------------
# JSON extraction
# ---------------------------------------------------------------------------

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S | re.I)


def _first_balanced(text: str) -> Optional[str]:
    """Return the first balanced {...} or [...] block, string-aware."""
    start = None
    depth = 0
    in_str = False
    esc = False
    opener = closer = ""
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch in "{[":
            if depth == 0:
                start = i
                opener, closer = ch, "}" if ch == "{" else "]"
            depth += 1
        elif ch in "}]":
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    return text[start:i + 1]
            elif depth == 0:
                continue
    # unterminated block: return the remainder so the salvage step can try
    return text[start:] if start is not None else None


def extract_json(text: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Best-effort JSON object extraction.

    Returns ``(obj_or_None, strategy_name)`` where strategy is one of
    ``strict|fence|balanced|salvage|failed``.
    """
    if not text:
        return None, "failed"
    raw = text.strip()

    for candidate, name in ((raw, "strict"),):
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                return obj, name
        except Exception:
            pass

    m = _FENCE.search(raw)
    if m:
        try:
            obj = json.loads(m.group(1).strip())
            if isinstance(obj, dict):
                return obj, "fence"
        except Exception:
            pass

    blk = _first_balanced(raw)
    if blk:
        for cand in (blk, blk.replace("'", '"'), re.sub(r",\s*([}\]])", r"\1", blk)):
            try:
                obj = json.loads(cand)
                if isinstance(obj, dict):
                    return obj, "balanced"
            except Exception:
                continue

    # salvage: regex key/value pairs (numbers, quoted strings, booleans)
    out: Dict[str, Any] = {}
    for key in ("answer", "confidence", "can_answer", "decision"):
        mk = re.search(r'["\']?' + key + r'["\']?\s*[:=]\s*(".*?"|\'.*?\'|'
                       r'true|false|null|-?\d+(?:\.\d+)?)', raw, re.S | re.I)
        if not mk:
            continue
        val = mk.group(1)
        if val.startswith(('"', "'")):
            out[key] = val[1:-1]
        elif val.lower() in ("true", "false"):
            out[key] = val.lower() == "true"
        elif val.lower() == "null":
            out[key] = None
        else:
            out[key] = float(val) if "." in val else int(val)
    if out:
        return out, "salvage"
    return None, "failed"


def coerce_confidence(value: Any) -> Optional[float]:
    """Map 0-100 or 0-1 style confidences onto [0, 1]; ``None`` if unparseable."""
    if value is None:
        return None
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, str):
        m = re.search(r"-?\d+(?:\.\d+)?", value)
        if not m:
            return None
        value = float(m.group(0))
        if "%" in value if isinstance(value, str) else False:
            return max(0.0, min(1.0, value / 100.0))
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if v > 1.0:
        v = v / 100.0
    return max(0.0, min(1.0, v))


def coerce_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        s = value.strip().lower()
        if s in ("true", "yes", "y", "1"):
            return True
        if s in ("false", "no", "n", "0"):
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return None


# ---------------------------------------------------------------------------
# client
# ---------------------------------------------------------------------------

class OllamaClient:
    def __init__(self, model: str, endpoint: str = "http://127.0.0.1:11434",
                 temperature: float = 0.0, num_predict: int = 256,
                 timeout_sec: int = 180, think: bool = False,
                 seed: int = 0, api: str = "auto"):
        self.model = model
        self.endpoint = endpoint.rstrip("/")
        self.temperature = temperature
        self.num_predict = num_predict
        self.timeout_sec = timeout_sec
        self.think = think
        self.seed = seed
        self.api = api
        self._think_supported: Optional[bool] = None
        self.stats = {"calls": 0, "errors": 0, "total_latency": 0.0}

    # -- transport ---------------------------------------------------------
    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = self.endpoint + path
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if requests is not None:
            resp = requests.post(url, data=data, headers=headers,
                                 timeout=self.timeout_sec)
            if resp.status_code >= 400:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
            return resp.json()
        if _urlreq is None:  # pragma: no cover
            raise RuntimeError("no HTTP backend available")
        req = _urlreq.Request(url, data=data, headers=headers, method="POST")
        with _urlreq.urlopen(req, timeout=self.timeout_sec) as fh:
            return json.loads(fh.read().decode("utf-8"))

    def ping(self) -> Dict[str, Any]:
        try:
            if requests is not None:
                r = requests.get(self.endpoint + "/api/tags", timeout=10)
                if r.status_code >= 400:
                    return {"ok": False, "error": f"HTTP {r.status_code}"}
                tags = r.json().get("models", [])
                return {"ok": True,
                        "models": [t.get("name") for t in tags]}
        except Exception as exc:
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        return {"ok": False, "error": "requests unavailable"}

    # -- chat --------------------------------------------------------------
    def chat(self, messages: List[Dict[str, str]], retries: int = 1) -> Dict[str, Any]:
        """Single serial chat call. Never raises: failures are recorded."""
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": self.temperature,
                        "num_predict": self.num_predict,
                        "seed": self.seed},
        }
        if self.think:
            payload["think"] = True
        elif self._think_supported is not False:
            payload["think"] = False

        last_err = None
        for attempt in range(retries + 1):
            started = time.time()
            try:
                parsed = self._post(CHAT_PATH, payload)
                latency = time.time() - started
                content = ((parsed.get("message") or {}).get("content") or "")
                thinking = ((parsed.get("message") or {}).get("thinking") or "")
                if content.strip() == "" and thinking.strip():
                    # model ignored "think": false and only produced reasoning
                    if "think" in payload:
                        self._think_supported = False
                        payload.pop("think", None)
                        continue
                if "think" in payload and not thinking and self._think_supported is None:
                    self._think_supported = True
                self.stats["calls"] += 1
                self.stats["total_latency"] += latency
                return {"ok": True, "text": content, "thinking": thinking,
                        "latency_sec": round(latency, 3),
                        "raw": parsed, "error": None}
            except Exception as exc:
                latency = time.time() - started
                last_err = f"{type(exc).__name__}: {str(exc)[:300]}"
                msg = last_err.lower()
                if "think" in payload and ("think" in msg or "unknown field" in msg
                                           or "invalid" in msg and "400" in msg):
                    self._think_supported = False
                    payload.pop("think", None)
                    continue
                break

        # one hardening retry with an explicit JSON-only reminder
        if retries >= 1:
            hardened = [dict(m) for m in messages]
            if hardened and hardened[0]["role"] == "system":
                hardened[0]["content"] += ("\nReply with one JSON object only, "
                                           "no code fences, no commentary.")
            payload["messages"] = hardened
            started = time.time()
            try:
                parsed = self._post(CHAT_PATH, payload)
                latency = time.time() - started
                self.stats["calls"] += 1
                self.stats["total_latency"] += latency
                content = ((parsed.get("message") or {}).get("content") or "")
                return {"ok": True, "text": content, "thinking": "",
                        "latency_sec": round(latency, 3), "raw": parsed,
                        "error": None, "hardened_retry": True}
            except Exception as exc:
                last_err = f"{type(exc).__name__}: {str(exc)[:300]}"

        self.stats["calls"] += 1
        self.stats["errors"] += 1
        return {"ok": False, "text": "", "thinking": "", "latency_sec": None,
                "raw": None, "error": last_err or "unknown error"}

    def ask_json(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """``chat`` + JSON extraction, in one place, so every caller gets both."""
        res = self.chat(messages)
        obj, strategy = extract_json(res.get("text") or "")
        res["parsed"] = obj
        res["parse_strategy"] = strategy
        return res

    def avg_latency(self) -> Optional[float]:
        ok = self.stats["calls"] - self.stats["errors"]
        return round(self.stats["total_latency"] / ok, 3) if ok > 0 else None
