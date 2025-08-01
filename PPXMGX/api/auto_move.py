import copy
import requests
import json
import logging
import traceback
import math
import urllib.parse


logging.basicConfig(filename='auto_dichotomy.log', filemode='a', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def main2(url, name):
    try:
        header = {"Cookie": f"_at={cookie_2}", 'web-token': "78826a12547b4da599faa439c4ee6f30"}
        url = (f'http://pms.pro.js.sgcc.com.cn:32100/yj-pms-coordinate-editing/shebei/detail?'
               f'psrId={url}&psrType=02&exValue=')
        logging.info(f"url2 : {url}")
        reps_data = requests.get(url, headers=header)
        
        first_data = reps_data.json()
        adjust_bracket_positions(first_data)
        # output(first_data, name)
    except Exception as e:
        logging.info(f"Error: {name} 出现错误")
        logging.info(f"Error: {str(e)}")
        logging.info(traceback.format_exc())


def main(name):
    try:
        head = {"Cookie": f"Admin-Token={cookie_1};sidebarStatus=0", "Authorization": cookie_1}
        encoded_name = urllib.parse.quote(name)
        url = (f'http://20.47.197.138:28004/prod-api/hc/sbDatachkAbnormalList/list?'
               f'pubPrivFlag=bxzl&orgNum=32101&pageSize=20&pageNum=1&cmsAffilPbName={encoded_name}')
        logging.info(f"url1: {url}")
        reps = requests.get(url, headers=head)
        reps_data = reps.json()
        logging.info(reps)
        if reps_data.get('code', '') == 200 and reps_data.get('msg', '') == '查询成功' and reps_data.get('rows', []):
            url_arg = reps_data.get('rows', [])[0].get("cmsAffilPbId", "")
            file_name = reps_data.get('rows', [])[0].get("cmsAffilPbName", "")
            if file_name and url_arg:
                main2(url_arg, file_name)
    except Exception as e:
        logging.info(f"Error: {name} 出现错误")
        logging.info(f"Error: {str(e)}")
        logging.info(traceback.format_exc())

def calculate_angle(line1, line2):
    # 计算两条线之间的夹角
    x1, y1 = line1[1][0] - line1[0][0], line1[1][1] - line1[0][1]
    x2, y2 = line2[1][0] - line2[0][0], line2[1][1] - line2[0][1]
    dot_product = x1 * x2 + y1 * y2
    magnitude1 = math.sqrt(x1**2 + y1**2)
    magnitude2 = math.sqrt(x2**2 + y2**2)
    if magnitude1 == 0 or magnitude2 == 0:
        return None
    cos_theta = dot_product / (magnitude1 * magnitude2)
    angle = math.degrees(math.acos(cos_theta))
    return angle

def adjust_bracket_positions(data):
    try:
        dict_data = json.loads(data.get("data", {}).get("geojson", {}))

        open('C:/ppxTemp/test_1.json', 'w', encoding="U8").write(json.dumps(dict_data, indent=4, ensure_ascii=False))
        features = dict_data.get("features", [])
        poles = []
        wall_brackets = []
        lines = []

        # 第一步：从 features 中提取杆塔、墙支架和连接线
        for feature in features:
            geometry = feature.get("geometry", {})
            properties = feature.get("properties", {})
            psr_type = properties.get("psrType", "")

            if psr_type == "dywlgt":  # 杆塔
                poles.append(feature)
            elif psr_type == "3114":  # 墙支架
                wall_brackets.append(feature)
            elif geometry.get("type") == "LineString":  # 连接线
                lines.append(feature)

        # 第二步：调整墙支架的位置，使其位于其连接的杆塔正下方
        for line in lines:
            line_coords = line["geometry"].get("coordinates", [])
            connected_pole = None
            connected_bracket = None

            # 找到与该连接线相连的杆塔和墙支架
            for pole in poles:
                pole_coords = pole["geometry"].get("coordinates", [])
                if pole_coords in line_coords:
                    connected_pole = pole
                    break

            for bracket in wall_brackets:
                bracket_coords = bracket["geometry"].get("coordinates", [])
                if bracket_coords in line_coords:
                    connected_bracket = bracket
                    break

            # 如果找到杆塔和墙支架，调整墙支架的位置
            if connected_pole and connected_bracket:
                pole_coords = connected_pole["geometry"].get("coordinates", [])
                bracket_coords = connected_bracket["geometry"].get("coordinates", [])

                # 将墙支架移动到杆塔的正下方
                bracket_coords[0] = pole_coords[0]
                bracket_coords[1] = pole_coords[1] - 0.0001  # 调整 y 坐标以使其位于杆塔下方
                connected_bracket["geometry"]["coordinates"] = bracket_coords
                logging.info(f"Adjusted wall bracket {connected_bracket['properties'].get('id')} below pole {connected_pole['properties'].get('id')}")

                # 更新连接线的坐标以反映新的墙支架位置
                for idx, coord in enumerate(line_coords):
                    if coord == bracket_coords:
                        line_coords[idx] = bracket_coords
                        logging.info(f"Updated line {line['properties'].get('id')} to reflect new bracket position")

        # 第三步：计算连接到有墙支架的杆塔的连接线之间的夹角
        for pole in poles:
            connected_lines = []
            pole_coords = pole["geometry"].get("coordinates", [])

            # 找到所有与该杆塔相连的连接线
            for line in lines:
                line_coords = line["geometry"].get("coordinates", [])
                if pole_coords in line_coords:
                    # 判断是否是杆塔与杆塔之间的连接线
                    other_coords = [coord for coord in line_coords if coord != pole_coords]
                    if any(other_coords == other_pole["geometry"].get("coordinates", []) for other_pole in poles):
                        connected_lines.append(line_coords)

            # 如果有两条连接线，计算它们之间的夹角
            if len(connected_lines) == 2:
                angle = calculate_angle(connected_lines[0], connected_lines[1])
                if angle is not None:
                    logging.info(f"Angle between lines connected to pole {pole['properties'].get('id')}: {angle} degrees")

                    # 根据夹角调整墙支架的位置
                    if angle < 30:
                        logging.info(f"Angle is less than 30 degrees, no movement for wall bracket connected to pole {pole['properties'].get('id')}")
                    elif 30 <= angle < 90:
                        # 移动墙支架到 45 度位置
                        logging.info(f"Angle is between 30 and 90 degrees, moving wall bracket to 45 degrees position for pole {pole['properties'].get('id')}")
                        for line_coords in connected_lines:
                            for bracket in wall_brackets:
                                bracket_coords = bracket["geometry"].get("coordinates", [])
                                if bracket_coords in line_coords:
                                    bracket_coords[0] = pole_coords[0] + 0.0001  # 调整 x 坐标到 45 度位置
                                    bracket_coords[1] = pole_coords[1] - 0.0001  # 调整 y 坐标到 45 度位置
                                    bracket["geometry"]["coordinates"] = bracket_coords
                                    logging.info(f"Moved wall bracket {bracket['properties'].get('id')} to 45 degrees position relative to pole {pole['properties'].get('id')}")
                    elif angle >= 90:
                        # 移动墙支架到 90 度位置
                        logging.info(f"Angle is greater than or equal to 90 degrees, moving wall bracket to 90 degrees position for pole {pole['properties'].get('id')}")
                        for line_coords in connected_lines:
                            for bracket in wall_brackets:
                                bracket_coords = bracket["geometry"].get("coordinates", [])
                                if bracket_coords in line_coords:
                                    bracket_coords[0] = pole_coords[0]  # 保持 x 坐标不变
                                    bracket_coords[1] = pole_coords[1] - 0.0002  # 调整 y 坐标到 90 度位置
                                    bracket["geometry"]["coordinates"] = bracket_coords
                                    logging.info(f"Moved wall bracket {bracket['properties'].get('id')} to 90 degrees position relative to pole {pole['properties'].get('id')}")

        return data

    except Exception as e:
        logging.error(f"发生错误: {str(e)}")
        logging.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    
    cookie_1 = ""
    cookie_2 = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIxMzk1NTA3MDgiLCJpYXQiOjE3MzIxNTE5NzMsInN1YiI6IndhbmdyOCIsImV4cCI6MTczMjIzODM3M30.wsxmJ5qGZR2p6HWR_yD_QiwkHHORKDSJO0qvMp-P2M4"
    psrId = "14000756240851"

    main2(psrId, '青湖167#尚庄北2公变')
