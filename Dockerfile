FROM nikolaik/python-nodejs:python3.6-nodejs16

MAINTAINER Ricardo Neves "rsn_4_91@hotmail.com"

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
RUN npm install
RUN npm run build

ENTRYPOINT [ "python" ]

CMD ["run.py" ]
