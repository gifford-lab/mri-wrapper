FROM haoyangz/cuda-caffe7.0

RUN apt-get update
RUN apt-get install -y vim curl r-base
RUN pip install scikit-learn

## Git clone codes
COPY . /scripts/mri-wrapper
RUN git clone https://github.com/haoyangz/Mri-app.git /scripts/Mri-app
RUN git clone https://github.com/gifford-lab/caffe-cnn.git /scripts/caffe-cnn

## Install Mri
RUN pip install -e git+https://github.com/Mri-monitoring/Mri-python-client.git#egg=mri-master
RUN cd /scripts/Mri-app && pip install -r requirements.txt && python setup.py install

## Set env
RUN chmod -R 777 /scripts
WORKDIR /scripts/mri-wrapper
