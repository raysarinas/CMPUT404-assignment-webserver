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
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n", 'utf-8'))
            return
        
        print(request_target)
        rel_path = "www" + request_target
        # https://stackoverflow.com/questions/5137497/find-current-directory-and-files-directory/44569198
        real_path = os.path.realpath(os.getcwd())

        # https://stackoverflow.com/a/3204819 - os.path.isdir()
        # move code below into bad_path and refactor so that logic follows old logic from b4
        if os.path.isdir(rel_path):
            self.process_path(real_path + "/" + rel_path)
            return

        if os.path.isfile(rel_path):
            self.serve_request(real_path + "/" + rel_path)
            return

        # if neither a dir or file then don't know what it is obvs
        self.request.sendall(bytearray("HTTP/1.1 404 File Not Found\r\n", 'utf-8'))

    def serve_request(self, path):
        response = "HTTP/1.1 "
        content_type = ""
        # try/catching FileNotFoundError from João Ventura
        # https://www.codementor.io/@joaojonesventura/building-a-basic-http-server-from-scratch-in-python-1cedkg0842#404-not-found
        try:
            with open(path, 'r') as fi:
                data = fi.read()
                response += "200 OK\r\n" + content_type + "\r\n"
                response += "\n" + data + "\r\n"
                response += "=========================================================\r\n"
                self.request.sendall(bytearray(response, 'utf-8'))

        except FileNotFoundError:
            self.request.sendall(bytearray(response + "404 File Not Found\r\n", 'utf-8'))
    
    def process_path(self, path):
        if path.endswith('/'):
            path += "index.html"
            self.serve_request(path)

        else: # correct the target path
            # print("does not end with / so 301 -_-")
            self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\n", 'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
