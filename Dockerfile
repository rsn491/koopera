FROM nikolaik/python-nodejs:python3.8-nodejs13

MAINTAINER Ricardo Neves "rsn_4_91@hotmail.com"

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt gunicorn
RUN npm install
RUN npm run build

EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "run:app"]
