FROM ubuntu:14.04
MAINTAINER Haoyang Zeng <haoyangz@mit.edu>

RUN mkdir /scripts
COPY . /scripts
RUN chmod -R 777 /scripts
