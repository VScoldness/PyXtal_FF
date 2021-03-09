# a slight modification based on table S5 from https://arxiv.org/pdf/1906.08888.pdf
from pyxtal_ff import PyXtal_FF
import os

TrainData = "data/training.json"
TestData  = "data/test.json"

if not os.path.exists(TrainData):
    if not os.path.exists('data'):
        os.mkdir('data')
    os.chdir('data')
    url = 'https://raw.githubusercontent.com/materialsvirtuallab/mlearn/master/data/Si/'
    print('Downloading the training and test data')
    os.system('wget ' + url + TrainData.split('/')[-1])
    os.system('wget ' + url + TestData.split('/')[-1])
    os.chdir('..')

descriptor = {'type': 'SO3',
              #'weights': {'Si': 1.0},
              'Rc': 5.0,
              'parameters': {'lmax': 4, 'nmax': 3},
              'ncpu': 1,
             }

model = {'system' : ['Si'],
         'hiddenlayers': [16, 16],
         'path': 'Si-so3/',
         #'restart': 'Si-so3/16-16-checkpoint.pth',
         'optimizer': {'method': 'lbfgs'},
         'force_coefficient': 2e-2,
         'stress_coefficient': 2e-3,
         'alpha': 1e-6,
         'epoch': 1000,
         }

ff = PyXtal_FF(descriptors=descriptor, model=model)
ff.run(mode='train', TrainData=TrainData, TestData=TestData)
