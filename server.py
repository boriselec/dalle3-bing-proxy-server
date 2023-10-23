#!/usr/bin/env python
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from dalle3 import Dalle

hostName = "0.0.0.0"
serverPort = 8081


class GenerationServer(BaseHTTPRequestHandler):
    lock = threading.Lock()

    def do_POST(self):
        if self.path.startswith('/generate'):
            if self.lock.acquire(blocking=False):
                try:
                    content_length = int(self.headers['Content-Length'])
                    data = self.rfile.read(content_length).decode('utf-8')

                    # Define cookie using env or empty string
                    cookie = "1cs6__B8gHKxn9ohRWOLeKYNTKNdfGVmasWfcJ2dc0XIF-FcOLpg7tCzLOo_Af0duEVgig0GH6QqfTzPSjB1Selw2OpqJkYDpdvhVt9fPz7H01pDgidU9pwai5ojGWB1D482pxZwcWGHVnulLTcQ9XnVheiCpdaBTX_Of5TEr2YU5MOi5Xgg6jCdRd27-mpsRG9oDstQroLbb31AghSFycw"

                    # Set up logging
                    logging.basicConfig(level=logging.INFO)

                    # Instantiate the Dalle class with your cookie value
                    dalle = Dalle(cookie)

                    # Open the website with your query
                    dalle.create(data)

                    # Get the image URLs
                    urls = dalle.get_urls()

                    # Download the images to your specified folder
                    dalle.download([urls[0]], "images/")

                    # Path to your main folder
                    folder_path = "images"

                    # Get all sub-folders in the main folder
                    subfolders = [f.path for f in os.scandir(folder_path) if f.is_dir()]

                    # Assuming there's only one sub-folder, get its path
                    subfolder_path = subfolders[0]

                    # Construct the full path to the image file
                    image_path = os.path.join(subfolder_path, 'image_1.png')

                    f = open(image_path, 'rb')
                    self.send_response(200)
                    self.send_header("Content-type", "image/png")
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()

                    os.remove("images")

                except RuntimeError:
                    logging.exception("Error processing request")
                    self.send_error(500)
                finally:
                    self.lock.release()
            else:
                self.send_error(503, 'Busy')

        else:
            self.send_error(404, 'Not found')


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), GenerationServer)
    print("Server started http://%s:%s\n" % (hostName, serverPort), flush=True)

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.", flush=True)
