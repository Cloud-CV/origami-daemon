FROM python:3

LABEL MAINTAINER="CloudCV Team <admin@cloudcv.org>"  

COPY dev-requirements.txt /dev-requirements.txt

RUN pip install -r dev-requirements.txt

COPY . /daemon

WORKDIR /daemon

RUN pip install -e .

CMD [ "origamid" ]
