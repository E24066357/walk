from ctypes import *
import random
from os import listdir
from os.path import isfile, isdir, join
import time
from queue import Queue
from collections import defaultdict
import csv
import pandas as pd
import numpy as np
import ast
import json
from PIL import Image
#import imagehash
import hashlib
import math
from statsmodels.tsa.api import ExponentialSmoothing, Holt, SimpleExpSmoothing

freewalk = [
    'freewalk_1',
]
walk_list = freewalk


def signed_encode(hash_):
    # signed compute
    hash_ = np.where(hash_ > 0, hash_, 0)
    hash_ = np.where(hash_ <= 0, hash_, 1)

    return hash_.astype(int)


def text_hash(beacon_id, RSSI):
    # print(type(beacon_id))
    # print(type(RSSI))
    # if walk_list == freewalk :
    RSSI_2 = 3*RSSI*RSSI + 2*RSSI*RSSI*RSSI + 1*RSSI*RSSI*RSSI*RSSI  # freewalk
    # if walk_list == scripted_walk :
    #   RSSI_2 = 1*RSSI + 3*RSSI*RSSI*RSSI + 2*RSSI*RSSI*RSSI*RSSI       #scripted_walk
    #RSSI_2 = 3*RSSI*RSSI*RSSI
    weight = abs(RSSI_2*10)

    text_ = hashlib.blake2b(beacon_id.encode()).hexdigest()
    #text_ = hashlib.sha256(beacon_id.encode()).hexdigest()
    text_encode = np.array([])

    for x in text_:
        value_ = int(x, base=16)
        tmp = '{0:04b}'.format(value_)
        value_list = [int(char) for char in tmp]
        text_encode = np.append(text_encode, value_list)
        text_encode = text_encode.astype(int)

    # weighted
    text_encode = np.where(text_encode < 0, text_encode, text_encode*weight)
    text_encode = np.where(text_encode > 0, text_encode, -1*weight)

    return text_encode


def similarity(hash1_, hash2_):
    # print(hash1_)
    # print(hash2_)
    # print(abs(hash1_-hash2_).sum())
    #print('len of hash1:',len(hash1_))
    # return 1 - abs(hash1_-hash2_).sum()/len(hash1_)
    return 1 - (((abs(hash1_ - hash2_)).sum())/len(hash1_))


# Wireless Train Hashing
name_type = 'beacon'
wireless_path = f'./walk_data/'
Wireless_Train = pd.read_csv(join(wireless_path, 'wireless_training_set.csv'))

list_of_Wireless_Train_hash = []
train_label = []
print(Wireless_Train.shape)
print(len(Wireless_Train))
for i in range(len(Wireless_Train)):
    Wireless_Train_row = Wireless_Train.iloc[i].to_dict()
    Wireless_Train_row_label = Wireless_Train_row['label']
    train_label.append(Wireless_Train_row_label)
    Wireless_Train_row.pop('label', None)
    # device1 hash encode
    Wireless_Train_hash = np.array([])
    for beacon_id, RSSI in Wireless_Train_row.items():
        hash_ = text_hash(beacon_id, RSSI)  # 每一個RSSI值被hash成一個大小512的array
        if len(Wireless_Train_hash) < 1:
            Wireless_Train_hash = hash_
        else:
            # 每個RSSI hash完的512array 8個array數值疊加起來(大小還是512)
            Wireless_Train_hash = Wireless_Train_hash + hash_

    Wireless_Train_hash = signed_encode(Wireless_Train_hash)
    list_of_Wireless_Train_hash.append(Wireless_Train_hash)


# Test Hashing 一起討論後推舉出候選人投票 寫給 image &pf
list_MDE = []
total_DE = 0
len_of_all_label = 0
K = 45

error_distri = [0]*16


hash_similarity = []
#list_of_Wireless_Train_hash_dic = list(Wireless_Train_hash_dic.values())

test_label = []
predict_label = []


# Wireless_Test = pd.read_csv(
#    join(f'./walk_data/wireless_fingerprint_avg_10_7_beacon_rate_10.csv'))
Wireless_Test = {'Beacon_1': 0.594202899, 'Beacon_2': 0.710144928, 'Beacon_3': 0.260869565,
                 'Beacon_4': 0.449275362, 'Beacon_5': 0.275362319, 'Beacon_6': 0.405797101, 'Beacon_7': 0.333333333, }
Wireless_Test_hash = np.array([])
for beacon_id, RSSI in Wireless_Test.items():
    hash_ = text_hash(beacon_id, RSSI)
    if len(Wireless_Test_hash) < 1:
        Wireless_Test_hash = hash_  # 因為0和512長度 不能相加
    else:
        Wireless_Test_hash = Wireless_Test_hash + hash_
Wireless_Test_hash = signed_encode(Wireless_Test_hash)
print(Wireless_Test_hash)
'''
for j in range(len(Wireless_Test)):
    # Device1
    Wireless_Test_row = Wireless_Test.iloc[j].to_dict()
    Wireless_Test_row_label = Wireless_Test_row['label']
    test_label.append(Wireless_Test_row_label)
    Wireless_Test_row.pop('label', None)

    # device1 hash encode
    Wireless_Test_hash = np.array([])
    for beacon_id, RSSI in Wireless_Test_row.items():
        hash_ = text_hash(beacon_id, RSSI)
        if len(Wireless_Test_hash) < 1:
            Wireless_Test_hash = hash_
        else:
            Wireless_Test_hash = Wireless_Test_hash + hash_
# Device1

    Wireless_Test_hash = signed_encode(Wireless_Test_hash)
'''
# 找出 Top K 個像的
k_top_similarity = [0.0]*K
voter = [0.0]*K
for k in range(len(list_of_Wireless_Train_hash)):
    sim_ = similarity(
        list_of_Wireless_Train_hash[k], Wireless_Test_hash)
    if sim_ > (min(k_top_similarity)):
        k_top_similarity[k_top_similarity.index(
            min(k_top_similarity))] = sim_
        voter[k_top_similarity.index(
            min(k_top_similarity))] = train_label[k]

# for m in range(len(voter_device2)):
    # voter.append(voter_device2[m])

# 將 similarity 做為 voter 的加權
vote = [0.0]*42
for i in range(len(voter)):
    vote[int(voter[i])] += k_top_similarity[i]

# print(k_top_similarity)
# print(voter)

#writer.writerow([Wireless_Test_row_label, voter])

predict_label.append(max(voter, key=voter.count))  # 票票等值
# predict_label.append(vote.index(max(vote))) # 票票不等值 similarity 為權重
#print("Ground Truth :", Wireless_Test_row_label)
print("predict_label :", max(voter, key=voter.count))
