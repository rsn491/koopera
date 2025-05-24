FROM python:3.13-slim

LABEL org.opencontainers.image.authors="rsn_4_91@hotmail.com"

# Install Node.js 20.x
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x -o nodesource_setup.sh && \
    bash nodesource_setup.sh && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
RUN npm install
RUN npm run build

ENTRYPOINT [ "python" ]

CMD ["run.py" ]
