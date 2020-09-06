FROM ubuntu:18.04

RUN apt-get update && apt-get install -y pyside-tools && apt-get clean

VOLUME /av-control

CMD cd /av-control && ./compileResources.sh
