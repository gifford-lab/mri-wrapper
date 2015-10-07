FROM haoyangz/cuda-caffe7.0

RUN apt-get update
RUN apt-get install -y vim nano curl python-pip python-numpy r-base

## Git clone codes
COPY . /scripts/mri-wrapper
RUN git clone https://haoyangz-ro:12312312@bitbucket.org/haoyangz/caffe-with-spearmint.git /scripts/Mri-app
RUN git clone https://haoyangz-ro:12312312@bitbucket.org/haoyangz/caffe-cnn.git /scripts/caffe-cnn

## Install Mri
RUN pip install -e git+https://github.com/Mri-monitoring/Mri-python-client.git#egg=mri-master
RUN cd /scripts/Mri-app && pip install -r requirements.txt && python setup.py install

## Make pycaffe
RUN cd /scripts/caffe && make pycaffe

## Set env
ENV PYTHONPATH /scripts/caffe/python:$PYTHONPATH
RUN chmod -R 777 /scripts
