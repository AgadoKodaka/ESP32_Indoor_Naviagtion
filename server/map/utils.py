import os
import matplotlib.pyplot as plt

def draw_map(map_data, max_bound, min_bound, step, map_img_path):
    plt.figure()
    for pt in map_data:
            lbl = map_data[pt]['label']
            lo = map_data[pt]['location']
            if lbl == '1':
                plt.plot([lo[0]], [lo[1]], marker='.', color='green')
            else:
                plt.plot([lo[0]], [lo[1]], marker='x', color='red')
        
    
    plt.xlim(max_bound, min_bound - step)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.savefig(map_img_path, format='pdf', dpi=300)