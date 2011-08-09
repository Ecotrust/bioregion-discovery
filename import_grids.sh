#!/bin/bash
# 
# Imports Bioregional input grids from a directory of ArcInfo grids to a Grass workspace
# No command line arguments, just adjust the setting variables at the top
#
# Before running the script,  
# 1. copy the entire G:\projects\projects2011\BigIdea\Analysis\inputs\binned directory to the server
# Data should all be projected to Mollweide. 
# 
# 2. Log into Grass mapset, PERMANENT location, set region to biomass_slope
# 

export INPUT_DIR=/home/grass/binned
export OUTPUT_DIR=/home/grass/world_moll3

r.in.gdal --o input=${INPUT_DIR}/biomass_mw/hdr.adf output=biomass_slope
r.in.gdal --o input=${INPUT_DIR}/min_temp_mw/hdr.adf output=min_temp_slope
r.in.gdal --o input=${INPUT_DIR}/tmp_rng_mw/hdr.adf output=tmp_rng_slope
r.in.gdal --o input=${INPUT_DIR}/precip_mw/hdr.adf output=precip_slope
r.in.gdal --o input=${INPUT_DIR}/mar_class_mw2/hdr.adf output=ocean_slope

# TODO get the actual data here.... 
r.in.gdal --o input=${INPUT_DIR}/precip_mw/hdr.adf output=lang_slope
r.in.gdal --o input=${INPUT_DIR}/precip_mw/hdr.adf output=elev_slope

# Calculate the temp_slope grid
r.mapcalc "temp_slope = (tmp_rng_slope + min_temp_slope) / 2"

