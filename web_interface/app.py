from flask import Flask, render_template, Response, request, redirect, url_for, session
import json
import cv2
from path_to_destination import draw_line_on_image
import requests
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Thay 'your_secret_key' bằng một giá trị ngẫu nhiên và bảo mật
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Đường dẫn đến tệp hình ảnh cụ thể
input_image_path = 'static/RoomMap.drawio.png'

# Ban đầu, submitted là False
submitted = False

@app.route('/')
def index():
    print("render")
    return render_template('index.html', submitted=submitted)

def generate_frames():
    img = cv2.imread(input_image_path)
    print("Image Read Successful")

    if submitted:
        # If submitted, send data to API and get results
        print("User SUbmitted")
        with open('Coor_Destination.json', 'r') as coor_file:
            coor_data = json.load(coor_file)
            print("Load Successful")
            print(coor_data)
        
        response = requests.post('https://e51b-14-231-14-232.ngrok-free.app/get_path', json=coor_data)
        
        if response.status_code == 200:
            path_data = response.json()
            intermediate_points = path_data.get('path',[])
            print("Inter_point",intermediate_points)
            print("Get Successful")
            if not intermediate_points:
                print("empty")
            else:
                print("Non-empty list:", intermediate_points)

            # Nếu exists interrmediate points, draw line on image
            if intermediate_points:
                img_with_line = draw_line_on_image(img, '/home/bachdaohuu/Microprocessing_FE/path_point_to_point.json', '/home/bachdaohuu/Microprocessing_FE/Coor_Destination.json')
                print("ve thanh cong ")
            else:
                img_with_line = img
        else:
            print(f"API request failed with status code {response.status_code}")
            img_with_line = img
    else:
        img_with_line = img

    # Convert image to binary
    ret, buffer = cv2.imencode('.jpg', img_with_line)
    frame = buffer.tobytes()

    return frame

@app.route('/img_feed')
def img_feed():
    frame = session.get('frame', None)
    if frame is None:
        # Nếu frame không tồn tại trong session, gọi hàm để tạo mới
        print("Frame is none")
        frame = generate_frames()
        session['frame'] = frame

    return Response(frame, mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/submit_destination', methods=['POST'])
def submit_destination():
    global submitted

    with open('start_point.json', 'r') as start_point_file:
        start_point_data = json.load(start_point_file)

    # Thêm logic để ánh xạ phòng đã chọn thành tọa độ
    room_coordinates = {
        '401': [480, 360],
        '402': [480, 240],
        '403': [360, 480],
        '404': [360, 240],
        '405': [240, 360],
        '406': [240, 240]
        # Thêm các phòng khác vào đây
    }

    selected_room = request.form['room']
    end_coordinates = room_coordinates.get(selected_room, [0, 0])  # Mặc định là [0, 0] nếu không tìm thấy

    # Lưu tọa độ đích và tọa độ xuất phát vào file JSON
    coor_data = {
        "start": start_point_data,  # Sửa thành tọa độ mới
        "end": end_coordinates
        # "room": selected_room
    }

    with open('Coor_Destination.json', 'w') as coor_file:
        json.dump(coor_data, coor_file)

    # Gọi API và lấy kết quả
    api_response = requests.post('https://e51b-14-231-14-232.ngrok-free.app/get_path', json=coor_data).json()

    # Lưu kết quả vào path_point_to_point.json
    with open('path_point_to_point.json', 'w') as path_file:
        json.dump(api_response.get('path', []), path_file)

    # Đánh dấu là đã submit
    submitted = True
    print("User submitted")

    # Gọi hàm để cập nhật frame và lưu vào session
    frame = generate_frames()
    session['frame'] = frame

    # Trả về trang chính
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
