#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Author: Emre Neftci
#
# Creation Date : Fri 01 Dec 2017 10:05:17 PM PST
# Last Modified : Sun 29 Jul 2018 01:39:06 PM PDT
#
# Copyright : (c)
# Licence : Apache License, Version 2.0
#-----------------------------------------------------------------------------

import struct
import time, copy
import numpy as np
import scipy.misc
import h5py
import torch.utils.data
from ..neuromorphic_dataset import NeuromorphicDataset 
from ..events_timeslices import *
from ..transforms import *
from .create_hdf5 import create_events_hdf5
import os

mapping = { 0 :'comeHome',
            1 :'left_swipe',
            2 :'right_swipe',
            3 :'rotation_CCW',
            4 :'rotation_CW',
            5 :'swipeDown',
            6 :'swipeUP',
            7 :'swipeV',
            8 :'X',
            9 :'Z'}

class IITMDataset(NeuromorphicDataset):
    directory = 'data/IITM/'
    resources_local = [directory+'Train', directory+'Test']

    def __init__(
            self, 
            root,
            train=True,
            transform=None,
            target_transform=None,
            download_and_create=True,
            chunk_size = 500,
            dt = 1000):

        self.n = 0
        self.nclasses = self.num_classes = 10
        self.download_and_create = download_and_create
        self.root = root
        self.train = train 
        self.dt = dt
        self.chunk_size = chunk_size

        super(IITMDataset, self).__init__(
                root,
                transform=transform,
                target_transform=target_transform )
        
        with h5py.File(root, 'r', swmr=True, libver="latest") as f:
            try:
                if train:
                    self.n = f['extra'].attrs['Ntrain']
                    self.keys = f['extra']['train_keys'][()]
                    self.keys_by_label = f['extra']['train_keys_by_label'][()]
                else:
                    self.n = f['extra'].attrs['Ntest']
                    self.keys = f['extra']['test_keys'][()]
                    self.keys_by_label = f['extra']['test_keys_by_label'][()]
                    self.keys_by_label[:,:] -= self.keys_by_label[0,0] #normalize
            except AttributeError:
                print('Attribute not found in hdf5 file. You may be using an old hdf5 build. Delete {0} and run again'.format(root))
                raise

    def create_hdf5(self):
        create_events_hdf5(self.directory, self.root)


    def __len__(self):
        return self.n
        
    def __getitem__(self, key):
        #Important to open and close in getitem to enable num_workers>0
        with h5py.File(self.root, 'r', swmr=True, libver="latest") as f:
            if self.train:
                key = f['extra']['train_keys'][key]
            else:
                key = f['extra']['test_keys'][key]
            data, target = sample(
                    f,
                    key,
                    T = self.chunk_size*self.dt)

        if self.transform is not None:
            data = self.transform(data)

        if self.target_transform is not None:
            target = self.target_transform(target)

        return data, target

def sample(hdf5_file,
        key,
        T = 300):
    dset = hdf5_file['data'][str(key)]
    label = dset['labels'][()]
    tend = dset['times'][-1] 
    start_time = 0
    ha = dset['times'][()]

    tmad = get_tmad_slice(dset['times'][()], dset['addrs'][()], start_time, T*1000)
    tmad[:,0]-=tmad[0,0]
    return tmad, label

def create_datasets(
        root = 'data/IITM/IITM.hdf5',
        batch_size = 72 ,
        chunk_size_train = 300,
        chunk_size_test = 300,
        ds = 2,
        dt = 1000,
        transform_train = None,
        transform_test = None,
        target_transform_train = None,
        target_transform_test = None):

    size = [2, 128//ds, 128//ds]

    if transform_train is None:
        transform_train = Compose([
            Downsample(factor=[dt,1,ds,ds]),
            ToCountFrame(T = chunk_size_train, size = size),
            ToTensor()])
    if transform_test is None:
        transform_test = Compose([
            Downsample(factor=[dt,1,ds,ds]),
            ToCountFrame(T = chunk_size_test, size = size),
            ToTensor()])
    if target_transform_train is None:
        target_transform_train =Compose([Repeat(chunk_size_train), toOneHot(10)])   #10 class
    if target_transform_test is None:
        target_transform_test = Compose([Repeat(chunk_size_test), toOneHot(10)])

    train_ds = IITMDataset(root,train=True,
                                 transform = transform_train, 
                                 target_transform = target_transform_train, 
                                 chunk_size = chunk_size_train,
                                 dt = dt)

    test_ds = IITMDataset(root, transform = transform_test, 
                                 target_transform = target_transform_test, 
                                 train=False,
                                 chunk_size = chunk_size_test,
                                 dt = dt)

    return train_ds, test_ds

def create_dataloader(
        root = 'data/IITM/IITM.hdf5',
        batch_size = 72 ,
        chunk_size_train = 300,
        chunk_size_test = 300,
        ds = 2,
        dt = 1000,
        transform_train = None,
        transform_test = None,
        target_transform_train = None,
        target_transform_test = None,
        **dl_kwargs):

    train_d, test_d = create_datasets(
        root = 'data/IITM/IITM.hdf5',
        batch_size = batch_size,
        chunk_size_train = chunk_size_train,
        chunk_size_test = chunk_size_test,
        ds = ds,
        dt = dt,
        transform_train = transform_train,
        transform_test = transform_test,
        target_transform_train = target_transform_train,
        target_transform_test = target_transform_test)


    train_dl = torch.utils.data.DataLoader(train_d, shuffle=True, batch_size=batch_size, **dl_kwargs)
    test_dl = torch.utils.data.DataLoader(test_d, shuffle=False, batch_size=batch_size, **dl_kwargs)

    return train_dl, test_dl



