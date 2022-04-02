FROM python:3

RUN mkdir /var/project/

WORKDIR /var/project/

COPY ./requirements.txt /var/project/

RUN pip3 install uwsgi

RUN pip3 install -r requirements.txt

COPY . .

RUN python3 manage.py migrate # Database is not used

EXPOSE 8000

CMD uwsgi --http "0.0.0.0:8000" --module moonfire_monitoring.wsgi --master --processes 4 --threads 2
