from sentinelhub import (SHConfig, CRS, BBox, UtmZoneSplitter, DataCollection,
                        MimeType, MosaickingOrder, SentinelHubRequest, 
                        bbox_to_dimensions, Geometry, SentinelHubDownloadClient)
import os
import json
from shapely.geometry import MultiLineString, MultiPolygon, Polygon, box, shape
import geopandas as gpd
from glob import glob
from osgeo import gdal 
import rioxarray
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from utils import plot_image
import tifffile
#import imagecodecs

def download_sentinel2_data(boundingbox, area, resolution, start_date, end_date, config, export_folder):
    crs=CRS.WGS84
    bbox = BBox(bbox=boundingbox, crs=CRS.WGS84)
    bbox_size = bbox_to_dimensions(bbox, resolution=resolution)
    resolution_tuple = (resolution, resolution)
    
    evalscript_all_bands = """
        //VERSION=3
        function setup() {
            return {
                input: [{
                    bands: ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12"],
                    units: "DN"
                }],
                output: {
                    bands: 12,
                    sampleType: "INT16"
                }
            };
        }

        function evaluatePixel(sample) {
            return [sample.B01,
                    sample.B02,
                    sample.B03,
                    sample.B04,
                    sample.B05,
                    sample.B06,
                    sample.B07,
                    sample.B08,
                    sample.B8A,
                    sample.B09,
                    sample.B11,
                    sample.B12];
        }
    """
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)

    request_all_bands = SentinelHubRequest(
        data_folder=export_folder,
        evalscript=evalscript_all_bands,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=(start_date, end_date),
                mosaicking_order=MosaickingOrder.LEAST_CC,
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=bbox,
        config=config,
        size=bbox_size)
    #all_bands_img = request_all_bands.get_data(save_data=True)
    try:
        request_all_bands.save_data()
    except SentinelHubRequest.InvalidClientError:
        raise AttributeError
     
    
def download_sentinel1_data(boundingbox, area, resolution, start_date, end_date, config, export_folder):
    crs=CRS.WGS84
    bbox = BBox(bbox=boundingbox, crs=CRS.WGS84)
    bbox_size = bbox_to_dimensions(bbox, resolution=resolution)
    tile_splits = UtmZoneSplitter([bbox], crs, (2500, 25000))
    resolution_tuple = (resolution, resolution)

    if not os.path.exists(export_folder):
        os.makedirs(export_folder)
    
    evalscript_sentinel1_IW = """
        //VERSION=3

        return [VV, 2 * VH, VV / VH / 100.0]
        """


    request = SentinelHubRequest(
                            data_folder=export_folder,
                            evalscript=evalscript_sentinel1_IW,
                            input_data=[SentinelHubRequest.input_data(
                                        data_collection=DataCollection.SENTINEL1_IW,
                                        time_interval=(start_date, end_date),
                                        )],
                            responses=[SentinelHubRequest.output_response('default', MimeType.TIFF)],
                            bbox=bbox, 
                            config=config,
                            size=bbox_size)
    # dl_request = request.download_list[0]
    # downloaded_data = SentinelHubDownloadClient(config=config).download([dl_request], max_threads=6)
    try:
        data = request.save_data()
    except SentinelHubRequest.InvalidClientError:
        raise AttributeError



if __name__ == "__main__":
    # set up sentinel-hub api
    # config = SHConfig()
    # config.sh_client_id = client_id
    # config.sh_client_secret = client_secret
    # config.instance_id = instance_id
    # config.save()
    
    death_valley_area = [-116.86, 36.07, -116.73, 36.18] # Example coordinates
    area = "death_valley_small"
    start_date = "2024-06-01"
    end_date = "2024-08-01"
    resolution = 10 

    root = "data"
    output_folder_sentinel2 = os.path.join(root,"sentinel2")
    output_folder_sentinel1 = os.path.join(root,"sentinel1")
    #  images = download_sentinel2_data(DEATH_VALLEY_COORDS, area, resolution, start_date, end_date, config, output_folder)

    sentinel2_filepath = os.path.join(output_folder_sentinel2,area,"sentinel-2.tiff")
    sentinel1_filepath = os.path.join(output_folder_sentinel1,area,"sentinel-1.tiff")
    
    #download_sentinel2_data(death_valley_area, area, resolution, start_date, end_date, config, output_folder_sentinel2)
    #download_sentinel1_data(death_valley_area, area, resolution, start_date, end_date, config, output_folder_sentinel1)

    #merge_tifs(output_folder_sentinel1, area, sentinel2_filepath, sentinel1_filepath)
    
    #plot_image(img[:,:,[3,2,1]], factor = 3.5/1e4, vmax = 1)