"""Keeper watcher files: wake and sleep, finding notes with dedupe, scan, report.

Keepers are read-only for the project: this module writes only under
`_oway/keeper/`. It states facts; it never fixes anything.
"""
from __future__ import annotations

import json
import re
import secrets
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import ledger, proof
from .project import OwayError

TYPES = ("DRIFT", "LOOP", "STUCK", "NO_PROGRESS", "PACE", "DESIGN", "INTENT", "DOC_STALE",
         "FAKE_PROOF", "HARDCODE", "TAMPER", "POLICY", "SYSTEM")
TEAMS = ("oway", "product", "uix", "dev", "qa")
OWNER_MAX = 200
NOTE = re.compile(r"^FINDING (\S+) \| (.*?) \| PROOF: (.*?) \| SINCE: (\S+)$", re.M)
PATHLIKE = re.compile(r"(?:\S*/\S+|\S+\.(?:md|py|json|ts|js|sh)\b)")
CMD_TOKENS = {"python3", "python", "sh", "true", "false", "test", "git"}
OWAY_BIN = Path(__file__).resolve().parent.parent / "oway"


def kdir(oway: Path) -> Path:
    return oway / "keeper"


def _awake_path(oway: Path) -> Path:
    return kdir(oway) / "awake.json"


def awake(oway: Path) -> dict[str, str]:
    p = _awake_path(oway)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def wake(oway: Path, team: str) -> None:
    _team(team)
    a = awake(oway)
    a.setdefault(team, ledger.now())
    _awake_path(oway).parent.mkdir(parents=True, exist_ok=True)
    _awake_path(oway).write_text(json.dumps(a, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sleep(oway: Path, team: str) -> None:
    _team(team)
    a = awake(oway)
    a.pop(team, None)
    _awake_path(oway).parent.mkdir(parents=True, exist_ok=True)
    _awake_path(oway).write_text(json.dumps(a, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _team(team: str) -> None:
    if team not in TEAMS:
        raise OwayError(f"unknown team '{team}' ({', '.join(TEAMS)})")


def findings(oway: Path) -> list[dict]:
    out = []
    for f in sorted((kdir(oway) / "notes").glob("F-*.md")):
        text = f.read_text(encoding="utf-8")
        m = NOTE.search(text)
        if not m:
            continue
        team = re.search(r"^team: (\S+)$", text, re.M)
        resolved = re.search(r"^RESOLVED (\S+) \| (.*)$", text, re.M)
        rejected = re.search(r"^REJECTED (\S+) \| (.*)$", text, re.M)
        state = "resolved" if resolved else ("rejected" if rejected else "open")
        out.append({"id": f.stem, "type": m.group(1), "fact": m.group(2), "proof": m.group(3),
                    "since": m.group(4), "team": team.group(1) if team else "?", "state": state})
    return out


def _one_line(text: str) -> str:
    return " ".join(text.split()).replace("|", "/")


def note(oway: Path, team: str, kind: str, fact: str, proof_text: str) -> tuple[str, bool]:
    """Write a finding. Returns (id, is_new). A known open finding is not sent again."""
    _team(team)
    kind = kind.upper()
    if kind not in TYPES:
        raise OwayError(f"unknown finding type '{kind}'")
    if team not in awake(oway) and kind not in {"TAMPER", "SYSTEM"}:
        raise OwayError(f"Keeper{team.capitalize()} is asleep: its team is not working")
    fact, proof_text = _one_line(fact), _one_line(proof_text)
    if not fact or not proof_text:
        raise OwayError("a finding needs a fact and a proof")
    for f in findings(oway):
        if f["state"] == "open" and (f["team"], f["type"], f["fact"]) == (team, kind, fact):
            return f["id"], False
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    notes = kdir(oway) / "notes"
    notes.mkdir(parents=True, exist_ok=True)
    while True:
        fid = f"F-{day}-{secrets.token_hex(2)}"
        if not (notes / f"{fid}.md").exists():
            break
    (notes / f"{fid}.md").write_text(
        f"# {fid}\nteam: {team}\n\nFINDING {kind} | {fact} | PROOF: {proof_text} | SINCE: {ledger.now()}\n",
        encoding="utf-8")
    write_index(oway)
    return fid, True


def resolve(oway: Path, fid: str, how: str) -> None:
    path = kdir(oway) / "notes" / f"{fid}.md"
    if not path.exists():
        raise OwayError(f"no finding {fid}")
    text = path.read_text(encoding="utf-8")
    if "\nRESOLVED " in text:
        raise OwayError(f"{fid} is already resolved")
    path.write_text(text + f"RESOLVED {ledger.now()} | {_one_line(how) or 'fixed'}\n", encoding="utf-8")
    write_index(oway)


def write_index(oway: Path) -> None:
    rows = [f"| [{f['id']}](notes/{f['id']}.md) | {f['type']} | {f['team']} | {f['state']} | {f['since']} |"
            for f in findings(oway)]
    kdir(oway).mkdir(parents=True, exist_ok=True)
    (kdir(oway) / "INDEX.md").write_text(
        "# Keeper index\nWritten by `oway keeper`. Read it before sending a finding.\n\n"
        "| id | type | team | state | since |\n| --- | --- | --- | --- | --- |\n"
        + "".join(r + "\n" for r in rows), encoding="utf-8")


def owner_message(f: dict) -> str:
    """The message to the owner: at most 200 characters, title + fact + one proof, no paths."""
    clean = lambda s: " ".join(PATHLIKE.sub("", s).split())
    msg = f"[{f['type']}] {clean(f['fact'])}. Proof: {clean(f['proof'])}"
    return msg if len(msg) <= OWNER_MAX else msg[:OWNER_MAX - 3].rstrip() + "..."


def _verify_evidence_seq(oway: Path, seq: int) -> bool:
    ev_dir = oway / "evidence"
    if not ev_dir.is_dir():
        return False
    for f in sorted(ev_dir.glob("*.jsonl")):
        try:
            chain = proof.read_chain(oway, f.stem)
        except proof.TamperError:
            continue
        if any(r.get("seq") == seq for r in chain):
            return True
    return False


def _verify_proof(oway: Path, kind: str, proof_text: str, timeout: int = 30) -> bool:
    """Replay or verify a finding's proof read-only; returns True only when confirmed."""
    root = oway.parent
    text = proof_text.strip()
    if not text:
        return False
    if text.startswith("cmd:"):
        cmd_str = text[4:].strip()
        if not cmd_str:
            return False
        try:
            r = subprocess.run(cmd_str, shell=True, cwd=root, capture_output=True, text=True, timeout=timeout)
            return r.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False
    if text.startswith("oway "):
        try:
            argv = [sys.executable, str(OWAY_BIN), "--root", str(root), *shlex.split(text)[1:]]
            r = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=timeout)
            return r.returncode == (3 if kind == "TAMPER" else 0)
        except (ValueError, OSError, subprocess.SubprocessError):
            return False
    m_ev = re.search(r"\bevidence\s+seq\s+(\d+)\b", text, re.I)
    if m_ev:
        return _verify_evidence_seq(oway, int(m_ev.group(1)))
    m_led = re.search(r"\b(L-\d{8}-\d+)\b", text)
    if m_led:
        lp = oway / "LEDGER.md"
        return lp.is_file() and m_led.group(1) in lp.read_text(encoding="utf-8")
    try:
        tokens = shlex.split(text)
    except ValueError:
        tokens = []
    if tokens and tokens[0] in CMD_TOKENS:
        try:
            r = subprocess.run(tokens, cwd=root, capture_output=True, text=True, timeout=timeout)
            return r.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False
    m_path = PATHLIKE.search(text)
    if m_path:
        rel_p = m_path.group(0).split(":", 1)[0].strip("`'\".,)")
        cand = (root / rel_p).resolve()
        return cand.is_file() and (cand == root.resolve() or root.resolve() in cand.parents)
    return False


def replay(oway: Path, fid: str, timeout: int = 30) -> tuple[bool, str]:
    """LeadKeeper proof replay: mark REJECTED if unconfirmed, else emit neutral [KEEPER] warning."""
    path = kdir(oway) / "notes" / f"{fid}.md"
    if not path.exists():
        raise OwayError(f"no finding {fid}")
    text = path.read_text(encoding="utf-8")
    m = NOTE.search(text)
    if not m:
        raise OwayError(f"finding {fid} has no FINDING line")
    kind, fact, proof_text, since = m.group(1), m.group(2), m.group(3), m.group(4)
    if not _verify_proof(oway, kind, proof_text, timeout=timeout):
        if "\nREJECTED " not in text:
            path.write_text(text + f"REJECTED {ledger.now()} | proof not confirmed\n", encoding="utf-8")
            write_index(oway)
        return False, f"REJECTED {fid}: proof not confirmed"
    if "\nCONFIRMED " not in text:
        path.write_text(text + f"CONFIRMED {ledger.now()} | proof replayed\n", encoding="utf-8")
        write_index(oway)
    return True, f"[KEEPER] {kind} | {fact} | PROOF: {proof_text} | SINCE: {since}"


def check_work_class(oway: Path, team: str = "dev") -> list[tuple[str, bool]]:
    """Emit DRIFT when checkpoint.json records unapproved SIDE or HARDENING work."""
    cp = oway / "state" / "checkpoint.json"
    if not cp.is_file() or team not in awake(oway):
        return []
    try:
        data = json.loads(cp.read_text(encoding="utf-8"))
    except ValueError:
        return []
    wc = str(data.get("work_class") or "").upper()
    if wc not in {"SIDE", "HARDENING"}:
        return []
    if data.get("approved") or data.get("work_class_approved"):
        return []
    sid = data.get("slice") or "active-slice"
    return [note(oway, team, "DRIFT", f"unapproved {wc} work on {sid}", "_oway/state/checkpoint.json")]


def scan(oway: Path) -> list[tuple[str, bool]]:
    """Findings a script can prove: TAMPER, BLOCKED/pivot LOOP, FAKE_PROOF, unapproved work-class DRIFT."""
    out = check_work_class(oway)
    is_dev_awake = "dev" in awake(oway)
    for m in sorted((oway / "slices").glob("*.matrix.md")) if (oway / "slices").is_dir() else []:
        sid = m.name[: -len(".matrix.md")]
        try:
            digest, items = proof._frozen_items(oway, sid)
            st = proof.states(oway, sid, digest, items)
        except proof.TamperError as exc:
            out.append(note(oway, "dev", "TAMPER", str(exc), f"oway check {sid}"))
            continue
        except OwayError:
            continue
        if not is_dev_awake:
            continue
        for iid, s in st.items():
            if s["state"] == "BLOCKED":
                out.append(note(oway, "dev", "LOOP",
                                f"{sid} {iid} failed {s['rounds']} rounds",
                                f"evidence seq {s['last']['seq']}: {s['last']['reason']}"))
            elif s["state"] == "FAKE":
                out.append(note(oway, "dev", "FAKE_PROOF",
                                f"{sid} {iid} produced fake or mocked proof",
                                f"evidence seq {s['last']['seq']}: {s['last']['reason']}"))
            elif s.get("pivot_required"):
                out.append(note(oway, "dev", "LOOP",
                                f"{sid} {iid} hit 2 consecutive identical failures (PIVOT_REQUIRED)",
                                f"evidence seq {s['last']['seq']}: {s['last']['reason']}"))
    return out


def report(oway: Path) -> Path:
    """LeadKeeper's full report of the open findings."""
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H")
    path = kdir(oway) / "reports" / f"{stamp}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    open_f = [f for f in findings(oway) if f["state"] == "open"]
    lines = [f"# Keeper report {stamp}", f"Open findings: {len(open_f)}. Awake: "
             f"{', '.join(sorted(awake(oway))) or 'none'}.", ""]
    lines += [f"- {f['id']} {f['type']} ({f['team']}): {f['fact']}. Proof: {f['proof']}" for f in open_f]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
