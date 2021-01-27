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
        print(http_request)

        # split the start line
        http_method, request_target, http_version = http_request[0].split(" ")

        if http_method != "GET": # donut allow POST, PUT or DELETE
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\n", 'utf-8'))
            return
        
        if self.bad_path(request_target):
            self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\n", 'utf-8'))
            return
        
        rel_path = "/www" + request_target
        # https://stackoverflow.com/questions/5137497/find-current-directory-and-files-directory/44569198
        real_path = os.path.realpath(os.getcwd())

        if rel_path.endswith('/'):
            rel_path += "index.html"
        print("RELATIVE PATH:", rel_path)
        full_path = real_path + rel_path
        print("FULL PATH:", full_path)

        self.serve_request(full_path)

    def serve_request(self, path):
        response = "HTTP/1.1 "
        # try/catching FileNotFoundError from João Ventura
        # https://www.codementor.io/@joaojonesventura/building-a-basic-http-server-from-scratch-in-python-1cedkg0842#404-not-found
        try:
            with open(path, 'r') as fi:
                data = fi.read()
                response += "200 OK\n"
                response += "Contents:\n" + data
                response += "=========================================================\n"
                self.request.sendall(bytearray(response, 'utf-8'))

        except FileNotFoundError:
            self.request.sendall(bytearray(response + "404 File Not Found\n", 'utf-8'))

    def bad_path(self, request_target):
        is_file = '.' in request_target.split("/")[-1]
        return request_target[-1] != '/' and not is_file

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
