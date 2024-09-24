import numpy as np
import tifffile
from supercloudUtils import train_model, segment_image
import matplotlib.pyplot as plt
import torch
from time import perf_counter
import warnings 
warnings.filterwarnings('ignore')

# ctxIMG, ctxDEM, ctxSLOPE, dayIR, nightIR, hrscND, hrscP1, hrscP2, hrscS1, hrscS2 = np.ones(10)
hrscS2 = 1

i = 0
tic = perf_counter()
for ctxIMG in range(2):
    for ctxDEM in range(2):
        for ctxSLOPE in range(2):
            for dayIR in range(2):
                for nightIR in range(2):
                    for hrscND in range(2):
                        for hrscP1 in range(2):
                            for hrscP2 in range(2):
                                for hrscS1 in range(2):
                                    tic_inner = perf_counter()
                                    name_list = []
                                    training_img = []
                                    if ctxIMG:
                                        img = tifffile.imread('../ML_set01/data/biggridData/ctxIMG.tif')
                                        training_img.append(img)
                                        name_list.append('ctxIMG')
                                    if ctxDEM:
                                        img = tifffile.imread('../ML_set01/data/biggridData/ctxDEM.tif')
                                        training_img.append(img)
                                        name_list.append('ctxDEM')
                                    if ctxSLOPE:
                                        img = tifffile.imread('../ML_set01/data/biggridData/ctxSLOPE.tif')
                                        training_img.append(img)
                                        name_list.append('ctxSLOPE')
                                    if dayIR:
                                        img = tifffile.imread('../ML_set01/data/biggridData/dayIR.tif')
                                        training_img.append(img)
                                        name_list.append('dayIR')
                                    if nightIR:
                                        img = tifffile.imread('../ML_set01/data/biggridData/nightIR.tif')
                                        training_img.append(img)
                                        name_list.append('nightIR')
                                    if hrscND:
                                        img = tifffile.imread('../ML_set01/data/biggridData/hrscND.tif')
                                        training_img.append(img)
                                        name_list.append('hrscND')
                                    if hrscP1:
                                        img = tifffile.imread('../ML_set01/data/biggridData/hrscP1.tif')
                                        training_img.append(img)
                                        name_list.append('hrscP1')
                                    if hrscP2:
                                        img = tifffile.imread('../ML_set01/data/biggridData/hrscP2.tif')
                                        training_img.append(img)
                                        name_list.append('hrscP2')
                                    if hrscS1:
                                        img = tifffile.imread('../ML_set01/data/biggridData/hrscS1.tif')
                                        training_img.append(img)
                                        name_list.append('hrscS1')
                                    if hrscS2:
                                        img = tifffile.imread('../ML_set01/data/biggridData/hrscS2.tif')
                                        training_img.append(img)
                                        name_list.append('hrscS2')

                                    if ~np.any(training_img): # handle the case where no data is selected
                                        continue

                                    s = np.shape(training_img) # need at least 2 channels I guess?
                                    if s[0] <= 1:
                                        continue
                                        
                                    training_img = np.transpose(training_img,(1,2,0))
                                    saveModelPath = '../ML_set01/trainedModels/biggrid_ctx/' + '_'.join(name_list) + '.pth'
                                    saveResultPath = '../ML_set01/results/biggrid_ctx/' + '_'.join(name_list) + '.png'
                                    model = train_model(training_img) # Train model
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