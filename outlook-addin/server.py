import http.server
import ssl
from functools import partial

HOST = "localhost"
PORT = 3000

CERT_FILE = r"C:\Users\HADIPUTRA\.office-addin-dev-certs\localhost.crt"
KEY_FILE = r"C:\Users\HADIPUTRA\.office-addin-dev-certs\localhost.key"

DIRECTORY = r"C:\xampp\htdocs\ShipCheck-AI\outlook-addin"

handler = partial(
    http.server.SimpleHTTPRequestHandler,
    directory=DIRECTORY,
)

server = http.server.ThreadingHTTPServer(
    (HOST, PORT),
    handler,
)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

context.load_cert_chain(
    certfile=CERT_FILE,
    keyfile=KEY_FILE,
)

server.socket = context.wrap_socket(
    server.socket,
    server_side=True,
)

print(f"ShipCheck AI HTTPS server running at https://{HOST}:{PORT}")
print("Press Ctrl+C to stop.")

server.serve_forever()
