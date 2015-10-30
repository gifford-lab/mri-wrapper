Incooperate [Mri](http://mri.readthedocs.org/en/latest/index.html) and [Caffe-cnn](https://github.com/gifford-lab/caffe-cnn) to perform hyper-parameter search.

## Prerequisite
+ [Docker](https://www.docker.com/) 


## Data preparation

Follow the instruction in [Caffe-cnn](https://github.com/gifford-lab/caffe-cnn) to prepare  data under $model_dir$/data/

The only difference is that in all the .txt files (like train.txt), the topfolder should be /data/data.

For example in train.txt:

```
/data/data/train.batch0.hd5
/data/data/train.batch1.hd5
...
```



## Model preparation

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
+ The following parameters in solver.prototxt are used for hyper-parameter search only. The ones used for actual training need to be specified in runparam.list
	
	+ max_iter 
	+ snapshot 
	+ test_interval 
	+ display 


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

In "hyperparams.list" file. See [Example](https://github.com/gifford-lab/mri-wrapper/blob/master/example/hyperparams.txt)

##### Specify model name
In "modelname" file. See [Example](https://github.com/gifford-lab/mri-wrapper/blob/master/example/modelname)

## Prepare runparam.list
This file specificies other parameters needed for training and testing.

Example : (example/runparam.list)

```
MRI_MAXITER  30
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
data_src zeng@sox2.csail.mit.edu:/cluster/zeng/code/research/kmer-analysis/     postprocess/compare_with_ctr/peakPred/embedding-CNN/target/NFKB_50flank/data
train_trial 6
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

+ `MRI_MAXITER`: The number of hyper-parameter setting to try
+ `ORDER`: The order to carry out. Usually no need to change.
+ `max_iter`: Maximum number of iteration in training phase
+ `snapshot`: The iteration iterval to save model in training phase
+ `test_interval`: The iteration interval to test on validation set in training phase
+ `display`: The iteration interval to display the training loss in training phase
+ `train_trial`: The number of training trial


## Run the model

```
docker run -v DATADIR:/data -v MODELDIR:/model -i --rm --device /dev/nvidiactl --device /dev/nvidia-uvm MOREDEVICE haoyangz/mri-wrapper python main.py /model/runparam.list GPUNUM
```

+ `DATADIR`: The topfolder of the output, i.e. $model_dir$
+ `MODELDIR`: The folder containing the model files, hyperparam file and modelname file
+ `MOREDEVICE`: For each of the GPU device number NUM available,append "--device /dev/nvidiaNUM". For example, if we have two GPU, then it  should be :

```
--device /dev/nvidia0 --device /dev/nvidia1
```
+ `GPUNUM`: The GPU device number to run

The output will be generated under $model_dir$/thenameofthemodel, where `thenameofthemodel` is the name specified in the file $MODELDIR$/modelname .