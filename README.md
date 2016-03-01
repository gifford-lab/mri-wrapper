Incooperate [Mri](http://mri.readthedocs.org/en/latest/index.html) and [Caffe-cnn](https://github.com/gifford-lab/caffe-cnn) to perform hyper-parameter search.

## Prerequisite
+ [Docker](https://www.docker.com/) 
+ NVIDIA 346.46 driver

## Quick run
_Replace the $REPO_HOME$ in the following command with the full path to the repository folder before running_

```
docker run -v $REPO_HOME$/example:/data -v $REPO_HOME$/example:/model -i --rm \
--device /dev/nvidiactl \
--device /dev/nvidia-uvm \
--device /dev/nvidia0 \
haoyangz/mri-wrapper python main.py /model/runparam.list 0
```
This will perform hyper-parameter searching, training and testing. The output will be under $REPO_HOME$/example/16_G/mri-best/best_trial/


## Data preparation

Follow the instruction in [Caffe-cnn](https://github.com/gifford-lab/caffe-cnn) to prepare  data under $model_dir$/data/

The only difference is that in [train.txt](https://github.com/gifford-lab/mri-wrapper/tree/master/example/data/train.txt)/[valid.txt](https://github.com/gifford-lab/mri-wrapper/tree/master/example/data/valid.txt)/[test.txt](https://github.com/gifford-lab/mri-wrapper/tree/master/example/data/test.txt), the topfolder should be /data/data.




## Model preparation

List of the files needed:

+ trainval.prototxt : training architecture
+ solver.prototxt: solver parameter
+ deploy.prototxt: testing architecture
+ hyperparams.txt: hyper-parameter specification
+ modelname: the name of the model

##### Generate Caffe model files
Follow the instruction in [Caffe-cnn](https://github.com/gifford-lab/caffe-cnn) to prepare caffe model files:

+ trainval.prototxt
+ solver.prototxt
+ deploy.prototxt

The only differences are:

+ In trainval.prototxt, the "source" in the input layer should be /data/data/train.txt and /data/data/valid.txt
+ The following parameters in solver.prototxt are used for hyper-parameter search only. The ones used for actual training need to be specified in [runparam.list](https://github.com/gifford-lab/mri-wrapper/blob/master/example/runparam.prototxt)
	
	+ `max_iter` 
	+ `test_interval`
	+ `snapshot`: In hyper-parameter search phase, we don't directly use the trained model. Therefore set this as arbitrarily large to save time and space.
	+ `display`: As we don't care training loss in hyper-parameter search phase, this should be set to arbitrarily large to save time and space.

##### Modify model files for hyper-parameter search

For each hyperparameter to tune, replace the value with %{param}% instead. For example:

In [solver.prototxt](https://github.com/gifford-lab/mri-wrapper/blob/master/example/solver.prototxt):

```
delta: %{delta}%
```

In [trainval.prototxt](https://github.com/gifford-lab/mri-wrapper/blob/master/example/trainval.prototxt) / [deploy.prototxt](https://github.com/gifford-lab/mri-wrapper/blob/master/example/deploy.prototxt): 

```
layer {
  name: "drop1"
  type: "Dropout"
  bottom: "fc1"
  top: "fc1"
  dropout_param{
    dropout_ratio: %{dropout_ratio}%
  }
}
```
_Note that every parameter changed in trainval.prototxt should also be modified accordingly in deploy.prototxt_

##### Specify value choices of hyper-parmeters

In "[hyperparams.txt](https://github.com/gifford-lab/mri-wrapper/blob/master/example/hyperparams.txt)" file. 

##### Specify model name
In "[modelname](https://github.com/gifford-lab/mri-wrapper/blob/master/example/modelname)" file.

## Prepare runparam.list
This file specificies other parameters needed for training and testing.

Example : (example/runparam.list)

```
MRI_MAXITER  5
TRAINVAL  /model/trainval.prototxt
SOLVER  /model/solver.prototxt
DEPLOY  /model/deploy.prototxt
HYPER  /model/hyperparams.txt
CAFFE_ROOT  /scripts/caffe
MRI_ROOT /scripts/Mri-app
CAFFECNN_ROOT /scripts/caffe-cnn
ORDER trainMRI,update,trainCaffe,testCaffe,testEvalCaffe
modelname_file /model/modelname
max_iter 6000
snapshot 100
test_interval 100
display 10000
model_topdir /data
data_src NA
train_trial 2
debugmode INFO
optimwrt accuracy
outputlayer prob
```

Constant params: (Don't change)

+ `TRAINVAL`: Training model file.
+ `SOLVER`: Solver file. 
+ `HYPER`: Hyper-parameter file.
+ `CAFFE_ROOT`: The path to caffe. 
+ `MRI_ROOT`: The path to Mri.
+ `CAFFECNN_ROOT`: The path to caffe-cnn
+ `modelname_file`: Modelname file.
+ `model_topdir`: The top folder of the output. 
+ `data_src`: not used in this version.

Tweakable params:

+ `MRI_MAXITER`: The number of hyper-parameter setting to try.
+ `ORDER`: The order to carry out. Usually no need to change.
+ `max_iter`: Maximum number of iteration in training phase.
+ `test_interval`: The iteration interval to test on validation set in training phase.
+ `snapshot`: The iteration iterval to save model in training phase. Should use same value as `test_interval`.
+ `display`: The iteration interval to display the training loss in training phase. For users who don't care the specific training process, this can be set to arbitrarily large to save time and space
+ `train_trial`: The number of training trial.
+ `debugmode`: The verbosity of log ('NONE'<'INFO'<'DEBUG'). We recommend 'INFO' in most case.
+ `optimwrt`: Choose the best param and training trial wrt to either accuracy or loss
+ `outputlayer`: The name of the output blob that will be used as prediction in test phase


## Run the model

```
docker run -v DATADIR:/data -v MODELDIR:/model -i --rm --device /dev/nvidiactl --device /dev/nvidia-uvm MOREDEVICE haoyangz/mri-wrapper python main.py /model/runparam.list GPUNUM
```

+ `DATADIR`: The topfolder of the output, i.e. $model_dir$
+ `MODELDIR`: The folder containing the model files, hyperparam file and modelname file
+ `MOREDEVICE`: For each of the GPU device available on your machine,append one "--device /dev/nvidiaNUM" where NUM is the number of that device. For hsf1/hsf2 in  Gifford Lab, since there are three GPU, it should be :

```
--device /dev/nvidia0 --device /dev/nvidia1 --device /dev/nvidia2
```
+ `GPUNUM`: The GPU device number to run

The output will be generated under $model_dir$/thenameofthemodel, where `thenameofthemodel` is the name specified in the file $MODELDIR$/modelname .
