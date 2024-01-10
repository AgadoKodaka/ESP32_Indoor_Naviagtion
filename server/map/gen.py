import os
import json
import matplotlib.pyplot as plt

white_list_xy = [120, 240, 360, 480]
white_list_y = [180, 300, 420]
max_bound = 660
min_bound = 0
step = 60
max_point_idx = 10
min_point_idx = 0

unit_circle_direction = [
    (0, -1), # up
    (0, 1), # down
    (-1, 0), # left
    (1, 0) # right
]


if __name__ == "__main__":
    
    map_data = {}
    
    for x_idx, x_value in enumerate(range(min_bound, max_bound, step)):
        for y_idx, y_value in enumerate(range(min_bound, max_bound, 60)):
            if (x_value in white_list_xy and y_value in white_list_xy) or (x_value in white_list_xy and y_value in white_list_y):
                label = '1'
            elif x_value == 300 and y_value in [120, 360]:
                label = '1'
            elif x_value == 180 and y_value in [120, 480]:
                label = '1'
            elif x_value == 420 and y_value in [120, 480]:
                label = '1'
            else:
                label = '0'
            
            map_data[f"{x_idx}-{y_idx}"] = {
                "location" : (x_value, y_value),
                "label" : label,
                "neighbors" : []
            }
    
    for x_idx, x_value in enumerate(range(min_bound, max_bound, step)):
        for y_idx, y_value in enumerate(range(min_bound, max_bound, 60)):
            current_point_idx = f"{x_idx}-{y_idx}"
            if map_data[current_point_idx]['label'] == '0':
                continue
            for direction in unit_circle_direction:
                check_neighbor_idx = (x_idx + direction[0], y_idx + direction[1])
                check_neighbor_idx_key = f"{check_neighbor_idx[0]}-{check_neighbor_idx[1]}"
                if max(check_neighbor_idx) <= max_point_idx and min(check_neighbor_idx) >= min_point_idx:
                    map_data[current_point_idx]['neighbors'].append(check_neighbor_idx_key)
    
                
    map_path = os.path.dirname(os.path.abspath(__file__)) + "/map.json"
    
    with open(map_path, 'w') as f:
        json.dump(map_data, f)
    
    plt.figure()
    
    for pt in map_data:
        lbl = map_data[pt]['label']
        lo = map_data[pt]['location']
        if lbl == '1':
            plt.plot([lo[0]], [lo[1]], marker='.', color='green')
        else:
            plt.plot([lo[0]], [lo[1]], marker='x', color='red')
    
    map_img_path = os.path.dirname(os.path.abspath(__file__)) + "/map.pdf"
    # plt.xlim(max_bound, min_bound - step)
    plt.ylim(max_bound, min_bound - step)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.savefig(map_img_path, format='pdf', dpi=300)