import csv
import json

TRACKED_ROUTES = ['M14A-SBS', 'M14D-SBS', 'M21', 'M23-SBS', 
                  'M34-SBS', 'M34A-SBS', 'M42', 'M50', 'M57', 'M66', 'M72', 
                  'M79-SBS', 'M86-SBS', 'M96', 'M106', 'M116', 'M125']

def load_route_shapes():
    """Load and parse GTFS shapes for crosstown routes, merging by route."""
    shapes_by_route = {}
    routes_merged = {}
    
    try:
        with open('shapes.txt', 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                shape_id = row['shape_id']
                route_identifier = shape_id[:-4]
                
                route_name = None
                
                if route_identifier.startswith('SBS'):
                    route_num = route_identifier[3:]
                    route_name = f'M{route_num}-SBS'
                elif route_identifier.startswith('SB'):
                    route_num = route_identifier[2:]
                    route_name = f'M{route_num}-SBS'
                elif route_identifier.startswith('M'):
                    route_num = route_identifier[1:].lstrip('0')
                    if route_num:
                        route_name = f'M{route_num}'
                else:
                    continue
                
                if not route_name:
                    continue
                
                is_tracked = False
                matched_route = None
                
                for tracked_route in TRACKED_ROUTES:
                    if route_name == tracked_route:
                        matched_route = tracked_route
                        is_tracked = True
                        break
                    if route_name == 'M34' and tracked_route == 'M34-SBS':
                        matched_route = 'M34-SBS'
                        is_tracked = True
                        break
                    if route_name == 'M34A' and tracked_route == 'M34A-SBS':
                        matched_route = 'M34A-SBS'
                        is_tracked = True
                        break
                
                if not is_tracked:
                    continue
                
                if shape_id not in shapes_by_route:
                    shapes_by_route[shape_id] = {
                        'route': matched_route,
                        'coordinates': []
                    }
                
                lat = float(row['shape_pt_lat'])
                lon = float(row['shape_pt_lon'])
                
                shapes_by_route[shape_id]['coordinates'].append([lon, lat])
        
        for shape_id, shape_data in shapes_by_route.items():
            route = shape_data['route']
            
            if route not in routes_merged:
                routes_merged[route] = []
            
            routes_merged[route].append(shape_data['coordinates'])
        
        output_shapes = {}
        for route, all_coords in routes_merged.items():
            output_shapes[route] = {
                'route': route,
                'coordinates': all_coords
            }
        
        print(f"✓ Loaded {len(output_shapes)} routes (merged from {len(shapes_by_route)} shape variants)")
        return output_shapes
        
    except FileNotFoundError:
        print("✗ shapes.txt not found")
        return {}

if __name__ == "__main__":
    shapes = load_route_shapes()
    with open('public/route_shapes.json', 'w') as f:
        json.dump(shapes, f, indent=2)
    print("✓ Generated public/route_shapes.json")