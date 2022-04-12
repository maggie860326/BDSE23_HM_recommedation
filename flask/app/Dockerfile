FROM tiangolo/uwsgi-nginx-flask:python3.9

MAINTAINER wuguansian

COPY . .

RUN pip3 install -r requirements.txt



CMD ["python3","main.py","/bin/sh"]