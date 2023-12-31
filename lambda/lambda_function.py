import requests
import json
import boto3
import os
from datetime import datetime

def handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    api_endpoint = os.environ['API_ENDPOINT']

    location_data = {
        'London': {
            'latitude': 51.5098,
            'longitude': -0.1180
        },
        'Paris': {
            'latitude': 48.8588897,
            'longitude': 2.3200410217200766
        },
        'Brussels': {
            'latitude': 50.8465573,
            'longitude': 4.351697
        },
        'Madrid': {
            'latitude': 40.4167047,
            'longitude': -3.7035825
        },
        'Budapest': {
            'latitude': 47.48138955,
            'longitude': 19.14609412691246
        },
        'Oslo': {
            'latitude': 59.97239745,
            'longitude': 10.775729194051895
        }
    }

    current_timestamp = int(datetime.now().timestamp())

    response_data = []
    for location, coordinates in location_data.items():
        lat = coordinates['latitude']
        lon = coordinates['longitude']
        endpoint = api_endpoint.format(lat=lat, lon=lon).replace('end=dynamic', f'end={current_timestamp}')

        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
            for item in data["list"]:
                item["location"] = location
            response_data.append(data)
        else:
            return {
                'statusCode': 500,
                'body': 'Failed to fetch data from API'
            }

    merged_data = {
        'coord': response_data[0]['coord'],
        'list': [item for data in response_data for item in data['list']],
        'locations': location_data
    }

    json_data = json.dumps(merged_data)

    current_datetime = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    s3_key = f'weather_data_{current_datetime}.json'

    s3 = boto3.resource('s3')
    s3.Object(bucket_name, s3_key).put(Body=json_data)

    return {
        'statusCode': 200,
        'body': 'Data stored in S3 bucket'
    }
