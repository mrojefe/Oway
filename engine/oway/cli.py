"""Command line: python3 engine/oway <command> ...

Exit codes: 0 ok, 1 check failed, 2 usage or setup error, 3 tamper.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import doctor, feedback, githeaders, guard, index, keeper, ledger, proof, setup, review, stophook, takeover, upgrade
from .project import OwayError, find_root


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="oway", description="Oway tool (method v0.4).")
    p.add_argument("--root", type=Path, help="project folder (default: search up from here)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("index", help="rebuild every INDEX.md under _oway/")
    s.add_argument("--check", action="store_true", help="only report stale indexes (for CI)")
    s = sub.add_parser("headers", help="fill created and updated in headers from Git")
    s.add_argument("--check", action="store_true")
    sub.add_parser("doctor", help="check headers, links, config and indexes")
    s = sub.add_parser("ledger", help="append one line to LEDGER.md")
    s.add_argument("text")
    s.add_argument("--who", default="oway")

    s = sub.add_parser("freeze", help="freeze an approved proof matrix")
    s.add_argument("slice")
    s = sub.add_parser("submit", help="run the verifier of one proof item")
    s.add_argument("slice")
    s.add_argument("item")
    s.add_argument("--timeout", type=int, default=600)
    s = sub.add_parser("review", help="run the reviewer on an item waiting for review")
    s.add_argument("slice")
    s.add_argument("item")
    s = sub.add_parser("check", help="exit 0 only when every item is PASS")
    s.add_argument("slice")
    s.add_argument("--head", action="store_true", help="every PASS must be at the current commit")

    sub.add_parser("guard", help="pre-tool hook: deny builder writes outside its zone (reads stdin)")
    s = sub.add_parser("stop-hook", help="builder stop hook (reads the host payload on stdin)")
    s.add_argument("--format", choices=("claude", "plain"), default="claude")

    _keeper_parser(sub)
    pl = sub.add_parser("platform", help="the owner's shared setup").add_subparsers(dest="pcmd", required=True)
    pl.add_parser("init").add_argument("--dir", type=Path)
    s = sub.add_parser("setup", help="create _oway/ for a new project")
    s.add_argument("--language", default="en")
    s.add_argument("--builder", action="append", default=[], help="DevBackend, DevData...")
    s.add_argument("--no-uix", action="store_true")
    s.add_argument("--platform", type=Path)
    s.add_argument("--claude-hook", action="store_true", help="add the Stop hook to .claude/settings.json")
    s = sub.add_parser("upgrade", help="move the project to this tool's version")
    s.add_argument("--dry-run", action="store_true")
    s = sub.add_parser("takeover", help="move a CGSpec 0.3 project into _oway/")
    s.add_argument("--from", dest="source", choices=("cgspec-0.3",), required=True)
    s.add_argument("--language", default="en")
    s.add_argument("--dry-run", action="store_true")
    s = sub.add_parser("feedback", help="draft an issue for the Oway repo (never sends it)")
    s.add_argument("title")
    s.add_argument("--body", default="")
    s = sub.add_parser("install-hook", help="install the builder stop hook for a host")
    s.add_argument("--host", choices=("claude", "pi"), default="claude")
    sub.add_parser("version")
    return p


def _keeper_parser(sub) -> None:
    k = sub.add_parser("keeper", help="keeper watcher files").add_subparsers(dest="kcmd", required=True)
    for name in ("wake", "sleep"):
        k.add_parser(name).add_argument("team")
    n = k.add_parser("note")
    n.add_argument("team")
    n.add_argument("type")
    n.add_argument("fact")
    n.add_argument("--proof", required=True)
    r = k.add_parser("resolve")
    r.add_argument("id")
    r.add_argument("how")
    k.add_parser("scan")
    k.add_parser("status")
    k.add_parser("report")
    m = k.add_parser("owner-message")
    m.add_argument("id")



def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return _run(args)
    except proof.TamperError as exc:
        print(exc, file=sys.stderr)
        return 3
    except OwayError as exc:
        print(f"oway: {exc}", file=sys.stderr)
        return 2


def _run(args) -> int:
    if args.cmd == "version":
        print(setup.VERSION_FILE.read_text().strip())
        return 0
    if args.cmd == "platform":
        path = args.dir or setup.default_platform()
        made = setup.platform_init(path)
        print(f"platform {path}: " + (", ".join(made) + " created" if made else "already set"))
        return 0
    if args.cmd == "takeover":
        root = (args.root or Path(".")).resolve()
        print("\n".join(takeover.run(root, args.language, args.dry_run)))
        return 0
    if args.cmd == "setup":
        root = (args.root or Path(".")).resolve()
        for line in setup.project_setup(root, args.language, args.builder, not args.no_uix,
                                        args.platform, args.claude_hook):
            print(line)
        return 0

    root = find_root(args.root)
    oway = root / "_oway"
    if args.cmd == "index":
        stale = index.build(oway, check=args.check)
        for p in stale:
            print(("stale " if args.check else "wrote ") + p.relative_to(root).as_posix())
        return 1 if args.check and stale else 0
    if args.cmd == "headers":
        stale = githeaders.run(root, args.check)
        for name in stale:
            print(("stale " if args.check else "wrote ") + name)
        return 1 if args.check and stale else 0
    if args.cmd == "doctor":
        problems = doctor.run(root)
        for line in problems:
            print("FAIL " + line)
        print("doctor: ok" if not problems else f"doctor: {len(problems)} problems")
        return 1 if problems else 0
    if args.cmd == "ledger":
        print(ledger.append(oway, args.text, args.who))
        return 0
    if args.cmd in ("freeze", "submit", "review", "check"):
        return _proof_cmd(args, root)
    if args.cmd == "stop-hook":
        code, out, err = stophook.main(root, sys.stdin.read() if not sys.stdin.isatty() else "", args.format)
        sys.stdout.write(out)
        sys.stderr.write(err)
        return code
    if args.cmd == "keeper":
        return _keeper(args, oway)
    if args.cmd == "guard":
        sys.stdout.write(guard.pre_tool(root, sys.stdin.read() if not sys.stdin.isatty() else ""))
        return 0
    if args.cmd in ("upgrade", "feedback", "install-hook"):
        return _project_cmd(args, root)
    raise OwayError(f"unknown command {args.cmd}")


def _proof_cmd(args, root: Path) -> int:
    if args.cmd == "freeze":
        print(proof.freeze(root / "_oway", args.slice))
        return 0
    if args.cmd == "submit":
        rec = proof.submit(root, args.slice, args.item, args.timeout)
        print(f"{args.item} {rec['verdict']}: {rec['reason']}")
        return 0 if rec["verdict"] == "PASS" else 1
    if args.cmd == "review":
        rec = review.run(root, args.slice, args.item)
        print(f"{args.item} review {rec['verdict']}: {rec['reason']}")
        return 0 if rec["verdict"] == "PASS" else 1
    if args.cmd == "check":
        ok, lines = proof.check(root, args.slice, args.head)
        print("\n".join(lines))
        return 0 if ok else 1
    raise OwayError(f"unknown command {args.cmd}")


def _project_cmd(args, root: Path) -> int:
    if args.cmd == "upgrade":
        print("\n".join(upgrade.run(root, setup.VERSION_FILE.read_text().strip(), args.dry_run)))
    elif args.cmd == "feedback":
        path, url, cmd = feedback.create(root / "_oway", args.title, args.body)
        print(f"saved {path.relative_to(root).as_posix()}\nopen: {url}\nor: {cmd}")
    elif args.host == "pi":
        print(setup.install_pi_extension(root))
    else:
        print(setup.install_claude_stop_hook(root))
    return 0


def _keeper(args, oway: Path) -> int:
    c = args.kcmd
    if c == "wake":
        keeper.wake(oway, args.team)
    elif c == "sleep":
        keeper.sleep(oway, args.team)
    elif c == "note":
        fid, new = keeper.note(oway, args.team, args.type, args.fact, args.proof)
        print(f"{fid} {'new' if new else 'known, not sent again'}")
    elif c == "resolve":
        keeper.resolve(oway, args.id, args.how)
    elif c == "scan":
        for fid, new in keeper.scan(oway):
            print(f"{fid} {'new' if new else 'known'}")
    elif c == "status":
        open_f = [f for f in keeper.findings(oway) if f["state"] == "open"]
        print(f"awake: {', '.join(sorted(keeper.awake(oway))) or 'none'}; open findings: {len(open_f)}")
    elif c == "report":
        print(keeper.report(oway).relative_to(oway.parent).as_posix())
    elif c == "owner-message":
        f = next((x for x in keeper.findings(oway) if x["id"] == args.id), None)
        if f is None:
            raise OwayError(f"no finding {args.id}")
        print(keeper.owner_message(f))
    return 0
