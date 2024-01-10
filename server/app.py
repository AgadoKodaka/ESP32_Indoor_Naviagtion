import os
import json
import shutil
from datetime import datetime

from flask import Flask, send_file, request, jsonify, make_response, current_app
from flask_ngrok import run_with_ngrok
from flask_cors import CORS
from functools import update_wrapper, wraps
from pyngrok import ngrok
import requests

from map import white_list_xy, max_bound, min_bound, step
from astar import distance, nearest_point_mapping, astar
    

if __name__ == '__main__':
    
    map_path = os.getcwd() + "/map/map.json"
    f = open(map_path)
    map_data = json.load(f)
    
    main_points = {key : map_data[key] for key in map_data if (map_data[key]['location'][0] in white_list_xy) and (map_data[key]['location'][1] in white_list_xy)}
    
    infer_dir = os.getcwd() + "/infer"
    if not os.path.exists(infer_dir):
        os.mkdir(infer_dir)
    else:
        shutil.rmtree(infer_dir)
        os.mkdir(infer_dir)

    app = Flask(__name__)
    port_no = 5000
    ngrok.set_auth_token("2AnC9szbri9GPw0kmnmKWKs5II4_6Jt8tgMqEZ7tPHbeCGVKq")
    public_url = ngrok.connect(port_no).public_url
    CORS(app)
    # run_with_ngrok(app)
    print(f"To access the Global link please click {public_url}")

    @app.route("/")
    def home():
        return "<h1>Hospital Navigation Backend Server</h1>"

    @app.route('/get_path', methods= ['GET', 'POST'])
    def get_path():
        if request.method == 'POST':
            json_data = request.json
            
            start = tuple(json_data['start']) # (x, y)
            end = tuple(json_data['end']) # (x', y')
            
            now = datetime.now().strftime("%m-%d-%Y - %H-%M-%S")
            sub_infer_dir = infer_dir + f"/{now}"
            if not os.path.exists(sub_infer_dir):
                os.mkdir(sub_infer_dir)
            
            config = {
                "start" : start,
                "end" : end
            }
            
            config_path = sub_infer_dir + "/config.json"
            with open(config_path, 'w') as file:
                json.dump(config, file)
            
            log_path = sub_infer_dir + "/log.txt"
            
            norm_start_point = nearest_point_mapping(point_location=start, main_points=main_points)
        
            norm_end_point = f"{int(end[0]//60)}-{int(end[1]//60)}"
            
            logs = [
                f"Starting point Normalization: {norm_start_point}\n",
                f"Ending point Normalization: {norm_end_point}\n"
            ]
            
            with open(log_path, 'w') as file:
                file.writelines(logs)
            
            path = astar(start_point=norm_start_point, end_point=norm_end_point, map_data=map_data)
            
            logs.append(f"Path: {path}\n")
            
            with open(log_path, 'w') as file:
                file.writelines(logs)
            
            return jsonify(path=path)
            
    app.run(port=port_no)