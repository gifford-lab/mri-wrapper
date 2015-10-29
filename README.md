Incooperate [Mri]() and [Caffe-cnn]() to perform hyper-parameter search.

## Prerequisite
### Install Docker
Following [instruction](https://www.docker.com/) to install Docker

### Prepare training data

Follow the instruction in [Caffe-cnn]() to prepare training data under $model_dir$/data/

The only difference is that in all the .txt files (like train.txt), the topfolder should be /data/data.

For example in train.txt:

```
/data/data/train.batch0.hd5
/data/data/train.batch1.hd5
...
```



### Prepare model files for Caffe
Follow the instruction in [Caffe-cnn]() to prepare caffe model files.

The only differences are:

+ In trainval.prototxt, the "source" in the input layer should be /data/data/train.txt and /data/data/valid.txt
+ The following parameters in solver.prototxt are used for hyper-parameter search only. The ones used for actual training need to be specified in runparam.list
	
	+ max_iter 
	+ snapshot 
	+ test_interval 
	+ display 


### Prepare hyper-pameter search
All the hyper-parameter to tune in solver.prototxt, trainval.prototxt should be surrounded by %{}% as exemplified in example/solver.protoxt and example/trainval.prototxt. The corresponding parameter in deploy.prototxt should also be converted accordingly.

Generate a hyperparam file **in the same folder as the model files**. Refer to examples/hyperparams.txt

### Prepare modelname file
We require a file named "modelname" in the same folder as model files that specify the name of the version of the model tested. Refer to examples/modelname.


### Prepare runparam.list
This file specificies all the parameters in the model. 

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