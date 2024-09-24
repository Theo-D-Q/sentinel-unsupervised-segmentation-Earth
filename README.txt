This set of code will download sentinel-2 and sentinel-1 satellite imagery from sentinelhub api and/or run the model defined in networksVaryingKernel.
The main file you need to run is 'model_pipeline.py'. You have the option of downloading images and/or running the model.

******* PREREQUISITES *******
The python dependencies used during the coding fo this project are listed in dependencies.txt. GDAL was installed using Homebrew
You will need to define an area you are investigating in location_list.json
You will also have to update you sentinelhub client credentials in client_credentials.json. Go to the section below for further information

******* DOWNLOADING *******
Images will not be downloaded if the system detects a tif file is already present in the location folder
You have the option of downloading sentinel-1 data alongside sentinel-2 data
The program will initially attempt to download the image in one go. If the api deems the area too large, the tile-splitter method will be used instead

******* RUNNING MODEL *******
In supercloudUtils.py you can change the parameters of the model. You can also change where the results are saved.
In image_layers.csv you can add or change which sentinel-1 & 2 layers you want to run your model with for data analysis. The model will run once for each line.

******* CREDENTIALS *******
If you need to downlaod sentinelhub data, please use your sentinelhub API credentials.
You can input them into client_credentials.json
If you have done so yet, please create an account at: https://www.sentinel-hub.com/develop/api/, or read https://sentinelhub-py.readthedocs.io/en/latest/configure.html

******* USEFUL UTILTIES *******
If you need to plot an RGB image for sentinel-2 data, use the function defined in utils.py. It looks like:
    img = tifffile.imread('sentinel-2_file.tif')
    plot_image(img[:,:,[3,2,1]], factor = 3.5/1e4, vmax = 1)
The layers 1-3 can be substituted with any other layers; factor increases or decreases brightness.

******* IMPORTANT *******
The code for the unsupervised learning model was written by Sudipan Saha (GitHub: sudipansaha).
Citation: Saha et al, 2022