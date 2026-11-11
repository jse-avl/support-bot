"""Run the eval set against the chat endpoint and write evals/report.md.

Each case starts a fresh session. Checks (only those a case defines):
  - expect_source:     at least one cited source comes from this KB file
  - must_include:      every string appears in the final answer (case-insensitive)
  - must_not_include:  none of these strings appear in the answer
  - expect_escalation: final turn escalated == this value (null = don't check)

Usage:
    python evals/run_evals.py [--url http://127.0.0.1:5678/webhook/chat] [--delay 6]
"""
import argparse
import json
import pathlib
import statistics
import time
import urllib.request
import uuid

HERE = pathlib.Path(__file__).resolve().parent


def ask(url, session_id, message, timeout=120):
    body = json.dumps({"session_id": session_id, "message": message}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))
    return data, (time.perf_counter() - t0) * 1000


def check(case, reply):
    answer = (reply.get("answer") or "").lower()
    sources = reply.get("sources") or []
    failures = []
    if case.get("expect_source") and not any(s.startswith(case["expect_source"]) for s in sources):
        failures.append(f"source {case['expect_source']} not cited (got {sources})")
    for s in case.get("must_include", []):
        if s.lower() not in answer:
            failures.append(f"missing '{s}'")
    for s in case.get("must_not_include", []):
        if s.lower() in answer:
            failures.append(f"contains forbidden '{s}'")
    exp = case.get("expect_escalation")
    if exp is not None and bool(reply.get("escalated")) != exp:
        failures.append(f"escalated={reply.get('escalated')} expected {exp}")
    return failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:5678/webhook/chat")
    ap.add_argument("--delay", type=float, default=6.0, help="seconds between calls (free-tier per-minute limits)")
    a = ap.parse_args()

    cases = [json.loads(l) for l in (HERE / "cases.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    results, latencies = [], []
    for case in cases:
        session = f"eval-{case['id'][:40]}-{uuid.uuid4().hex[:6]}"
        reply, failures = {}, []
        try:
            for turn in case["turns"]:
                reply, ms = ask(a.url, session, turn)
                latencies.append(ms)
                time.sleep(a.delay)
            failures = check(case, reply)
        except Exception as e:  # network/timeout: count as a failure, keep going
            failures = [f"error: {e}"]
        ok = not failures
        results.append((case, reply, failures))
        print(f"{'PASS' if ok else 'FAIL'}  {case['id']}" + ("" if ok else f"  -> {'; '.join(failures)}"))

    passed = sum(1 for _, _, f in results if not f)
    p95 = statistics.quantiles(latencies, n=20)[-1] if len(latencies) >= 2 else (latencies or [0])[0]
    lines = [
        "# Eval report",
        "",
        f"- Date: {time.strftime('%Y-%m-%d %H:%M')}",
        f"- Cases: {len(results)} | **Passed: {passed} ({100 * passed / len(results):.0f}%)**",
        f"- Latency per turn: median {statistics.median(latencies):.0f} ms, p95 {p95:.0f} ms" if latencies else "",
        "",
        "| Case | Result | Escalated | Sources | Notes |",
        "|---|---|---|---|---|",
    ]
    for case, reply, failures in results:
        lines.append("| {} | {} | {} | {} | {} |".format(
            case["id"], "✅" if not failures else "❌", reply.get("escalated", "—"),
            ", ".join(reply.get("sources") or []) or "—",
            "; ".join(failures).replace("|", "/") or ""))
    (HERE / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n{passed}/{len(results)} passed -> evals/report.md")


if __name__ == "__main__":
    main()
