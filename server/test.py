import os
import json
import matplotlib.pyplot as plt
import shutil
import copy

from map import white_list_xy, max_bound, min_bound, step
from astar import distance, nearest_point_mapping, astar

if __name__ == '__main__':
    
    map_path = os.getcwd() + "/map/map.json"
    f = open(map_path, 'r')
    map_data = json.load(f)
    f.close()
    
    main_points = {key : map_data[key] for key in map_data if (map_data[key]['location'][0] in white_list_xy) and (map_data[key]['location'][1] in white_list_xy)}
    
    test_dir = os.getcwd() + "/test"
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)
    else:
        shutil.rmtree(test_dir)
        os.mkdir(test_dir)
    
    main_point_path = test_dir + "/main_points.json"
    with open(main_point_path, 'w') as f:
        json.dump(main_points, f)
    
    start_point = [(130.5, 250.72), (560.23, 232.26)]
    end_point = [(480, 480), (120, 120)]
    
    for idx, (_start, _end) in enumerate(zip(start_point, end_point)):
        sub_test_dir = test_dir + f"/{idx}"
        if not os.path.exists(sub_test_dir):
            os.mkdir(sub_test_dir)
        
        config = {
            "start" : _start,
            "end" : _end
        }
        
        config_path = sub_test_dir + "/config.json"
        with open(config_path, 'w') as file:
            json.dump(config, file)
        
        norm_start_point = nearest_point_mapping(point_location=_start, main_points=main_points)
        
        norm_end_point = f"{_end[0]//60}-{_end[1]//60}"
        
        print(f"Starting point Normalization: {norm_start_point}")
        print(f"Ending point Normalization: {norm_end_point}")
        
        path = astar(start_point=norm_start_point, end_point=norm_end_point, map_data=map_data)
        
        print(path)
        
        plt.figure()
    
        for pt in map_data:
            lbl = map_data[pt]['label']
            lo = map_data[pt]['location']
            if lbl == '1':
                plt.plot([lo[0]], [lo[1]], marker='.', color='green')
            else:
                plt.plot([lo[0]], [lo[1]], marker='x', color='red')
        
        for idx in range(len(path) - 1):
            start = path[idx]
            end = path[idx + 1]
            
            x, y = start
            dx, dy = end[0] - x, end[1] - y
            
            plt.arrow(x=x, y=y, dx=dx, dy=dy, width = 1, head_width=10, color = 'blue')
            
        map_img_path = sub_test_dir + "/map.pdf"
        plt.xlim(max_bound, min_bound - step)
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.savefig(map_img_path, format='pdf', dpi=300)