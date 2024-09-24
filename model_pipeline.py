from sentinelhub import SHConfig
import os
import json
from glob import glob 
import numpy as np
import matplotlib.pyplot as plt
from utils import plot_image
import tifffile
import json
import shutil
import csv
from model_run_test import hypergrid_run
from sentinelHubSmallDownloader import download_sentinel1_data, download_sentinel2_data
from sentinelHubDownloader import download_sentinel1_data_batch, download_sentinel2_data_batch, merge_tifs, reproject_tifs
from file_creator import fileCreator

def load_location(location_name): # load the required data about the desired location
    with open('location_list.json', 'r') as file:
        locations = json.load(file)
        return locations.get(location_name)
    
def load_credentials():
    with open('client_credentials.json', 'r') as file:
        credentials = json.load(file)
        return credentials.get("client_credentials")

def copy_and_rename(src_path, dest_path, new_name):
    # Copy the file
    shutil.copy(src_path, dest_path)
    # Rename the copied file
    new_path = f"{dest_path}/{new_name}"
    shutil.move(f"{dest_path}/response.tiff", new_path)
    print(f'{new_name} was moved to {dest_path} successfully')

def download_script(location_data, area, sentinel2_output_folder, sentinel1_output_folder,sentinel2_filepath,sentinel1_filepath, get_sentinel1 = True):
    credentials = load_credentials()
    client_id = credentials['client_id']
    client_secret = credentials['client_secret']
    instance_id = credentials['instance_id']

    # set up sentinel-hub api
    config = SHConfig()
    config.sh_client_id = client_id
    config.sh_client_secret = client_secret
    config.instance_id = instance_id
    config.save()
    
    # variables
    boundingbox = location_data['coordinates']
    start_date = location_data['start_date']
    end_date = location_data['end_date']
    resolution = 10

    if not os.path.exists(sentinel2_filepath):
        download_sentinel2_data(boundingbox, area, resolution, start_date, end_date, config, sentinel2_output_folder)
        # check if files were successfully downloaded in case image request was too large
        files = glob(f"{sentinel2_output_folder}/**/*.tiff")
        if any(files):
            try:
                print('Sentinel-2 img was downloaded successfully')
                copy_and_rename(files[0], sentinel2_output_folder, 'sentinel-2.tif') # moves tif tile into main directory
            except:
                print('Sentinel-2 img was not copied into area directory successfully')
    else:
        print('Sentinel-2 file already exists in directory')
    if get_sentinel1 and not os.path.exists(sentinel1_filepath): # in case sentinel-1 data is being requested
        download_sentinel1_data(boundingbox, area, resolution, start_date, end_date, config, sentinel1_output_folder)
        files = glob(f"{sentinel1_output_folder}/**/*.tiff")
        if any(files):
            try:
                print('Sentinel-1 img was downloaded successfully')
                copy_and_rename(files[0], sentinel1_output_folder, 'sentinel-1.tif')
                reproject_tifs(sentinel2_filepath, sentinel1_filepath)
            except:
                print('Sentinel-1 img could not be copied into directory and reprojected')
    elif not get_sentinel1:
        pass
    else:
        print('Sentinel-1 file already exists in directory')
    if not(any(glob(f"{sentinel2_output_folder}/**/*.tiff"))): # will only go through if files were not downloaded
        # download using the tilebox splitting function instead
        download_sentinel2_data_batch(boundingbox, area, resolution, start_date, end_date, config, sentinel2_output_folder)
        # merge downloaded tifs
        if any(glob(f"{sentinel2_output_folder}/**/*.tiff")) and not os.path.exists(sentinel2_filepath):
            merge_tifs(sentinel2_output_folder, area, sentinel2_filepath)
    if not(any(glob(f"{sentinel1_output_folder}/**/*.tiff"))) and get_sentinel1:
        download_sentinel1_data_batch(boundingbox, area, resolution, start_date, end_date, config, sentinel1_output_folder)
        if any(glob(f"{sentinel1_output_folder}/**/*.tiff")) and not os.path.exists(sentinel1_filepath):
            merge_tifs(sentinel1_output_folder, area, sentinel1_filepath)
            reproject_tifs(sentinel2_filepath, sentinel1_filepath)

        
if __name__ == "__main__":
    fileCreator()
    download_data = True
    get_sentinel1 = True
    run_model = False
    # Load and print specific locations
    location_data = load_location("death_valley_large_test")

    death_valley_coords = location_data['coordinates'] # Coordinates
    area = location_data['area'] # Name of area 

    root = "data"
    sentinel2_output_folder = os.path.join(root,"sentinel2",area)
    sentinel1_output_folder = os.path.join(root,"sentinel1",area)
    
    sentinel2_filepath = os.path.join(sentinel2_output_folder,"sentinel-2.tif")
    sentinel1_filepath = os.path.join(sentinel1_output_folder,"sentinel-1.tif")

    reprojected_sentinel2_filepath = os.path.join(sentinel2_output_folder,"sentinel-2-reprojected.tif")
    reprojected_sentinel1_filepath = os.path.join(sentinel1_output_folder,"sentinel-1-reprojected.tif")    
    
    if download_data:
        try:
            download_script(location_data, area, sentinel2_output_folder, sentinel1_output_folder,sentinel2_filepath,sentinel1_filepath, get_sentinel1)
        except ValueError:
            raise ValueError('Sentinelhub client credentials have not been input. Please documentation for more information on how to set up an account.')
        except AttributeError:
            raise ValueError('Sentinelhub client credentials are invalid. Please read documentation on how to set up an account')        

    # now we run our model
    if run_model:
        with open('image_layers.csv', 'r') as f:
            reader = csv.reader(f)
            fnames = np.array(list(reader))[0]
        hypergrid_run(sentinel2_filepath, reprojected_sentinel1_filepath, fnames, area)


