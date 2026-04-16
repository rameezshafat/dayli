"""
One-time script to get a Google OAuth2 refresh token for Google Calendar access.

Your credentials are already in .env. Before running this script, do ONE thing:

1. Go to https://console.cloud.google.com
2. APIs & Services → Credentials → click your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs" → Add:  http://localhost:8765
4. Click Save

Then run:
    python scripts/google_auth.py

A browser window opens → sign in → grant access.
Copy the printed GOOGLE_REFRESH_TOKEN into your .env file.
"""

import os
import sys
from pathlib import Path

# Load .env file manually so the script works without exporting vars to shell
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())
import urllib.parse
import urllib.request
import webbrowser
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = "http://localhost:8765"
SCOPES = "https://www.googleapis.com/auth/calendar"

auth_code: str | None = None


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        global auth_code
        # accept any path so both /callback and / work
        params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
        auth_code = params.get("code")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h2>Auth complete! You can close this tab.</h2>")

    def log_message(self, *args: object) -> None:
        pass  # suppress request logs


def main() -> None:
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env first.")
        sys.exit(1)

    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urllib.parse.urlencode({
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": SCOPES,
            "access_type": "offline",
            "prompt": "consent",
        })
    )

    print("Opening browser for Google sign-in...")
    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", 8765), _Handler)
    server.handle_request()  # blocks until one request arrives

    if not auth_code:
        print("ERROR: No auth code received.")
        sys.exit(1)

    data = urllib.parse.urlencode({
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }).encode()

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        tokens = json.loads(resp.read())

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        print("ERROR: No refresh token returned. Make sure you set access_type=offline and prompt=consent.")
        sys.exit(1)

    print("\nSuccess! Add this to your .env file:\n")
    print(f"GOOGLE_REFRESH_TOKEN={refresh_token}\n")


if __name__ == "__main__":
    main()
