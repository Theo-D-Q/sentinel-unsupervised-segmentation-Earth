import numpy as np
import tifffile
from supercloudUtils import train_model, segment_image
import matplotlib.pyplot as plt
import torch
from time import perf_counter
import warnings 
warnings.filterwarnings('ignore')
import json
import os




def hypergrid_run(sentinel2_filepath, sentinel1_filepath, fnames, area):
    i = 0
    tic = perf_counter()
    for fname in fnames: 
        name_list = [area]  
        training_img = []
        if "sent1VV" in fname:
            img = tifffile.imread(sentinel1_filepath)
            training_img.append(img[:,:,0])
            name_list.append('sent1VV')
        if "sent2R" in fname:
            img = tifffile.imread(sentinel2_filepath)
            training_img.append(img[:,:,3])
            name_list.append('sent2R')
        if "sent2G" in fname:
            img = tifffile.imread(sentinel2_filepath)
            training_img.append(img[:,:,2])
            name_list.append('sent2G')
        if "sent2B" in fname:
            img = tifffile.imread(sentinel2_filepath)
            training_img.append(img[:,:,1])
            name_list.append('sent2B')
        if "sent2B01" in fname:
            img = tifffile.imread(sentinel2_filepath)
            training_img.append(img[:,:,0])
            name_list.append('sent2B01')
        if "sent2B05" in fname:
            img = tifffile.imread(sentinel2_filepath)
            training_img.append(img[:,:,4])
            name_list.append('sent2B05')
        if "sent2B06" in fname:
            img = tifffile.imread(sentinel2_filepath)
            training_img.append(img[:,:,5])
            name_list.append('sent2B06')
        if "sent2B07" in fname:
            img = tifffile.imread(sentinel2_filepath)
            training_img.append(img[:,:,6])
            name_list.append('sent2B07')
        if "sent2B08" in fname:
            img = tifffile.imread(sentinel2_filepath)
            training_img.append(img[:,:,7])
            name_list.append('sent2B08')
        if "sent2B8A" in fname:
            img = tifffile.imread(sentinel2_filepath)
            training_img.append(img[:,:,8])
            name_list.append('sent2B8A')
        if "sent2B09" in fname:
            img = tifffile.imread(sentinel2_filepath)
            training_img.append(img[:,:,9])
            name_list.append('sent2B09')
        if "sent2B11" in fname:
            img = tifffile.imread(sentinel2_filepath)
            training_img.append(img[:,:,10])
            name_list.append('sent2B11')
        if "sent2B12" in fname:
            img = tifffile.imread(sentinel2_filepath)
            training_img.append(img[:,:,11])
            name_list.append('sent2B12')
        print(np.shape(training_img))

        if ~np.any(training_img): # handle the case where no data is selected
            continue

        s = np.shape(training_img) # need at least 2 channels I guess?
        if s[0] <= 1:
            continue
        print('Put data into array')
        
        training_img = np.transpose(training_img,(1,2,0))
        print('Transposed array')
        
        trainingEpochs = 4
        batchSize = 8
        finalFeatures_grid = [6,4,8,10]
        patchSize_grid = [448,336,224,112]
        
        finalFeatures = finalFeatures_grid[0]
        patchSize = patchSize_grid[2]
        tic_inner = perf_counter()
        
        hyper_str = "_ff" + str(finalFeatures) + "_ps" + str(patchSize)
        
        if not os.path.exists('./ML_set01/trainedModels/hypergrid_sparse/'):
            os.makedirs('./ML_set01/trainedModels/hypergrid_sparse/')
        
        if not os.path.exists('./ML_set01/results/hypergrid_sparse/'):
            os.makedirs('./ML_set01/results/hypergrid_sparse/')
        
        saveModelPath = './ML_set01/trainedModels/hypergrid_sparse/' + '_'.join(name_list) + hyper_str + '.pth'
        saveResultPath = './ML_set01/results/hypergrid_sparse/' + '_'.join(name_list) + hyper_str + '.png'
        
        model = train_model(training_img,trainingEpochs=trainingEpochs,batchSize=batchSize,
                            finalFeatures=finalFeatures,patchSize=patchSize) # Train model
        torch.save(model,saveModelPath) # Save model
        #model = torch.load(saveModelPath)
        result = segment_image(training_img, model) # Segment image
        plt.imsave(saveResultPath,result) # Save segmented image

        toc_inner = perf_counter()
        i = i+1
        print("Iteration ",i," complete in %.2f minutes" % round((toc_inner-tic_inner)/(60),2))


    toc = perf_counter()
    print("Iterations:",i)
    print("Elapsed: %.2f s" % round((toc-tic),2))
    print("Elapsed: %.2f min" % round((toc-tic)/60,2))
    print("Elapsed: %.2f hr" % round((toc-tic)/(60*60),2))
    print("Elapsed: %.2f day" % round((toc-tic)/(60*60*24),2))
    print("Minutes per iteration: %.2f" % round(((toc-tic)/(60))/i,2))