kalisher
========

Software for the interactive art lab in Seminar Ha-Kibutzim.

server.py - a computer vision script that analyzes camera input and serves the results as HTTP JSONP replies over port 8000 and as [FUDI](http://en.wikipedia.org/wiki/FUDI) messages over port 3001 in response to messages over port 3000. Requires the Python cv2 module.

index.html - a simple HTML and JS example that harvests and displays data from the server. Requires a browser and an Internet connection.

test.pd - a Pure Data example canvas that sends requests and prints replies. Requires Pure Data.
