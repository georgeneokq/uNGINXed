FROM nginx
expose 80/tcp
run apt update && apt install -y python3 python3-pip
run pip3 install Jinja2 Werkzeug --break-system-packages
copy ./raw-response-reading.conf /etc/nginx/nginx.conf
copy ./app.py /root/app.py
copy ./start.sh /root/start.sh
copy ./error.html /root/error.html
run chmod +x /root/start.sh
workdir /root
entrypoint ./start.sh
