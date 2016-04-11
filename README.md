Incooperate [Mri](http://mri.readthedocs.org/en/latest/index.html) and [Caffe-cnn](https://github.com/gifford-lab/caffe-cnn) to perform hyper-parameter search.

## Prerequisite
+ [Docker](https://www.docker.com/) 
+ NVIDIA 346.46 driver

## Quick run
We provide some toy data on which you can quickly perform hyper-parameter searching, training and testing.

_Replace the $REPO_HOME$ in the following command with the full path to the repository folder before running_

```
docker pull haoyangz/mri-wrapper
docker run -v $REPO_HOME$/example:/data -v $REPO_HOME$/example/model:/model -i --rm \
--device /dev/nvidiactl \
--device /dev/nvidia-uvm \
--device /dev/nvidia0 \
haoyangz/mri-wrapper python main.py /model/runparam.list 0
```
This is what happens if it runs:

+ It will search for the best hyper-parameters for a toy [Caffe model](https://github.com/gifford-lab/mri-wrapper/tree/master/example/model/) on some toy [training and validation data](https://github.com/gifford-lab/mri-wrapper/tree/master/example/data). 

+ It will pick the set of parameters with best performance, and try a few times to train on the training data. 

+ It will find the trial and iteration where the model reaches the best performance on the validation set, and  make prediction with it on the toy testing [data](https://github.com/gifford-lab/mri-wrapper/tree/master/example/data). The output will be under $REPO_HOME$/example/16_G/mri-best/best_trial/


## Data preparation

Follow the instruction in [Caffe-cnn](https://github.com/gifford-lab/caffe-cnn) to prepare  data under $DATADIR$/data. 




## Model preparation

All of the files in this part should be saved under $MODELDIR$.

##### Caffe model files
Follow the instruction in [Caffe-cnn](https://github.com/gifford-lab/caffe-cnn) to prepare caffe model files:

+ trainval.prototxt : training architecture
+ solver.prototxt: solver parameter
+ deploy.prototxt: testing architecture

The only differences:

+ In trainval.prototxt, the "source" in the input layer should be /data/data/train.txt and /data/data/valid.txt


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

## Prepare [runparam.list](https://github.com/gifford-lab/mri-wrapper/blob/master/example/runparam.list)


```
MRI_MAXITER  5
ORDER trainMRI,update,trainCaffe,testCaffe,testEvalCaffe
search_max_iter 6000
search_snapshot 100
search_test_interval 100
search_display 10000
train_trial 2
debugmode INFO
optimwrt accuracy
outputlayer prob
```

+ `MRI_MAXITER`: The number of hyper-parameter setting to try.
+ `ORDER`: The order to carry out. Usually no need to change.
+ `search_max_iter`: Maximum number of iteration in hyper-parameter search.
+ `search_test_interval`: The iteration interval to test on validation set in hyper-parameter search.
+ `search_snapshot`: The iteration iterval to save model in hyper-parameter search.
+ `search_display`: The iteration interval to display the training loss in hyper-parameter search.
+ `train_trial`: After the best hyper-params are chosen, we will train this number of times and pick the best trial.
+ `debugmode`: The verbosity of log ('NONE'<'INFO'<'DEBUG'). We recommend 'INFO' in most case.
+ `optimwrt`: Choose the best param and training trial with respect to either accuracy or loss
+ `outputlayer`: The name of the output blob that will be used as prediction in test phase


## Ready to go!

```
docker pull haoyangz/mri-wrapper
docker run -v DATADIR:/data -v MODELDIR:/model -i --rm \
	--device /dev/nvidiactl --device /dev/nvidia-uvm MOREDEVICE \
	haoyangz/mri-wrapper python main.py /model/runparam.list GPUNUM
```

+ `DATADIR`: The topfolder of the output. Your data should be under $DATADIR$/data.
+ `MODELDIR`: The folder containing the model files, hyperparam file and modelname file
+ `MOREDEVICE`: For each of the GPU device available on your machine,append one "--device /dev/nvidiaNUM" where NUM is the number of that device. For hsf1/hsf2 in  Gifford Lab, since there are three GPU, it should be :

	```
--device /dev/nvidia0 --device /dev/nvidia1 --device /dev/nvidia2
```
+ `GPUNUM`: The GPU device number to run

	The output will be generated under $DATADIR$/thenameofthemodel, where `thenameofthemodel` is the name specified in the file $MODELDIR$/modelname .
