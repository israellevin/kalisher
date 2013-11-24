kalisher
========

Software for the interactive art lab in Seminar Ha-Kibutzim.

server.py - a computer vision python script that analyzes camera input and
serves the results as HTTP JSONP replies over port 8000 and as
[FUDI](http://en.wikipedia.org/wiki/FUDI) messages over port 3001 in response
to messages over port 3000. Requires the Python cv2 module.

index.html - a simple HTML and JS example that harvests and displays data from
the server. Requires a browser and an Internet connection.

test.pd - a simple Pure Data example canvas that sends requests and prints
replies. Requires Pure Data.

install.sh - a bash script that installs a system from tar into a target,
chroots into it and installs grub. Requires a mounted device to install on.

mktar.sh - a bash script that creates a tar of a very open, minimal, hackable
debian sid chroot, with everything we need. Requires debootstrap.

overlay - a directory containing files for mktar.sh.
