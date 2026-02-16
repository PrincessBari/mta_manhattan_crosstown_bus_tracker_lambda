import json
import os
import requests

TRACKED_ROUTES = ['M14A-SBS', 'M14D-SBS', 'M21', 'M23-SBS', 
                  'M34-SBS', 'M34A-SBS', 'M42', 'M50', 'M57', 'M66', 'M72', 
                  'M79-SBS', 'M86-SBS', 'M96', 'M106', 'M116', 'M125']

def handler(event, context):
    """Vercel serverless function handler"""
    
    api_key = os.environ.get('MTA_API_KEY')
    
    if not api_key:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'API key not configured'})
        }
    
    try:
        url = "https://bustime.mta.info/api/siri/vehicle-monitoring.json"
        params = {
            'key': api_key,
            'version': '2',
            'VehicleMonitoringDetailLevel': 'calls'
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        buses = []
        vehicle_activities = data['Siri']['ServiceDelivery']['VehicleMonitoringDelivery'][0].get('VehicleActivity', [])
        
        for activity in vehicle_activities:
            journey = activity.get('MonitoredVehicleJourney', {})
            location = journey.get('VehicleLocation', {})
            lat = location.get('Latitude')
            lon = location.get('Longitude')
            
            if not lat or not lon:
                continue
            
            vehicle_ref = journey.get('VehicleRef', 'Unknown')
            published_line_raw = journey.get('PublishedLineName', '')
            
            if isinstance(published_line_raw, list) and len(published_line_raw) > 0:
                published_line = published_line_raw[0]
            elif isinstance(published_line_raw, str):
                published_line = published_line_raw
            else:
                published_line = ''
            
            destination_name = journey.get('DestinationName', 'Unknown')
            
            if not published_line or not isinstance(published_line, str) or not published_line.startswith('M'):
                continue
            
            route_matches = False
            for tracked_route in TRACKED_ROUTES:
                normalized_published = published_line.replace(' ', '').replace('-', '').replace('+', '')
                normalized_tracked = tracked_route.replace(' ', '').replace('-', '').replace('+', '')
                if normalized_published == normalized_tracked or published_line == tracked_route:
                    route_matches = True
                    break
            
            if not route_matches:
                continue
            
            next_stops = []
            onward_calls = journey.get('OnwardCalls', {})
            if onward_calls:
                calls = onward_calls.get('OnwardCall', [])
                for call in calls[:3]:
                    stop_name = call.get('StopPointName', 'Unknown')
                    next_stops.append(stop_name)
            
            bus_info = {
                'vehicle_id': vehicle_ref.replace('MTA NYCT_', ''),
                'route': published_line,
                'latitude': lat,
                'longitude': lon,
                'destination': destination_name,
                'next_stops': next_stops
            }
            
            buses.append(bus_info)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'buses': buses,
                'count': len(buses)
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
```

And update `requirements.txt` to remove Flask:
```
requests==2.31.0
python-dotenv==1.0.0