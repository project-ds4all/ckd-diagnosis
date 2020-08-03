# ckd-diagnosis #

## services ##
Includes the main services used in the backend, like the S3 downloader, the model loader, the dataset loader

#### S3 Service ####
Service that loads that downloads the data from S3

#### blocks_data_storage ####
Service that stores the geojson that contains Bogota's blocks. This service uses the previously mentioned data to get the strata of the patient's block.

#### parks_data_storage ####
Service that stores the geojson that contains Bogota's parks. This service uses the previously mentioned data to get the closest park to the patient's location.

#### ckd_data_storage ####
Service that stores the csv with the patients' information included in the RIPS. This service uses the previously mentioned data to build pivot tables for the dashboard located in the frontend.

#### model_loader ####
Service that loads the model and checks if it matches the expected type. 

#### ckd_predictor ####
Service that uses the loaded model to predict propensity to CKD.

#### google_geocoder ####
Service that uses the Google Geoding API to get the latitude and longitude from the patient's address.

#### json_formatter ####
Service that formats the answer into a json file to return it to the frontend.

#### ckd_analyzer ####
Service that returns a diet based on the user's propensity to CKD.

## app.py ##
The app.py file contains the main code where all the previously mentioned services are consumed for both endpoint: the one in charge of sending pivot tables to the dashboard and the one that delivers the prediction to the diagnosis tab.

## EDA and Data Wrangling ##
This folder includes a jupyter notebook with the EDA and the plotly graphs that inspired the ones included in the dashboard. Also there is a python file where the data wrangling was done, using the csv of the census and the geojsons of the other geospatial data. This python file also includes the clustering that lead to the different layers of the map.

## Model training ##
In the folder model_notebook can be found a jupyter notebook that shows the development of the neural network employed by the backend to predict the propensity to develop CKD.


