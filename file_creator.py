import os
def fileCreator():
    if not os.path.exists('./data'):
        os.mkdir('./data')

    if not os.path.exists('./data/sentinel2'):
        os.mkdir('./data/sentinel2')

    if not os.path.exists('./data/sentinel1'):
        os.mkdir('./data/sentinel1')

    if not os.path.exists('./ML_set01/trainedModels'):
        os.mkdir('./ML_set01/trainedModels')
        
    if not os.path.exists('./ML_set01/results'):
        os.mkdir('./ML_set01/results')
