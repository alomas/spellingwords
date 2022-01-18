#!/usr/bin/env python
import json

"""Extend Python's built in HTTP server to save files

curl or wget can be used to send files with options similar to the following

  curl -X PUT --upload-file somefile.txt http://localhost:8000
  wget -O- --method=PUT --body-file=somefile.txt http://localhost:8000/somefile.txt

__Note__: curl automatically appends the filename onto the end of the URL so
the path can be omitted.

Windows upload & download

    powershell -ep bypass -c "$wc=New-Object Net.WebClient;$wc.UploadFile('http://target.com/upload.bin', 'PUT', 'c:\\upload.bin');"

    powershell -ep bypass -c "$wc=New-Object Net.WebClient;$wc.DownloadFile('http://target.com/download.bin','c:\\download.bin');"


Linux upload & download

    curl -X PUT --upload-file upload.bin http://target.com/upload.bin
    wget -O- --method=PUT --body-file=upload.bin http://target.com/upload.bin

    wget http://target.com/download.bin -O /tmp/download.bin
    curl http://target.com/download.bin -o /tmp/download.bin

"""
import os

try:
    import http.server as server
except ImportError:
    # Handle Python 2.x
    import SimpleHTTPServer as server


class HTTPRequestHandler(server.SimpleHTTPRequestHandler):
    """Extend SimpleHTTPRequestHandler to handle PUT requests"""

    def do_PUT(self):
        """Save a file following a HTTP PUT request"""
        filename = os.path.basename(self.path)

        # Don't overwrite files
        if os.path.exists(filename):
            self.send_response(409, 'Conflict')
            self.end_headers()
            reply_body = '"%s" already exists\n' % filename
            self.wfile.write(reply_body.encode('utf-8'))
            return

        file_length = int(self.headers['Content-Length'])
        read = 0
        with open(filename, 'wb+') as output_file:
            while read < file_length:
                new_read = self.rfile.read(min(66556, file_length - read))
                read += len(new_read)
                output_file.write(new_read)
        self.send_response(201, 'Created')
        self.end_headers()
        reply_body = 'Saved "%s"\n' % filename
        self.wfile.write(reply_body.encode('utf-8'))

    def do_GET(self):
        if self.path == '/nextword':
            self.send_response(200, 'Not Found')
            self.end_headers()
            global data
            global counter
            if len(data) == 0:
                with open('bee.json', 'r') as f:
                    data = json.load(f)
            print(f'counter={data[counter]} {len(data)}')
            newword = data.pop(0).replace("'", "\'")
            self.wfile.write(newword.encode('utf-8'))

        else:
            self.send_response(404, 'Not Found')
            self.end_headers()
            self.wfile.write("Sorry, your page is not found".encode('utf-8'))

counter = 0
with open('bee.json', 'r') as f:
  data = json.load(f)

if __name__ == '__main__':
    server.test(HandlerClass=HTTPRequestHandler)