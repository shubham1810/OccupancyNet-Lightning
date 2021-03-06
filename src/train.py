import os
import glob
import cv2
import random
import pandas as pd
from skimage import io
import numpy as np
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils
import h5py
import argparse

# Network building stuff
import torch
import torch.nn as nn
import torch.nn.functional as F

import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.callbacks import ModelCheckpoint
import torchmetrics

from models import *
from dataset.dataloader import OccupancyNetDatasetHDF
from trainer import ONetLit
from utils import Config, count_parameters


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argument parser for training the model")
    parser.add_argument('--cdim', action='store', type=int, default=128, help="feature dimension")
    parser.add_argument('--hdim', action='store', type=int, default=128, help="hidden size for decoder")
    parser.add_argument('--pdim', action='store', type=int, default=3, help="points input size for decoder")
    parser.add_argument('--data_root', action='store', type=str, default="/ssd_scratch/cvit/sdokania/hdf_shapenet/hdf_data/", help="location of the parsed and processed dataset")
    parser.add_argument('--batch_size', action='store', type=int, default=64, help="Training batch size")
    parser.add_argument('--output_path', action='store', type=str, default="/home2/sdokania/all_projects/occ_artifacts/", help="Model saving and checkpoint paths")
    parser.add_argument('--exp_name', action='store', type=str, default="initial", help="Name of the experiment. Artifacts will be created with this name")
    parser.add_argument('--encoder', action='store', type=str, default="efficientnet-b0", help="Name of the Encoder architecture to use")
    parser.add_argument('--decoder', action='store', type=str, default="decoder-cbn", help="Name of the decoder architecture to use")
    
    args = parser.parse_args()
    # Get the model configuration
    config = Config(args)
    
    # Define the lightning module
    onet = ONetLit(config)
    
    # Initialize tensorboard logger
    logger = TensorBoardLogger(
        save_dir=config.exp_path,
        version=1,
        name="lightning_logs"
    )

    # Initialize the checkpoint module
    checkpoint_callback = ModelCheckpoint(
        monitor="val_loss",
        mode="min",
        save_top_k=3
    )
    
    # Define the trainer object
    trainer = pl.Trainer(
        gpus=1,
        # auto_scale_batch_size='binsearch',
        logger=logger,
        min_epochs=1,
        max_epochs=200,
        default_root_dir=config.output_dir,
        log_every_n_steps=10,
        progress_bar_refresh_rate=5,
        # precision=16,
        # stochastic_weight_avg=True,
        # track_grad_norm=2,
        callbacks=[checkpoint_callback],
        check_val_every_n_epoch=1,
    )
    
    # Start training
    trainer.fit(onet)
