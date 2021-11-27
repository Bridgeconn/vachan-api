FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./app /app/app
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
WORKDIR /app/app

RUN adduser vachan_user
USER vachan_user
ENV NODE_VERSION=16.13.0
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
ENV NVM_DIR=/home/vachan_user/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
ENV PATH="/home/vachan_user/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"
RUN node --version
RUN npm --version
RUN npm install -g usfm-grammar@2.2.0

USER root
