FROM nikolaik/python-nodejs:python3.8-nodejs16

LABEL org.opencontainers.image.authors="rsn_4_91@hotmail.com"

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
RUN npm install
RUN npm run build

ENTRYPOINT [ "python" ]

CMD ["run.py" ]
