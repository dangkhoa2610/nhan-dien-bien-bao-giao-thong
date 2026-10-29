import yaml

class_names_vi = [
    'Cấm vào',                              # 0: No Entry
    'Chỉ được rẽ phải',                     # 1: Turn Right Only
    'Tốc độ tối đa cho phép 40km/h',        # 2: Speed limit 40hm/h
    'Cấm xe tải và xe khách',               # 3: No Trucks and Bus
    'Cấm xe tải',                           # 4: No Trucks
    'Chiều cao hạn chế',                    # 5: Low Clearance
    'Cấm xe ô tô',                          # 6: No Cars
    'Nguy hiểm khác',                       # 7: Danger
    'Đi chậm',                              # 8: Slown Down
    'Ngoặt nguy hiểm liên tiếp bên phải',   # 9: Double curve first to right
    'Chướng ngại vật',                     # 10: Obstacle on the Road
    'Đoạn đường có camera giám sát',        # 11: Road with Surveillance Camera
    'Tốc độ tối đa cho phép 60km/h',        # 12: Speed limit 60hm/h
    'Cấm xe mô tô',                         # 13: No Moto
    'Làn đường dành riêng theo phương tiện', # 14: Lane Allocation
    'Hạn chế chiều cao',                    # 15: Height Limit
    'Cấm bấm còi',                          # 16: No Horns
    'Cấm rẽ trái',                          # 17: No Left Turn
    'Cấm rẽ phải',                          # 18: No Right Turn
    'Cấm quay đầu xe',                      # 19: No U-Turn
    'Cấm quay đầu và rẽ trái',              # 20: No U-Turn and No Left Turn
    'Cấm quay đầu và rẽ phải',             # 21: No U-Turn and No Right Turn
    'Giao nhau có tín hiệu đèn',            # 22: Traffic light ahead
    'Cấm dừng xe và đỗ xe',                 # 23: No Stopping & No Parking
    'Cấm đỗ xe',                            # 24: No Parking
    'Cấm đi thẳng và rẽ phải',              # 25: No Straight and Right Turn
    'Cấm rẽ trái và rẽ phải',               # 26: No Left or Right Turn
    'Chỗ ngoặt nguy hiểm bên trái',         # 27: Sharp Left Turn
    'Chỗ ngoặt nguy hiểm bên phải',        # 28: Sharp Right Turn
    'Giao nhau với đường không ưu tiên',    # 29: Intersection with a Minor Road
    'Giao nhau cùng cấp',                  # 30: Intersection with Equal Roads
    'Cấm xe mô tô rẽ trái',                 # 31: No Moto Turn Left
    'Giao nhau với đường ưu tiên',          # 32: Intersection with a Priority Road
    'Đường dành cho người đi bộ',          # 33: Pedestrian Lane
    'Đường bị hẹp bên trái',               # 34: Narrow Road Left Side
    'Đường bị hẹp bên phải',              # 35: Narrow Road Right Side
    'Đường bị hẹp cả hai bên',             # 36: Narrow road both sides
    'Cấm xe 2 và 3 bánh',                  # 37: No Two or Three-wheeled Vehicles
    'Gờ giảm tốc',                          # 38: Speed Bump
    'Tốc độ tối đa cho phép 50km/h',        # 39: Speed limit 50hm/h
    'Tốc độ tối đa cho phép 70km/h',        # 40: Speed limit 70hm/h
    'Tốc độ tối đa cho phép 80km/h',        # 41: Speed limit 80hm/h
    'Giao nhau với đường sắt có rào chắn',  # 42: Level Crossing with Barriers
    'Cấm xe ô tô quay đầu',                 # 43: No U-Turn for Cars
    'Cấm xe xe khách',                      # 44: No bus
    'Cấm vượt',                             # 45: No Overtaking
    'Trẻ em ngang qua',                     # 46: Children Crossing
    'Đường người đi bộ sang đường',        # 47: Pedestrian Crossing
    'Hết tất cả các lệnh cấm',              # 48: End of all prohibition
    'Đi về bên trái',                      # 49: Keep left
    'Công trường',                          # 50: Road Work Ahead
    'Đường một chiều',                      # 51: One way street
    'Rẽ trái',                              # 52: Turn Left
    'Rẽ phải',                             # 53: Turn Right
    'Đèn xanh',                            # 54: Green Light
    'Đèn đỏ',                              # 55: Red Light
    'Nơi giao nhau chạy theo vòng xuyến',  # 56: Roundabout
    'Tốc độ tối đa cho phép 10km/h',        # 57: Speed limit 10km/h
    'Tốc độ tối đa cho phép 100km/h',       # 58: Speed limit 100km/h
    'Tốc độ tối đa cho phép 110km/h',       # 59: Speed limit 110km/h
    'Tốc độ tối đa cho phép 120km/h',       # 60: Speed limit 120km/h
    'Tốc độ tối đa cho phép 20km/h',        # 61: Speed limit 20km/h
    'Tốc độ tối đa cho phép 30km/h',        # 62: Speed limit 30km/h
    'Tốc độ tối đa cho phép 90km/h',        # 63: Speed limit 90km/h
    'Dừng lại',                             # 64: Stop
    'Khu vực quay đầu xe',                  # 65: U-Turn Area
    'Cấm đỗ xe ngày lẻ',                    # 66: No Parking on Odd Days
    'Cấm đỗ xe ngày chẵn',                  # 67: No Parking on Even Days
    'Nơi đỗ xe',                            # 68: Parking
    'Điểm dừng xe buýt',                    # 69: Bus Stop
    'Bệnh viện',                            # 70: Hospital
    'Cấm xe ô tô quay đầu và rẽ trái',     # 71: No U-Turn and Left Turn for Cars
    'Đoạn đường hay xảy ra tai nạn',       # 72: Accident area
    'Đường đôi',                            # 73: Dual carriageway
    'Cấm xe ô tô rẽ trái',                  # 74: No left turn for cars
    'Dốc lên nguy hiểm',                    # 75: Steep ascent
    'Cầu hẹp',                              # 76: Narrow bridge
    'Đường không bằng phẳng',               # 77: Uneven road
    'Hết hạn chế tốc độ tối đa 50km/h',     # 78: End of 50km/h speed limit
    'Khu đông dân cư',                      # 79: Residential area
    'Hết khu đông dân cư',                  # 80: sparsely populated area
    'Đường trơn trượt'                      # 81: Slippery Road
]

data = {
    'path': 'du_lieu/tho/dataset_cropped/dataset',
    'train': 'train/images',
    'val': 'test/images',
    'test': 'test/images',
    'nc': len(class_names_vi),
    'names': {i: name for i, name in enumerate(class_names_vi)}
}

yaml_path = "du_lieu/tho/dataset_cropped/dataset/data.yaml"
with open(yaml_path, 'w', encoding='utf-8') as f:
    yaml.dump(data, f, sort_keys=False, allow_unicode=True)

print(f"✅ Đã cập nhật file data.yaml với tên lớp Tiếng Việt tại: {yaml_path}")