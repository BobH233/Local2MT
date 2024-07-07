import json
import numpy as np

with open("./output/camera.json","r") as file:
    camera_data = json.load(file)

with open("./output/affine_matrix.json","r") as file:
    affine_data = json.load(file)

def GetIntersectPoint(pixel_position):
    global camera_data
    # 相机内参
    K = np.array(camera_data["intrinsics"])
    rotation = np.array(camera_data["rotation"])
    translation = np.array([camera_data["translation"][0][0], camera_data["translation"][1][0], camera_data["translation"][2][0]])
    d = np.linalg.inv(K) @ np.array([pixel_position[0], pixel_position[1], 1])
    global_d = rotation @ d
    t = -translation[2] / global_d[2]
    intersection_point = translation + t * global_d
    return intersection_point

# 首先获取图片上某一个像素点对应的3d位置
intersect_p = GetIntersectPoint([960, 540])
print("intersect_p:", intersect_p)

# 然后获取他在动捕下的位置
affine_matrix = np.array(affine_data["affine_matrix"])
camera_point_augmented = np.append(intersect_p, 1)
transformed_point = affine_matrix @ camera_point_augmented
print("transformed_point:", transformed_point)