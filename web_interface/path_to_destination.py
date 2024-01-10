import cv2
import json


def draw_line_on_image(img, path_file ='/home/bachdaohuu/Microprocessing_FE/path_point_to_point.json' , coord_file='/home/bachdaohuu/Microprocessing_FE/Coor_Destination.json'):
    # Đọc danh sách điểm trung gian từ file JSON
    with open(path_file, 'r') as file:
        path_data = json.load(file)
    

    # Kiểm tra xem path_data có phải là kiểu list không
    if isinstance(path_data, list):
        intermediate_points = path_data
    else:
        intermediate_points = []

    # Đọc start_point và end_point từ file Coor_Destination.json
    with open(coord_file, 'r') as coord_file:
        coord_data = json.load(coord_file)

    start_point = coord_data['start']
    end_point = coord_data['end']


    # Kiểm tra xem danh sách intermediate_points có tồn tại không
    if intermediate_points is not None and len(intermediate_points) > 0:
        # Chuyển đổi tọa độ của các điểm theo hệ tọa độ mới
        start_point = (img.shape[1] - start_point[0], img.shape[0] - start_point[1])
        intermediate_points = [(img.shape[1] - point[0], img.shape[0] - point[1]) for point in intermediate_points]
        end_point = (img.shape[1] - end_point[0], img.shape[0] - end_point[1])

        # Vẽ đường từ điểm xuất phát đến điểm đầu tiên trong danh sách
        cv2.line(img, start_point, intermediate_points[0], (0, 0, 255), 2)

        # Vẽ các đoạn thẳng giữa các điểm trung gian
        for i in range(len(intermediate_points) - 1):
            cv2.line(img, intermediate_points[i], intermediate_points[i + 1], (0, 0, 255), 2)

        # Vẽ đường từ điểm cuối cùng trong danh sách đến điểm đích
        cv2.line(img, intermediate_points[-1], end_point, (0, 0, 255), 2)
    else:
        # Nếu danh sách trung gian rỗng, chỉ vẽ đường từ điểm xuất phát đến điểm đích
        cv2.line(img, start_point, end_point, (0, 0, 255), 2)

    return img

def show_image_with_line(img_path='/home/bachdaohuu/VXL_FE/static/Floor_raw_60.png', window_name='Output Image'):
    # Đọc ảnh đầu vào
    input_image = cv2.imread(img_path)

    # Gọi hàm để vẽ đường trên ảnh
    output_image = draw_line_on_image(input_image)

    # Hiển thị ảnh đã vẽ
    cv2.imshow(window_name, output_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# show_image_with_line()


if __name__ == "__main__":
    # Đọc ảnh đầu vào
    input_image = cv2.imread('/home/bachdaohuu/Microprocessing_FE/static/Floor.drawio.png')

    # Gọi hàm để vẽ đường trên ảnh
    output_image = draw_line_on_image(input_image)

    # Hiển thị ảnh đã vẽ
    cv2.imshow('Output Image', output_image)
    cv2.waitKey(0)  
    cv2.destroyAllWindows()
