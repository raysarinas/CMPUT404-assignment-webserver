#  coding: utf-8 
import socketserver, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()

        # decode and split
        http_request = self.data.decode("utf-8").split("\r\n")

        # split the start line
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages
        http_method, request_target, http_version = http_request[0].split(" ")

        if http_method != "GET": # donut allow POST, PUT or DELETE
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n", 'utf-8'))
            return

        # os.path stuff from Russell Dias https://stackoverflow.com/users/322129/
        # https://stackoverflow.com/a/5137509
        # https://docs.python.org/3.7/library/os.path.html
        rel_path = "www" + request_target
        real_path = os.path.realpath(os.getcwd())
        full_path = real_path + "/" + rel_path

        # checking if path or file from Jesse Jashinsky https://stackoverflow.com/users/349415/
        # https://stackoverflow.com/a/3204819
        # https://docs.python.org/3.7/library/os.html
        if os.getcwd() in os.path.realpath(full_path):
            if os.path.isdir(rel_path):
                self.process_path(full_path, request_target)
                return

            if os.path.isfile(rel_path):
                self.serve_request(full_path)
                return

        # if bad path
        self.request.sendall(bytearray("HTTP/1.1 404 File Not Found\r\n", 'utf-8'))

    def serve_request(self, path):
        content_type = ""

        # try/catching FileNotFoundError from João Ventura https://www.codementor.io/@joaojonesventura/
        # https://www.codementor.io/@joaojonesventura/building-a-basic-http-server-from-scratch-in-python-1cedkg0842#404-not-found
        # MIME types https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
        try:
            if ".css" in path:
                content_type = "Content-Type: text/css\r\n"
            elif ".html" in path:
                content_type = "Content-Type: text/html\r\n"
            # else:
            #     raise FileNotFoundError

            with open(path, 'r') as fi:
                data = fi.read()
                response = "HTTP/1.1 200 OK\r\n"
                response += content_type + "\r\n"
                response += "\n" + data + "\r\n"
                self.request.sendall(bytearray(response, 'utf-8'))

        except FileNotFoundError:
            self.request.sendall(bytearray("HTTP/1.1 404 File Not Found\r\n", 'utf-8'))
    
    def process_path(self, path, target):
        if path.endswith('/'):
            path += "index.html"
            self.serve_request(path)

        else: # correct the target path
            self.request.sendall(bytearray(f"HTTP/1.1 301 Moved Permanently\r\nLocation: {target}\r\n", 'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
