import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from app import analyze_bug_description, get_driver, import_demo_data


HOST = "127.0.0.1"
PORT = 8000
MAX_REQUEST_BYTES = 20000


def make_handler(driver):
    class BugHandler(BaseHTTPRequestHandler):
        def send_json(self, status, payload):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path != "/":
                self.send_error(404)
                return
            body = Path(__file__).with_name("index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if self.path != "/api/analyze":
                self.send_error(404)
                return

            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > MAX_REQUEST_BYTES:
                    self.send_json(413, {"error": "Please submit a description under 20 KB."})
                    return
                request = json.loads(self.rfile.read(length).decode("utf-8"))
                description = request.get("description", "").strip()
                if not description:
                    self.send_json(400, {"error": "Enter a description of the bug first."})
                    return
                result = analyze_bug_description(driver, description)
                self.send_json(200, result)
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError, TypeError):
                self.send_json(400, {"error": "The request was not valid JSON."})
            except Exception as exc:
                self.send_json(500, {"error": str(exc)})

        def log_message(self, format, *args):
            print(f"UI: {format % args}")

    return BugHandler


def main():
    driver = get_driver()
    server = None
    try:
        print("Checking Neo4j data...")
        import_demo_data(driver)
        server = ThreadingHTTPServer((HOST, PORT), make_handler(driver))
        url = f"http://{HOST}:{PORT}"
        print(f"Smashing Bugs UI is ready at {url} (press Ctrl+C to stop).")
        webbrowser.open(url)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping the UI.")
    finally:
        if server is not None:
            server.server_close()
        driver.close()


if __name__ == "__main__":
    main()
