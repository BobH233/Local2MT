
import numpy as np
import json

def calculate_affine_matrix(source_points, target_points):
    ones = np.ones((source_points.shape[0], 1))
    source_points_augmented = np.hstack([source_points, ones])

    # 增加一个额外的0行以适配仿射变换的需要
    target_points_augmented = np.hstack([target_points, np.ones((target_points.shape[0], 1))])

    affine_matrix, residuals, rank, s = np.linalg.lstsq(source_points_augmented, target_points_augmented, rcond=None)
    return affine_matrix.T  # 转置以匹配期望的形状

pattern_size = (8, 5)  # 例如，8x5的棋盘格
pattern_length = 0.015 # 棋盘格子长度，单位m


# 摄像机坐标系下的点
pat_width = pattern_size[0] - 1
pat_height = pattern_size[1] - 1
camera_points = np.array([
    [pat_width * pattern_length, pat_height * pattern_length, 0],
    [0, pat_height * pattern_length, 0],
    [pat_width * pattern_length, 0, 0],
    [0, 0, 0]
])

# 动捕坐标系下的点
motion_tracking_points = np.array([
    [1.438722, 1.097681, 0.014119],
    [1.342729, 1.194850, 0.016144],
    [1.382868, 1.045779, 0.014958],
    [1.285947, 1.141837, 0.015950]
])

# 计算仿射变换矩阵
affine_matrix = calculate_affine_matrix(camera_points, motion_tracking_points)


json_data = {
    "affine_matrix": affine_matrix.tolist()
}

with open("./output/affine_matrix.json", "w") as file:
    json.dump(json_data, file)

print("affine_matrix:", affine_matrix)
