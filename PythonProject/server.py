from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

arrangements = {'rome': 'italy',
                'istanbul': 'turkey',
                'paris': 'france',
                'bangkok': 'thailand'}


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.log_message("Incoming GET request...")
        try:
            name = parse_qs(self.path[2:])['name'][0]
        except:
            self.send_response_to_client(404, 'Incorrect parameters provided')
            self.log_message("Incorrect parameters provided")
            return

        if name in arrangements.keys():
            self.send_response_to_client(200, arrangements[name])
        else:
            self.send_response_to_client(400, 'Name not found')
            self.log_message("Name not found")

    def do_POST(self):
        self.log_message('Incoming POST request...')
        data = parse_qs(self.path[2:])
        try:
            arrangements[data['name'][0]] = data['country'][0]
            self.send_response_to_client(200, arrangements)
        except KeyError:
            self.send_response_to_client(404, 'Incorrect parameters provided')
            self.log_message("Incorrect parameters provided")

    def send_response_to_client(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(str(data).encode())


server_address = ('127.0.0.1', 8080)
http_server = HTTPServer(server_address, RequestHandler)
http_server.serve_forever()