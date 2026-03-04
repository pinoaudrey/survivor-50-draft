#!/usr/bin/env python3
"""
Local dev server for Survivor 50 Fantasy Draft.
Serves static files AND handles POST endpoints to write data files.
Run: python3 server.py
"""
import http.server
import json
import os
import sys

PORT = 8765
ROOT = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        if self.path == "/save-leagues":
            try:
                parsed = json.loads(body)
                out_path = os.path.join(ROOT, "data", "leagues.json")
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=2)
                self._respond(200, {"ok": True})
            except Exception as e:
                self._respond(400, {"ok": False, "error": str(e)})

        elif self.path == "/save-week-csv":
            try:
                # Expect JSON body: { "week": 1, "csv": "...csv text..." }
                payload = json.loads(body)
                week = int(payload["week"])
                csv_text = payload["csv"]
                out_path = os.path.join(ROOT, "data", f"week_{week}.csv")
                with open(out_path, "w", encoding="utf-8", newline="") as f:
                    f.write(csv_text)
                print(f"  → Saved data/week_{week}.csv")
                self._respond(200, {"ok": True, "filename": f"week_{week}.csv"})
            except Exception as e:
                self._respond(400, {"ok": False, "error": str(e)})

        elif self.path == "/save-quiz-response":
            try:
                response = json.loads(body)
                quiz_path = os.path.join(ROOT, "data", "quiz.json")
                # Load existing or init
                if os.path.exists(quiz_path):
                    with open(quiz_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = {"responses": [], "correctAnswers": None}
                # Check for duplicate name (case-insensitive)
                name = response.get("name", "").strip().lower()
                if any(r.get("name", "").strip().lower() == name for r in data["responses"]):
                    self._respond(409, {"ok": False, "error": "Name already submitted"})
                    return
                data["responses"].append(response)
                with open(quiz_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print(f"  → Quiz response saved: {response.get('name', '?')}")
                self._respond(200, {"ok": True})
            except Exception as e:
                self._respond(400, {"ok": False, "error": str(e)})

        elif self.path == "/save-quiz-answers":
            try:
                correct_answers = json.loads(body)  # may be null
                quiz_path = os.path.join(ROOT, "data", "quiz.json")
                if os.path.exists(quiz_path):
                    with open(quiz_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = {"responses": [], "correctAnswers": None}
                data["correctAnswers"] = correct_answers
                with open(quiz_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print(f"  → Quiz correct answers {'cleared' if correct_answers is None else 'saved'}")
                self._respond(200, {"ok": True})
            except Exception as e:
                self._respond(400, {"ok": False, "error": str(e)})

        else:
            self._respond(404, {"ok": False, "error": "Not found"})

    def _respond(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # Suppress noisy GET logs, only show POSTs and errors
        if args and (str(args[1]) not in ("200", "304") or self.path == "/save-leagues"):
            super().log_message(fmt, *args)


if __name__ == "__main__":
    os.chdir(ROOT)
    print(f"🏝️  Survivor Draft server running at http://localhost:{PORT}")
    print(f"   Serving: {ROOT}")
    print(f"   Auto-save: POST /save-leagues       → data/leagues.json")
    print(f"   Auto-save: POST /save-week-csv      → data/week_N.csv")
    print(f"   Quiz:      POST /save-quiz-response → data/quiz.json (append)")
    print(f"   Quiz:      POST /save-quiz-answers  → data/quiz.json (set answers)")
    print(f"   Stop: Ctrl+C\n")
    try:
        with http.server.HTTPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
