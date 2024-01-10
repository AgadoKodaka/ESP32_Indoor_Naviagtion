import requests
import json

# Đường dẫn tới file JSON cần truyền
json_file_path = 'Coor_Destination.json'

# URL của API ngrok
ngrok_api_url = 'https://e51b-14-231-14-232.ngrok-free.app/get_path'

# Đọc nội dung từ file JSON
with open(json_file_path, 'r') as file:
    json_data = json.load(file)

# Gửi yêu cầu POST với dữ liệu JSON
response = requests.post(ngrok_api_url, json=json_data)

# Kiểm tra phản hồi từ server
if response.status_code == 200:
    print('Yêu cầu thành công!')
    print('Dữ liệu phản hồi:', response.json())

    # Lấy danh sách điểm trung gian từ phản hồi
    path_points = response.json().get('path', [])

    # Lưu danh sách điểm trung gian vào tệp JSON
    with open('path_point_to_point.json', 'w') as path_json_file:
        json.dump(path_points, path_json_file)

else:
    print('Yêu cầu thất bại. Mã trạng thái:', response.status_code)
    print('Nội dung phản hồi:', response.text)
