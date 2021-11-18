from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
import time
from fetchComponent import *
from urllib.parse import urlparse, parse_qs
from tempfile import TemporaryDirectory
import zipfile
import glob
import os.path
import sys
import io

USE_HTTPS = False

def fetch(part):
    with TemporaryDirectory() as dir:
        fetchLcsc_(os.path.join(dir, "JLC.pretty"), True, part, "KIPRJMOD")
        zipdata = io.BytesIO()
        zip = zipfile.ZipFile(zipdata, "w")
        g = glob.glob(os.path.join(dir, "**"), recursive=True)
        for f in g:
            rf = os.path.relpath(f, dir)
            print(f)
            if f.endswith("wrl") or f.endswith("kicad_mod"):
                zip.write(f, rf, compress_type=zipfile.ZIP_DEFLATED)
            #zip.write(g[0])
        zip.close()
        zipdata.seek(0)
        return zipdata.read()

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):


        qs = parse_qs(urlparse(self.path).query)
        part = qs.get('part', None)
        
        if part:
            try:
                part = part[0]
                zipdata = fetch(part)
                self.send_response(200)
                self.send_header('Content-type', 'application/zip')
                self.send_header('Content-Disposition', 'attachment; filename="JLC_{}.zip"'.format(part))
                self.end_headers()
                self.wfile.write(zipdata)
            except Exception as e:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(bytes(str(e), "utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

        #self.wfile.write(b'Hello world\t' + threading.currentThread().getName().encode() + b'\t' + str(threading.active_count()).encode() + b'\n')


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

def run():
    port = int(sys.argv[1])
    print("Listen on 0.0.0.0:{}".format(port))
    server = ThreadingSimpleServer(('0.0.0.0', port), Handler)
    if USE_HTTPS:
        import ssl
        server.socket = ssl.wrap_socket(server.socket, keyfile='./key.pem', certfile='./cert.pem', server_side=True)
    server.serve_forever()


if __name__ == '__main__':
    run()