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
