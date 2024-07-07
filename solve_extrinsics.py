import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json

# 相机内参矩阵
camera_matrix = np.array([
    [1010.3189694810105, 0.0, 1015.0927389339929],
    [0.0, 1010.2102194659125, 534.4561232862634],
    [0.0, 0.0, 1.0]
])

# 相机畸变系数
dist_coeffs = np.array([
    -0.06046845156654011,
    -0.00327963133444338,
    -0.00510223471826531,
    0.00113234650865978
])

camera_image_path = "./img/camera12.jpg"

g_cam_mat = [camera_matrix]
g_cam_dist = [dist_coeffs]

# 棋盘格大小
pattern_size = (8, 5)  # 例如，8x5的棋盘格
square_size = 0.015  # 每个方格的边长，单位为米

def DrawCameraRT(picture, cam_id, ax):
    global g_cam_mat, g_cam_dist
    camera_matrix = g_cam_mat[cam_id - 1]
    dist_coeffs = g_cam_dist[cam_id - 1]
    image = cv2.imread(picture, cv2.IMREAD_GRAYSCALE)
    ret, corners = cv2.findChessboardCorners(image, pattern_size)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    if ret:
        # 提高角点精度
        corners2 = cv2.cornerSubPix(image, corners, (11, 11), (-1, -1), criteria)

        # 定义世界坐标系中的棋盘格点
        objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
        objp *= square_size

        # 计算相机相对于棋盘格的位姿
        ret, rvecs, tvecs = cv2.solvePnP(objp, corners2, camera_matrix, dist_coeffs)

        # 将旋转向量转换为旋转矩阵
        R, _ = cv2.Rodrigues(rvecs)
        R = R.T
        tvecs = -R @ tvecs

        print("Rotation matrix:")
        print(R)
        print("Translation vector:")
        print(tvecs)

        json_data = {
            "rotation": R.tolist(),
            "translation": tvecs.tolist(),
            "intrinsics": camera_matrix.tolist()
        }
        with open("./output/camera.json", "w") as file:
            json.dump(json_data, file)

        # 绘制棋盘格在世界坐标系中的点
        if cam_id == 1:
            ax.scatter(objp[:, 0], objp[:, 1], objp[:, 2], c='r', marker='o')

        # 绘制相机坐标系的原点
        camera_origin = tvecs.flatten()
        ax.scatter(camera_origin[0], camera_origin[1], camera_origin[2], c='b', marker='^')
        ax.text(camera_origin[0], camera_origin[1], camera_origin[2], f'{cam_id}', color='red')

        # 绘制相机坐标系的坐标轴
        axis_length = 0.1  # 坐标轴长度
        x_axis = camera_origin + R[:, 0] * axis_length
        y_axis = camera_origin + R[:, 1] * axis_length
        z_axis = camera_origin + R[:, 2] * axis_length

        # 绘制相机坐标系的x轴
        ax.plot([camera_origin[0], x_axis[0]],
                [camera_origin[1], x_axis[1]],
                [camera_origin[2], x_axis[2]], 'r-')

        # 绘制相机坐标系的y轴
        ax.plot([camera_origin[0], y_axis[0]],
                [camera_origin[1], y_axis[1]],
                [camera_origin[2], y_axis[2]], 'g-')

        # 绘制相机坐标系的z轴
        ax.plot([camera_origin[0], z_axis[0]],
                [camera_origin[1], z_axis[1]],
                [camera_origin[2], z_axis[2]], 'b-')
    else:
        print(f"cam{cam_id}: 棋盘格角点检测失败。")

# 在matplotlib中绘制结果
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

DrawCameraRT(camera_image_path, 1, ax)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.legend()

# 设置坐标轴范围
max_range = np.array([
    ax.get_xlim(), ax.get_ylim(), ax.get_zlim()
]).ptp().max() / 2

mid_x = (ax.get_xlim()[0] + ax.get_xlim()[1]) / 2
mid_y = (ax.get_ylim()[0] + ax.get_ylim()[1]) / 2
mid_z = (ax.get_zlim()[0] + ax.get_zlim()[1]) / 2

ax.set_xlim(mid_x - max_range, mid_x + max_range)
ax.set_ylim(mid_y - max_range, mid_y + max_range)
ax.set_zlim(mid_z - max_range, mid_z + max_range)

plt.show()
