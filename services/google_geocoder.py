import googlemaps

from entities.patient_request import PatientRequest


class Geocoder:
    def __init__(self, access_key):
        self._client = googlemaps.Client(key=access_key)

    def lat_long_assign(self, patient: PatientRequest):
        geocode_result = self._client.geocode(patient.address + 'Bogota')
        patient.lat = geocode_result[0]['geometry']['location']['lat']
        patient.lng = geocode_result[0]['geometry']['location']['lng']
