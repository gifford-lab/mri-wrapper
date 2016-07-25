Incooperate [Mri](http://mri.readthedocs.org/en/latest/index.html) and [Caffe-cnn](https://github.com/gifford-lab/caffe-cnn) to perform hyper-parameter search.

## Dependencies
+ [Docker](https://www.docker.com/) 
+ NVIDIA 346.46 driver

## Quick run
We provide some toy data on which you can quickly perform hyper-parameter searching, training and testing._You need to run it under the repository directory_.

```
docker pull haoyangz/mri-wrapper
docker run -v $(pwd)/example:/data -v $(pwd)/example/model:/model -i --rm \
--device /dev/nvidiactl \
--device /dev/nvidia-uvm \
--device /dev/nvidia0 \
haoyangz/mri-wrapper python main.py /model/runparam.list 0
```
This is what happens if it runs:

+ Search for the best hyper-parameters for a toy [Caffe model](https://github.com/gifford-lab/mri-wrapper/tree/master/example/model/) on some toy [training and validation data](https://github.com/gifford-lab/mri-wrapper/tree/master/example/data). 

+ Pick the set of parameters with best performance, and try a few times to train on the training data. The trial and iteration where the model reaches the best performance on the validation set will be picked for testing and prediction.

+ Make prediction with the best model on the toy testing [data](https://github.com/gifford-lab/mri-wrapper/tree/master/example/data). The output will be under *$REPO_HOME$/example/16_G/mri-best/best_trial/*

+ Make prediction with a pre-trained model (specified by _example/newdata/deploy.txt_ and _example/newdata/bestiter.caffemodel_) to predict on new data specified in *example/newdata/test.txt*. The output will be saved under *example/newdata_output*.


## Data preparation

Follow the instruction in [Caffe-cnn](https://github.com/gifford-lab/caffe-cnn) to prepare  data under *$DATADIR$/data*. 

## Model preparation

All of the files in this part should be saved under $MODELDIR$.

##### Caffe model files
Follow the instruction in [Caffe-cnn](https://github.com/gifford-lab/caffe-cnn) to prepare caffe model files:

+ trainval.prototxt : training architecture
+ solver.prototxt: solver parameter
+ deploy.prototxt: testing architecture

**The only differences**:

+ In trainval.prototxt, the "source" in the input layer should be /data/data/train.txt and /data/data/valid.txt


##### Modify model files for hyper-parameter search

For each hyperparameter to tune, replace the value with %{param}% instead. For example:

In [solver.prototxt](https://github.com/gifford-lab/mri-wrapper/blob/master/example/model/solver.prototxt):

```
delta: %{delta}%
```

In [trainval.prototxt](https://github.com/gifford-lab/mri-wrapper/blob/master/example/model/trainval.prototxt) / [deploy.prototxt](https://github.com/gifford-lab/mri-wrapper/blob/master/example/model/deploy.prototxt): 

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
**Note that every parameter changed in trainval.prototxt should also be modified accordingly in deploy.prototxt**

##### Specify value choices of hyper-parmeters

In "[hyperparams.txt](https://github.com/gifford-lab/mri-wrapper/blob/master/example/model/hyperparams.txt)" file. 

##### Specify model name
In "[modelname](https://github.com/gifford-lab/mri-wrapper/blob/master/example/model/modelname)" file.

## Prepare [runparam.list](https://github.com/gifford-lab/mri-wrapper/blob/master/example/model/runparam.list)

General argument:
+ `ORDER`: The order to carry out. 
	+ `trainMRI`: hyper-parameter tuning
	+ `update`: pick the best hyper-parameter
	+ `trainCaffe`: train on the training set with the best hyper-parameter
	+ `testCaffe`: predict on the test set with the trained model
	+ `testEvalCaffe`: evaluate the performance on test set
	+ `predictCaffe`: predict with a pre-trained model to predict on new data

If you want to perform hyper-parameter tuning, training and testing:
+ `MRI_MAXITER`: The number of hyper-parameter setting to try.
+ `search_max_iter`: Maximum number of iteration in hyper-parameter search.
+ `search_test_interval`: The iteration interval to test on validation set in hyper-parameter search.
+ `search_snapshot`: The iteration iterval to save model in hyper-parameter search.
+ `search_display`: The iteration interval to display the training loss in hyper-parameter search.
+ `train_trial`: After the best hyper-params are chosen, we will train this number of times and pick the best trial.
+ `debugmode`: The verbosity of log ('NONE'<'INFO'<'DEBUG'). We recommend 'INFO' in most case.
+ `optimwrt`: Choose the best param and training trial with respect to either accuracy or loss
+ `outputlayer`: The name of the output blob that will be used as prediction in test phase

If you want to  predict on new data with a trained model:
+ `outputlayer`: Same as above.
+ `deploy2predictW`: path to the [deploy.prototxt](https://github.com/gifford-lab/mri-wrapper/blob/master/example/newdata/deploy.prototxt) file of the trained model, which specifies the network architecture.
+ `caffemodel2predictW`: path to the snapshot of the trained model, which ends with '.caffemodel' and during training will be saved every `snapshot` number of iteration as specified in [solver.prototxt](https://github.com/gifford-lab/mri-wrapper/blob/master/example/model/solver.prototxt).
+ `data2predict`: path to the [manifest](https://github.com/gifford-lab/mri-wrapper/blob/master/example/newdata/test.txt) file specifying all HDF5 format data to predict on.
+ `predict_outdir`:  the output directory, under which 'bestiter.pred' and 'bestiter.pred.params.pkl' will be saved. See description for `outputlayer`.

**As Mri-wrapper lives in the docker container, it can only access the directory mounted to the container. For instance, in the toy example above, *$(pwd)/example* is mounted as */data* and *$(pwd)/example/model* is mounted as */model*. Therefore all the above path parameters should be relative to one of the mounted directory. But you can mount as many directory as you want with '-v' option as in the toy example.**


## Ready to go!

```
docker pull haoyangz/mri-wrapper
docker run -v DATADIR:/data -v MODELDIR:/model -i --rm \
	--device /dev/nvidiactl --device /dev/nvidia-uvm MOREDEVICE \
	haoyangz/mri-wrapper python main.py /model/runparam.list GPUNUM
```

+ `DATADIR`: The topfolder of the output. Your data should be under *$DATADIR$/data*.
+ `MODELDIR`: The folder containing the model files, hyperparam file and modelname file
+ `MOREDEVICE`: For each of the GPU device available on your machine,append one "--device /dev/nvidiaNUM" where NUM is the number of that device. For hsf1/hsf2 in  Gifford Lab, since there are three GPU, it should be :

	```
--device /dev/nvidia0 --device /dev/nvidia1 --device /dev/nvidia2
```
+ `GPUNUM`: The GPU device number to run


For hyper-parameter tuning, training and testing, the output will be generated under *$DATADIR$/thenameofthemodel*, where `thenameofthemodel` is the name specified in the file $MODELDIR$/modelname .
