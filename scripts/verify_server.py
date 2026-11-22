import socket
import ssl
import sys
import urllib.error
import urllib.request

if len(sys.argv) != 2:
    print(f"Usage: python3 {sys.argv[0]} <host>")
    sys.exit(1)

HOST = sys.argv[1]

for port in (22, 80, 443):
    try:
        with socket.create_connection((HOST, port), timeout=3):
            print(f"[PASS] Port {port} is open on {HOST}")
    except socket.error as e:
        print(f"[FAIL] Port {port} is closed on {HOST}: {e}")
        sys.exit(1)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


try:
    urllib.request.build_opener(NoRedirect).open(f"http://{HOST}", timeout=3)
except urllib.error.HTTPError as err:
    assert err.code == 301, f"Expected 301, got {err.code}"
    print(f"[PASS] HTTP 80 redirects to {err.headers.get('Location')}")
else:
    raise AssertionError("Expected HTTP 301 redirect, got 200")


ctx = ssl._create_unverified_context()
with urllib.request.urlopen(f"https://{HOST}", context=ctx, timeout=3) as resp:
    assert resp.status == 200
    print(f"[PASS] HTTPS 443 returned 200: {resp.read().decode().strip()}")