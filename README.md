# Deep Continuous Local Learning (DCLL)

## Environment
Make sure you have install the software below already 
* Ubuntu 18.04LTS
* NVIDIA driver 460.91.03
* CUDA 11.1
* CuDNN 8.0.4



## Installing
Clone and install. The Python setuptools and Conda environment.yml will take care of dependencies.

```
git clone https://github.com/fjcu-ee-islab/decolle.git
cd decolle

conda env create -f environment.yml
pip install -r requirements.txt
python setup.py install --user
```

## Downloading converted dataset from google drive
[Download](https://drive.google.com/drive/folders/1NLecOGpySNxd85QFZxENldeOXOHuALfN?usp=sharing)

The converted data should have the following file structure:

***(hdf5 files created when running the training code at first time)***
```
scripts
├── data
    ├── dvscifar10
        ├── Test
        ├── Train
        ├── dvscifar10.hdf5 
    ├── dvsgesture
        ├── raw
        ├── dvs_gesture_build19.hdf5
    ├── dvsmnist
        ├── Test
        ├── Train
        ├── dvsmnist.hdf5
    ├── IITM
        ├── Test
        ├── Train
        ├── IITM.hdf5
    ├── nmnist
        ├── Test
        ├── Train
        ├── nmnist.hdf5
    ├── UCF11
        ├── Test
        ├── Train
        ├── UCF11.hdf5
```

All parameter sets are contained in scripts/parameters, you can use them as such:

```
cd scripts
python train.py --params_file=parameters/params_dvscifar10.yml
python train.py --params_file=parameters/params_dvsgesture.yml
python train.py --params_file=parameters/params_dvsmnist.yml
python train.py --params_file=parameters/params_IITM.yml
python train.py --params_file=parameters/params_nmnist.yml
python train.py --params_file=parameters/params_UCF11.yml
```
