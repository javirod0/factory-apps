#!/usr/bin/env python3
"""
Emisor de eventos de la fábrica.

Append-only a events.jsonl. Sin dependencias, sin red, sin servidor.

Uso desde línea de comandos:

    emit.py run-start   --task T-142 --actor implementer --model claude-fable-5-1
    emit.py run-end     --run r_01H --task T-142 --actor implementer \\
                        --outcome success --duration 412 \\
                        --input-tokens 184300 --output-tokens 12400 \\
                        --cache-read 920000 --cost 2.87
    emit.py state       --task T-142 --from in_progress --to in_review
    emit.py handoff     --task T-142 --from-actor implementer --to-actor reviewer \\
                        --reason "tests en verde" --artifact "PR #38"
    emit.py wait-start  --task T-142 --on po --gate uat \\
                        --question "¿Apruebas el UAT de guardar-para-mí?"
    emit.py wait-end    --task T-142 --on po --resolution aprobado
    emit.py blocked     --task T-142 --kind spec_gap --detail "..."
    emit.py unblocked   --task T-142
    emit.py gate        --task T-142 --gate security_review --result blocked \\
                        --severity HIGH --detail "C1: policy UPDATE sin SELECT"
    emit.py intervene   --task T-142 --what-failed "..." --should-have-been mobile-platform \\
                        --gap-type skill --minutes 45

Uso como librería:

    from emit import Emitter
    e = Emitter(task="T-142", slice_="save-for-myself", phase="implement",
                actor="implementer")
    run = e.run_start(model="claude-fable-5-1")
    ...
    e.run_end(run, outcome="success", duration_s=412, cost_usd=2.87)

Contexto por defecto vía entorno, para no repetirlo en cada llamada:
    FACTORY_TASK, FACTORY_SLICE, FACTORY_PHASE, FACTORY_ACTOR, FACTORY_EVENTS
"""

import argparse
import json
import os
import secrets
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PATH = "factory/observability/events.jsonl"

VALID_PHASES = {"brainstorm", "specify", "plan", "tasks", "analyze",
                "implement", "review", "uat", "release"}
VALID_OUTCOMES = {"success", "failed", "blocked", "abandoned"}
VALID_GAPS = {"skill", "roster", "spec", "tooling"}
VALID_BLOCK_KINDS = {"dependency", "spec_gap", "tooling", "external",
                     "unclear_requirement"}


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rid():
    return "r_" + secrets.token_hex(8)


def _warn(msg):
    print(f"emit: aviso: {msg}", file=sys.stderr)


class Emitter:
    """Escribe eventos. Nunca lanza al llamante: perder un evento no debe
    tumbar el trabajo real. Los problemas van a stderr."""

    def __init__(self, path=None, task=None, slice_=None, phase=None,
                 actor=None, actor_type="agent"):
        self.path = Path(path or os.environ.get("FACTORY_EVENTS", DEFAULT_PATH))
        self.task = task or os.environ.get("FACTORY_TASK")
        self.slice = slice_ or os.environ.get("FACTORY_SLICE")
        self.phase = phase or os.environ.get("FACTORY_PHASE")
        self.actor = actor or os.environ.get("FACTORY_ACTOR")
        self.actor_type = actor_type

    # ---------- núcleo ----------

    def emit(self, event, **fields):
        rec = {
            "ts": _now(),
            "event": event,
            "task_id": self.task,
            "slice": self.slice,
            "phase": self.phase,
            "actor": self.actor,
            "actor_type": self.actor_type,
        }
        rec.update(fields)
        rec = {k: v for k, v in rec.items() if v is not None}

        if rec.get("phase") and rec["phase"] not in VALID_PHASES:
            _warn(f"fase desconocida '{rec['phase']}'")

        line = json.dumps(rec, ensure_ascii=False)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            # append en modo texto es atómico para líneas cortas en POSIX
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception as exc:                       # noqa: BLE001
            _warn(f"no se pudo escribir el evento: {exc}\n  {line}")
        return rec

    # ---------- ejecuciones ----------

    def run_start(self, run_id=None, model=None, effort=None, input_ref=None):
        run_id = run_id or _rid()
        self.emit("run.started", run_id=run_id, model=model, effort=effort,
                  input=input_ref)
        return run_id

    def run_end(self, run_id, outcome="success", duration_s=None,
                input_tokens=None, output_tokens=None, cache_read=None,
                cost_usd=None, files_changed=None):
        if outcome not in VALID_OUTCOMES:
            _warn(f"outcome desconocido '{outcome}'")
        tokens = {k: v for k, v in {
            "input": input_tokens, "output": output_tokens,
            "cache_read": cache_read,
        }.items() if v is not None} or None
        if cost_usd is None:
            _warn("run.finished sin cost_usd: el cockpit no podrá atribuir "
                  "coste a este agente")
        return self.emit("run.finished", run_id=run_id, outcome=outcome,
                         duration_s=duration_s, tokens=tokens,
                         cost_usd=cost_usd, files_changed=files_changed)

    # ---------- tareas ----------

    def state_changed(self, from_state, to_state, time_in_previous_s=None):
        return self.emit("task.state_changed", **{"from": from_state,
                                                  "to": to_state},
                         time_in_previous_s=time_in_previous_s)

    def handoff(self, from_actor, to_actor, reason=None, artifact=None):
        ev = self.emit("handoff", from_actor=from_actor, to_actor=to_actor,
                       reason=reason, artifact=artifact)
        if to_actor in ("po", "designer"):
            _warn(f"handoff a '{to_actor}': emite también wait-start, o el "
                  "cockpit no sabrá que hay un humano bloqueando")
        return ev

    # ---------- esperas ----------

    def wait_start(self, waiting_on, question=None, gate=None, blocking=True):
        if waiting_on in ("po", "designer") and not question:
            _warn("wait-start a un humano sin --question: una petición vaga se "
                  "convierte en una revisión que el humano tiene que inventar")
        return self.emit("waiting.started", waiting_on=waiting_on,
                         question=question, gate=gate, blocking=blocking)

    def wait_end(self, waiting_on, waited_s=None, resolution=None):
        return self.emit("waiting.ended", waiting_on=waiting_on,
                         waited_s=waited_s, resolution=resolution)

    # ---------- bloqueos ----------

    def blocked(self, kind, detail=None, blocked_by_task=None):
        if kind not in VALID_BLOCK_KINDS:
            _warn(f"kind de bloqueo desconocido '{kind}'")
        if kind in ("spec_gap", "unclear_requirement"):
            _warn(f"bloqueo por '{kind}': la spec falló, no el agente. "
                  "Considera emitir también una intervención.")
        return self.emit("blocked", kind=kind, detail=detail,
                         blocked_by_task=blocked_by_task)

    def unblocked(self, detail=None):
        return self.emit("unblocked", detail=detail)

    # ---------- gates ----------

    def gate(self, gate, result, severity=None, detail=None):
        return self.emit("gate.evaluated", gate=gate, result=result,
                         severity=severity, detail=detail)

    # ---------- intervenciones ----------

    def intervention(self, what_failed, should_have_been=None,
                     gap_type=None, minutes_spent=None):
        if gap_type and gap_type not in VALID_GAPS:
            _warn(f"gap_type desconocido '{gap_type}'")
        return self.emit("intervention", actor_type="human",
                         what_failed=what_failed,
                         should_have_been=should_have_been,
                         gap_type=gap_type, minutes_spent=minutes_spent)


