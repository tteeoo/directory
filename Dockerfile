# sudo docker build -t directory .
# sudo docker run -dit -p 1010:1010 --name directory directory
FROM alpine:3.7

RUN apk update && \
    apk add py3-pip python3-dev

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

COPY . /app

EXPOSE 1010

CMD ["gunicorn", "--workers=4", "--bind", "0.0.0.0:1010", "wsgi"]
