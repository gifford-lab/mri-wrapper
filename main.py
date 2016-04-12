#!/usr/bin/python
import os,sys
from parseMRI import parseMRI
from os.path import dirname,exists,join,realpath
from os import system,makedirs,chdir,getcwd,makedirs

cwd = dirname(realpath(__file__))
system('ln /dev/null /dev/raw1394')

runparam_file = sys.argv[1]
gpunum = sys.argv[2]

with open(runparam_file,'r') as f:
    runparamdata = f.readlines()
runparams = {}
for i in range(len(runparamdata)):
    line = runparamdata[i].strip().split()
    runparams.update({line[0]:line[1]})
    print line[0] +' : '+str(line[1])

order = runparams['ORDER']
CAFFE_ROOT = '/scripts/caffe'
mri_maxiter = int(runparams['MRI_MAXITER'])
mri_ROOT = '/scripts/Mri-app'
CAFFECNN_ROOT = '/scripts/caffe-cnn'
runparams['TRAINVAL'] = '/model/trainval.prototxt'
runparams['SOLVER'] = '/model/solver.prototxt'
runparams['DEPLOY'] = '/model/deploy.prototxt'
runparams['HYPER'] = '/model/hyperparams.txt'
runparams['model_topdir'] = '/data'

with open('/model/modelname','r') as f:
    modelname = [x.strip() for x in f][0]

mrifolder = join(runparams['model_topdir'],modelname,'mri')
mri_bestfolder = join(runparams['model_topdir'],modelname,'mri','best')
deploy_tempalte = os.path.join(cwd,'deploy.prototxt')
trainval_file = join(cwd,'trainval.prototxt')
solver_file = join(cwd,'solver.prototxt')
param_file = join(cwd,'param.list')
train_params = join(cwd,'train.params')
hyperparam = join(cwd,'hyperparams.txt')
mrilogfile = join(mrifolder,'mri.log')

transfer_params = {'max_iter','snapshot','test_interval','display'}

with open(param_file,'w') as f:
    f.write('output_topdir %s\n' % runparams['model_topdir'])
    f.write('caffemodel_topdir %s\n' % mri_bestfolder)
    f.write('batch2predict mri-best\n')
    f.write('gpunum %s\n' % gpunum)
    f.write('model_name %s\n' % modelname)
    f.write('batch_name %s\n' % 'mri-best')
    f.write('trial_num %s\n' % runparams['train_trial'])
    f.write('optimwrt %s\n' % runparams['optimwrt'])
    f.write('outputlayer %s\n' % runparams['outputlayer'])
    if 'predict_on' in runparams:
        f.write('predict_filelist %s\n' % runparams['predict_on'])


if 'trainMRI' in order:
    system(' '.join(['cp ',runparams['TRAINVAL'],trainval_file]))
    system(' '.join(['cp ',runparams['DEPLOY'],deploy_tempalte]))
    system(' '.join(['cp ',runparams['HYPER'],hyperparam]))

    with open(solver_file,'w') as outs,open(runparams['SOLVER'],'r') as ins:
        for x in ins:
            key = x.strip().split(':')[0].split(' ')[0]
            if key in transfer_params:
                newkey = 'search_'+key
                outs.write('%s\n' % ':'.join([key,runparams[newkey]]))
            else:
                outs.write(x)

    system(' '.join(['echo','\'device_id: '+gpunum+'\'','>>',solver_file]))

    if exists(mrifolder):
        print 'output folder ' + mrifolder + ' exists! Will be removed'
        system('rm -r ' + mrifolder)

    print 'Trainning MRI'
    key = '\'MRIDIR\''
    value = '\'' + mrifolder +'\''
    cmd = ' '.join(['Rscript', join(cwd,'subPlaceholder.R'),join(cwd,'config.txt.template'),key,value,join(cwd,'config.txt')])
    system(cmd)

    key = '\'' + ';'.join(['MRIDIR','CAFFEROOT','INFO']) + '\''
    value = '\'' + ';'.join([mrifolder,CAFFE_ROOT,runparams['debugmode']]) + '\''
    cmd = ' '.join(['Rscript', join(cwd,'subPlaceholder.R'),join(cwd,'config.template'),key,value,join(mri_ROOT,'mriapp','config')])
    system(cmd)

    system('python generate_tasks.py random -n '+str(mri_maxiter))

    chdir(mri_ROOT+'/mriapp')
    system('python MriApp.py')
    chdir(cwd)

if 'update' in order:
    system(' '.join(['cp ',runparams['TRAINVAL'],trainval_file]))
    system(' '.join(['cp ',runparams['SOLVER'],solver_file]))
    system(' '.join(['cp ',runparams['DEPLOY'],deploy_tempalte]))
    system(' '.join(['cp ',runparams['HYPER'],hyperparam]))
    system(' '.join(['echo','\'device_id: '+gpunum+'\'','>>',solver_file]))

    print 'Retrieving best param from Mri'
    refile = 'mri_summary'
    system(' '.join(['grep \'Final Extreme\'', mrilogfile, '>',refile]))
    re= parseMRI(refile,runparams['optimwrt'])
    print 'best params:'
    print re

    trainsolver = join(mri_bestfolder,'solver.prototxt')
    trainproto = join(mri_bestfolder,'trainval.prototxt')
    testdeploy = join(mri_bestfolder,'deploy.prototxt')
    if not exists(mri_bestfolder):
        makedirs(mri_bestfolder)

    key = '\'' + ';'.join([x for x in re.keys()]) + '\''
    value = '\'' + ';'.join([re[x] for x in re.keys()]) + '\''

    cmd = ' '.join(['Rscript', os.path.join(cwd,'subPlaceholder.R'),solver_file,key,value,trainsolver])
    os.system(cmd)
    cmd = ' '.join(['Rscript', os.path.join(cwd,'subPlaceholder.R'),trainval_file,key,value,trainproto])
    os.system(cmd)
    cmd = ' '.join(['Rscript', os.path.join(cwd,'subPlaceholder.R'),deploy_tempalte,key,value,testdeploy])
    os.system(cmd)

if 'trainCaffe' in order:
    print 'Training caffe on best mri-params'
    os.system(' '.join(['python',CAFFECNN_ROOT+'/run.py','train',param_file]))

if 'testCaffe' in order:
    print 'Testing caffe on best mri-params'
    os.system(' '.join(['python',CAFFECNN_ROOT+'/run.py','test',param_file]))

if 'testEvalCaffe' in order:
    print 'Evaluating caffe on best mri-params'
    os.system(' '.join(['python',CAFFECNN_ROOT+'/run.py','test_eval',param_file]))