# ---------------------------------------------------------------- CLI

def _common(p):
    p.add_argument("--task")
    p.add_argument("--slice")
    p.add_argument("--phase")
    p.add_argument("--actor")
    p.add_argument("--events")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Emisor de eventos de la fábrica")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("run-start"); _common(p)
    p.add_argument("--run"); p.add_argument("--model")
    p.add_argument("--effort"); p.add_argument("--input-ref")

    p = sub.add_parser("run-end"); _common(p)
    p.add_argument("--run", required=True)
    p.add_argument("--outcome", default="success")
    p.add_argument("--duration", type=int)
    p.add_argument("--input-tokens", type=int)
    p.add_argument("--output-tokens", type=int)
    p.add_argument("--cache-read", type=int)
    p.add_argument("--cost", type=float)
    p.add_argument("--files-changed", type=int)

    p = sub.add_parser("state"); _common(p)
    p.add_argument("--from", dest="from_state", required=True)
    p.add_argument("--to", dest="to_state", required=True)
    p.add_argument("--time-in-previous", type=int)

    p = sub.add_parser("handoff"); _common(p)
    p.add_argument("--from-actor", required=True)
    p.add_argument("--to-actor", required=True)
    p.add_argument("--reason"); p.add_argument("--artifact")

    p = sub.add_parser("wait-start"); _common(p)
    p.add_argument("--on", dest="waiting_on", required=True)
    p.add_argument("--question"); p.add_argument("--gate")

    p = sub.add_parser("wait-end"); _common(p)
    p.add_argument("--on", dest="waiting_on", required=True)
    p.add_argument("--waited", type=int); p.add_argument("--resolution")

    p = sub.add_parser("blocked"); _common(p)
    p.add_argument("--kind", required=True)
    p.add_argument("--detail"); p.add_argument("--blocked-by")

    p = sub.add_parser("unblocked"); _common(p)
    p.add_argument("--detail")

    p = sub.add_parser("gate"); _common(p)
    p.add_argument("--gate", required=True)
    p.add_argument("--result", required=True)
    p.add_argument("--severity"); p.add_argument("--detail")

    p = sub.add_parser("intervene"); _common(p)
    p.add_argument("--what-failed", required=True)
    p.add_argument("--should-have-been")
    p.add_argument("--gap-type")
    p.add_argument("--minutes", type=int)

    a = ap.parse_args(argv)
    e = Emitter(path=a.events, task=a.task, slice_=a.slice,
                phase=a.phase, actor=a.actor)

    if a.cmd == "run-start":
        print(e.run_start(a.run, a.model, a.effort, a.input_ref))
        return
    if a.cmd == "run-end":
        e.run_end(a.run, a.outcome, a.duration, a.input_tokens,
                  a.output_tokens, a.cache_read, a.cost, a.files_changed)
    elif a.cmd == "state":
        e.state_changed(a.from_state, a.to_state, a.time_in_previous)
    elif a.cmd == "handoff":
        e.handoff(a.from_actor, a.to_actor, a.reason, a.artifact)
    elif a.cmd == "wait-start":
        e.wait_start(a.waiting_on, a.question, a.gate)
    elif a.cmd == "wait-end":
        e.wait_end(a.waiting_on, a.waited, a.resolution)
    elif a.cmd == "blocked":
        e.blocked(a.kind, a.detail, a.blocked_by)
    elif a.cmd == "unblocked":
        e.unblocked(a.detail)
    elif a.cmd == "gate":
        e.gate(a.gate, a.result, a.severity, a.detail)
    elif a.cmd == "intervene":
        e.intervention(a.what_failed, a.should_have_been, a.gap_type, a.minutes)


if __name__ == "__main__":
    main()
