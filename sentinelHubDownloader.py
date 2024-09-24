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
from tifffile import tifffile
from utils import plot_image

def extract_required_metadata(search_results):
    # Adjust metadata extraction for Sentinel-2 specifics (e.g., cloud cover)
    top_tiles = search_results[:3]
    metadata_list = []
    for search_result in top_tiles:
        metadata = {
            'id': search_result['id'],
            'date_time': search_result['properties']['datetime'],
            'cloud_coverage': search_result['properties'].get('eo:cloud_cover', None),
            'platform': search_result['properties']['platform']
        }
        metadata_list.append(metadata)
    return metadata_list

def store_metadata(metadata_list, directory):
    metadata_file = os.path.join(directory, "detailed_metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata_list, f)

def download_sentinel2_data_batch(boundingbox, area, resolution, start_date, end_date, config, export_folder):
    crs=CRS.WGS84
    bbox = box(boundingbox[0], boundingbox[1], boundingbox[2], boundingbox[3])
    assert isinstance(bbox, Polygon)
    tile_splits = UtmZoneSplitter([bbox], crs, (2500, 25000))
    resolution_tuple = (resolution, resolution)

    if not os.path.exists(export_folder):
        os.makedirs(export_folder)
    
    evalscript_all_bands = """
        //VERSION=3
        function setup() {
            return {
                input: [{
                    bands: ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B11", "B12", "dataMask"],
                units: "DN"
                }],
                output: { bands: 13, sampleType: "INT16" }
            };
        }
        function evaluatePixel(sample) {
            return [sample.B01, sample.B02, sample.B03, sample.B04, sample.B05, sample.B06, sample.B07, sample.B08, sample.B8A, sample.B09, sample.B11, sample.B12, sample.dataMask];
        }
    """
    

    bbox_list = tile_splits.get_bbox_list()
    for tile_bbox in bbox_list:
        request = SentinelHubRequest(
                                data_folder=export_folder,
                                evalscript=evalscript_all_bands,
                                input_data=[SentinelHubRequest.input_data(
                                            data_collection=DataCollection.SENTINEL2_L2A,
                                            time_interval=(start_date, end_date),
                                            mosaicking_order=MosaickingOrder.LEAST_CC)],
                                responses=[SentinelHubRequest.output_response('default', MimeType.TIFF)],
                                bbox=tile_bbox, 
                                resolution=resolution_tuple,
                                config=config)
        # dl_request = request.download_list[0]
        # downloaded_data = SentinelHubDownloadClient(config=config).download([dl_request], max_threads=6)
        data = request.save_data() 
    print(f"Downloaded sentinel-2 data for area: {area} using tile-splitter")

def download_sentinel1_data_batch(boundingbox, area, resolution, start_date, end_date, config, export_folder):
    crs=CRS.WGS84
    bbox = box(boundingbox[0], boundingbox[1], boundingbox[2], boundingbox[3])
    assert isinstance(bbox, Polygon)
    tile_splits = UtmZoneSplitter([bbox], crs, (2500, 25000))
    resolution_tuple = (resolution, resolution)

    if not os.path.exists(export_folder):
        os.makedirs(export_folder)
    
    evalscript_sentinel1_IW = """
        //VERSION=3

        return [VV, 2 * VH, VV / VH / 100.0, dataMask]
        """

    bbox_list = tile_splits.get_bbox_list()
    for tile_bbox in bbox_list:
        request = SentinelHubRequest(
                                data_folder=export_folder,
                                evalscript=evalscript_sentinel1_IW,
                                input_data=[SentinelHubRequest.input_data(
                                            data_collection=DataCollection.SENTINEL1_IW,
                                            time_interval=(start_date, end_date),
                                            )],
                                responses=[SentinelHubRequest.output_response('default', MimeType.TIFF)],
                                bbox=tile_bbox, 
                                resolution=resolution_tuple,
                                config=config)
        # dl_request = request.download_list[0]
        # downloaded_data = SentinelHubDownloadClient(config=config).download([dl_request], max_threads=6)
        data = request.save_data() 
    print(f"Downloaded sentinel-1 data for area: {area} using tile-splitter")

def merge_tifs(output_folder, area, output_file):
    tiff_files = glob(f"{output_folder}/**/*.tiff")

    if not tiff_files:
        raise ValueError("No TIFF files found for specified directory.")
    
    # File paths for VRT and GeoTIFF
    vrt_filepath = output_file.replace(".tif", ".vrt")

    # Check if the VRT file already exists
    if not os.path.exists(vrt_filepath):
        # Create the VRT (Virtual Raster)
        options = gdal.BuildVRTOptions()
        asc_mosaic_vrt = gdal.BuildVRT(vrt_filepath, tiff_files, options=options)
        
        if asc_mosaic_vrt is None:
            raise RuntimeError("Failed to build the VRT. Check the input files and paths.")
        
        asc_mosaic_vrt.FlushCache()
        print(f"Created VRT file: {vrt_filepath}")
    else:
        print(f"VRT file already exists: {vrt_filepath}")

    #asc_mosaic_vrt = gdal.BuildVRT(sentinel2_filepath.replace(".tif", ".vrt"), files, options=options)
    #asc_mosaic_vrt.FlushCache()
    cmd = f"gdalwarp -overwrite -of GTiff -co 'COMPRESS=LZW' -co 'BIGTIFF=YES' -co 'TILED=YES' -co 'NUM_THREADS=ALL_CPUS'\
            -co 'SPARSE_OK=TRUE' -t_srs EPSG:4326 -srcnodata 0 {output_file.replace(".tif", ".vrt")} {output_file}"
    os.system(cmd)
    print(f'merging of tifs in {output_folder} was successful')


def reproject_tifs(sentinel2_filepath, sentinel1_filepath):
    reprojected_sentinel2_filepath = sentinel2_filepath.replace(".tif","-reprojected.tif")
    reprojected_sentinel1_filepath = sentinel1_filepath.replace(".tif","-reprojected.tif")
    sent1 = rioxarray.open_rasterio(sentinel1_filepath)
    sent2 = rioxarray.open_rasterio(sentinel2_filepath)
    sentinel = sent1.rio.reproject_match(sent2)
    sentinel.rio.to_raster(reprojected_sentinel1_filepath)
    print('reprojection was successful')

if __name__ == "__main__":
    # set up sentinel-hub api
    # config = SHConfig()
    # config.sh_client_id = client_id
    # config.sh_client_secret = client_secret
    # config.instance_id = instance_id
    # config.save()
    
    death_valley_coords = [-117.00, 35.84, -116.50, 36.34] # Example coordinates
    area = "death_valley_subsection"
    start_date = "2024-04-01"
    end_date = "2024-07-01"
    resolution = 10 

    root = "data"
    output_folder_sentinel2 = os.path.join(root,"sentinel2")
    output_folder_sentinel1 = os.path.join(root,"sentinel1")
    # images = download_sentinel2_data(DEATH_VALLEY_COORDS, area, resolution, start_date, end_date, config, output_folder)

    sentinel2_filepath = os.path.join(output_folder_sentinel2,area,"sentinel-2.tif")
    sentinel1_filepath = os.path.join(output_folder_sentinel1,area,"sentinel-1.tif")
    #dem_filepath = os.path.join(root,"topography","death_valley_dem.tif")
    #download_sentinel2_data_batch(death_valley_coords, area, resolution, start_date, end_date, config, output_folder_sentinel2)
    #download_sentinel1_data_batch(death_valley_coords, area, resolution, start_date, end_date, config, output_folder_sentinel1)

    #merge_tifs_batch(output_folder_sentinel2,output_folder_sentinel1, area, sentinel2_filepath, sentinel1_filepath)
    
