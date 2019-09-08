FROM python:3.6

MAINTAINER Ricardo Neves "rsn_4_91@hotmail.com"

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt gunicorn

RUN apt-get update
RUN apt-get install curl -y
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash
RUN apt-get install nodejs -y
RUN npm install
RUN npm run build

EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "run:app"]