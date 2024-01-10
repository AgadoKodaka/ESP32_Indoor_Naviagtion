import os


def distance(x, y):
    return (x[0] - y[0])**2 + (x[1] - y[1])**2

def nearest_point_mapping(point_location, main_points):
    point_keys = []
    point_dis = []
    for point, point_data in main_points.items():
        location = point_data['location']
        dis = distance(location, point_location)
        
        point_keys.append(point)
        point_dis.append(dis)
    
    idx = point_dis.index(min(point_dis))
    return point_keys[idx]

def astar(start_point, end_point, map_data):
    current_point = start_point
    previous_point = current_point
    path = [map_data[current_point]['location']]
    
    end_point_location = map_data[end_point]['location']
    
    round = 0
    
    print(f"Start: {current_point} - Target: {end_point} - Location: {map_data[current_point]['location']}")
    while current_point != end_point:
        current_point_info = map_data[current_point]
        neighbors = current_point_info['neighbors']
        
        reachable_neighbors = [x for x in neighbors if map_data[x]['label'] == '1']
        if previous_point in reachable_neighbors:
            reachable_neighbors.remove(previous_point)
        
        if len(reachable_neighbors) == 1:
            next_point = reachable_neighbors[0]
        elif len(reachable_neighbors) > 1:
            reachable_neighbors_location = [map_data[x]['location'] for x in reachable_neighbors]
            dis_compare = [distance(x, end_point_location) for x in reachable_neighbors_location]
            
            min_idx = dis_compare.index(min(dis_compare))
            next_point = reachable_neighbors[min_idx]
        else:
            raise Exception("reachable list is empty")
            
        previous_point = current_point
        current_point = next_point
        path.append(map_data[next_point]['location'])
        
        print(f"Round: {round} - Current: {current_point} - Location: {next_point}")
        round += 1
    
    return path