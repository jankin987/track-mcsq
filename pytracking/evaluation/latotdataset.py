import os
import json
import numpy as np
from pytracking.evaluation.data import Sequence, BaseDataset, SequenceList
from pytracking.utils.load_text import load_text
from PIL import Image
from pathlib import Path


class LaTOTDataset(BaseDataset):
    """
    LaSOT test set consisting of 280 videos (see Protocol-II in the LaSOT paper)

    Publication:
        LaSOT: A High-quality Benchmark for Large-scale Single Object Tracking
        Heng Fan, Liting Lin, Fan Yang, Peng Chu, Ge Deng, Sijia Yu, Hexin Bai, Yong Xu, Chunyuan Liao and Haibin Ling
        CVPR, 2019
        https://arxiv.org/pdf/1809.07845.pdf

    Download the dataset from https://cis.temple.edu/lasot/download.html
    """
    def __init__(self, vos_mode=False, attribute=None):
        super().__init__()
        self.base_path = self.env_settings.latot_path
        self.sequence_info_list = self._get_sequence_info_list()

    def get_sequence_list(self):
        return SequenceList([self._construct_sequence(s) for s in self.sequence_info_list])

    def _construct_sequence(self, sequence_info):
        sequence_path = sequence_info["path"]
        imgs = os.listdir(os.path.join(self.base_path, sequence_path))
        frames = list()
        for img in sorted(imgs):
            imgpath = os.path.join(sequence_path, img)
            # print(imgpath)
            frames.append(os.path.join(self.base_path, imgpath))
        
        init_omit = 0
        if 'initOmit' in sequence_info:
            init_omit = sequence_info['initOmit']
        anno_path = '{}/{}'.format(self.base_path, sequence_info['anno_path'])
        # NOTE: OTB has some weird annos which panda cannot handle
        ground_truth_rect = load_text(str(anno_path), delimiter=(',', None), dtype=np.float64, backend='numpy')

        return Sequence(sequence_info['name'], frames, 'otb', ground_truth_rect[init_omit:, :],
                        object_class=sequence_info['object_class'])
    
    def __len__(self):
        return len(self.sequence_info_list)


    def _get_sequence_info_list(self):
        
        sequence_dir = []
        sequence_path = []

        for root, dirs, files in os.walk(self.base_path):
            for dir in dirs:
                if dir == 'img':
                # if dir == 'img': # filter the img direction
                    continue
                sequence_dir.append(dir) # restore sequence direction
                sequence_path.append(os.path.join(root, dir)) # restore sequence dircetion path
        sequence_dir = sorted(sequence_dir)
        sequence_path = sorted(sequence_path)
        img_path = []
        end_frame = []
        # print('seq: ',sequence_path)
        for path in sequence_path:

            for root, dirs, files in os.walk(path):
                for dir in dirs:
                    img_path.append(os.path.join(root, dir))
        
        for img_p in img_path:
            # print('img: ',img_p)
            # for root, dirs, files in os.walk(img_p):
            files = os.listdir(img_p)
            end_frame.append(len(files))
        sequence_info_list = []
        for i in range(len(sequence_dir)):
            sequence_info = {}
            sequence_info["name"] = sequence_dir[i] 
            sequence_info["path"] = sequence_dir[i]+'/img'
            sequence_info["startFrame"] = int('1')
            sequence_info["endFrame"] = end_frame[i]
                
            sequence_info["nz"] = int('6')
            sequence_info["ext"] = 'jpg'
            sequence_info["anno_path"] = os.path.join(sequence_dir[i], sequence_info["name"]+'.txt')
            sequence_info["object_class"] = 'person'
            sequence_info_list.append(sequence_info)    
        return sequence_info_list


