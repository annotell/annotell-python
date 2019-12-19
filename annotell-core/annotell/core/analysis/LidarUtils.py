import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.transform import Rotation
# from database.DB import DB


def plot_lidar_annotations(boxes_anno, color='b', include_arrow=False, include_text=False, alpha=0.2):
    order = [0, 4, 7, 3, 0]
    for ix, box in enumerate(boxes_anno):
        coords = box.box_coordinates
        plt.plot(coords[1, order], -coords[0, order], color, alpha=alpha)
        # plt.plot(box.position[1], -box.position[0], color+'.')
        if include_text:
            plt.text(box.position[1], -box.position[0], box.object_id, color=color)
        if include_arrow:
            x0 = box.position[0]
            y0 = box.position[1]
            yaw = box.rotation[2]
            radius = box.scale[1] / 2
            dx = radius * np.cos(yaw + np.pi / 2)
            dy = radius * np.sin(yaw + np.pi / 2)

            plt.arrow(y0, -x0, dy, -dx, fc=color, ec=color, head_width=radius / 10, head_length=radius / 5, alpha=alpha)


def plot_lidar_in_yz_plane(boxes_anno, color='b'):
    order = [0, 1, 5, 4, 0]
    for ix, box in enumerate(boxes_anno):
        coords = box.box_coordinates
        plt.plot(coords[1, order], coords[2, order], color, alpha=0.5)


def calculate_iou(box_1, box_2, num_samples=10000, return_std=False):
    diagonal_1 = np.linalg.norm(box_1.scale)
    diagonal_2 = np.linalg.norm(box_2.scale)

    relative_position = (box_1.position - box_2.position).reshape((3, -1))

    if np.linalg.norm(relative_position) >= (diagonal_1 + diagonal_2) / 2:
        return 0  # if it is possible for the boxes to intersect

    # get_rotation_matrices
    rotobj = Rotation.from_euler('xyz', box_1.rotation)
    R1 = rotobj.as_dcm()

    rotobj = Rotation.from_euler('xyz', box_2.rotation)
    R2 = rotobj.as_dcm()
    R2_inv = np.linalg.inv(R2)

    # sample points randomly in box 1
    points_in_box_1 = np.random.uniform(-0.5, 0.5, size=(3, num_samples)) * box_1.scale.reshape(3, -1)

    # transformation from box_1 reference system to box_2 reference system
    point_in_box_2 = R2_inv @ (R1 @ points_in_box_1 + relative_position)

    box_2_boundaries = box_2.scale.reshape((3, -1)) / 2

    # caclulate boxes both in box_1 and box_2
    A1 = point_in_box_2 <= box_2_boundaries
    A2 = point_in_box_2 >= -box_2_boundaries
    A = np.logical_and(A1, A2)
    is_inside = np.prod(A, axis=0)
    fraction_overlay = np.sum(is_inside) / is_inside.size  # fractions of box 1 in box 2

    volume_box_1 = np.prod(box_1.scale)
    intersection_volume = fraction_overlay * volume_box_1
    volume_box_2 = np.prod(box_2.scale)
    union_volume = volume_box_1 + volume_box_2 - intersection_volume

    iou = intersection_volume / union_volume

    if return_std:
        # MC integration uncertainty prediction
        std_est = np.sqrt(np.var(is_inside) / is_inside.size)
        return iou, std_est
    return iou


def diff_lidar_annotations(anno, corr):
    box_match = list()
    for i_anno_box, anno_box in enumerate(anno.data_content):
        iou_max = 0
        matching_corr_obj = -1
        direction_projection = 0
        for i_corr_box, corr_box in enumerate(corr.data_content):
            iou = calculate_iou(anno_box, corr_box)
            if iou > iou_max:
                iou_max = iou
                matching_corr_obj = i_corr_box

                y = np.array([0, 1, 0]).reshape((3, 1))
                direction_anno_box = anno_box.rotation_matrix @ y
                direction_corr_box = corr_box.rotation_matrix @ y
                direction_projection = direction_anno_box.transpose() @ direction_corr_box
                direction_projection = direction_projection[0, 0]

        box_match.append([matching_corr_obj, iou_max, direction_projection])
    box_match = np.array(box_match)

    # solve issue with anno relates to two corr boxes
    max_iou_dict = dict()
    for a_id in range(box_match.shape[0]):
        c_id = box_match[a_id, 0]
        if c_id != -1:
            if c_id in max_iou_dict:
                curr_iou = box_match[a_id, 1]
                prev_a_id, prev_iou = max_iou_dict[c_id]
                if curr_iou > prev_iou:
                    box_match[prev_a_id, :] = [-1, 0, 0]
                else:
                    box_match[a_id, :] = [-1, 0, 0]
            else:
                max_iou_dict[c_id] = a_id, box_match[a_id, 1]

    return box_match


class TransformationUtils:
    def __init__(self, task_def_id, camera_id):
        annotelldb = DB()
        raw_data_content = annotelldb.query(f"""
        select data.content from task_definitions
        JOIN data_lists ON data_lists.id = task_definitions.published_data_lists_id
        JOIN data_list_members ON data_list_members.data_lists_id = data_lists.id
        JOIN data ON data_list_members.data_id = data.id
        where task_definitions.id = {task_def_id};
        """)

        self.camera_calibration = raw_data_content[0][0]['cameraCalibration'][camera_id]
        self.lidar_calibration = raw_data_content[0][0]['cameraCalibration']['lidar']

        rotation_obj_lidar = Rotation.from_quat(np.array(self.lidar_calibration['rotation_quaternion'])[[1, 2, 3, 0]])
        self.rotation_matrix_lidar = rotation_obj_lidar.as_dcm()
        self.lidar_position = np.array(self.lidar_calibration['position']).reshape([3, 1])

        rotation_obj_camera = Rotation.from_quat(np.array(self.camera_calibration['rotation_quaternion'])[[1, 2, 3, 0]])
        self.rotation_matrix_camera = rotation_obj_camera.as_dcm()
        self.inv_rotation_matrix_camera = np.linalg.inv(self.rotation_matrix_camera)
        self.camera_position = np.array(self.camera_calibration['position']).reshape([3, 1])
        self.distortion_coefficients = np.array(self.camera_calibration['distortion_coefficients'])
        self.camera_matrix = self.camera_calibration['camera_matrix']

    def convert_lidar_to_ref_coord_sys(self, lidar_points):
        """
        :param lidar_points: Nx3 dimensional matrix of points in lidar ref system
        :return: Nx3 dimensional matrix of the same points in global reference system
        """
        points_in_ref_coord = self.rotation_matrix_lidar @ lidar_points.T + self.lidar_position
        return points_in_ref_coord.T

    def convert_ref_to_camera_coord_sys(self, ref_points):
        """

        :param ref_points: Nx3 matrix of points in global reference system
        :return: nx3 matrix of points in camera reference system
        """
        points_in_camera_coord_sys = self.inv_rotation_matrix_camera @ (ref_points.T - self.camera_position)
        return points_in_camera_coord_sys.T

    def distort_points_old(self, px, py):
        """

        :param px: normalized x coordinates
        :param py: normalized y coordinates
        :return: distortion adjusted coefficients
        """
        px2 = np.power(px, 2)
        py2 = np.power(py, 2)
        r2 = px2 + py2
        k = self.distortion_coefficients[[0, 1, 4]]
        p = self.distortion_coefficients[[2, 3]]
        kr = 1 + k[0] * r2 + k[1] * np.power(r2, 2) + k[2] * np.power(r2, 3)
        xy = px * py
        tx = 2 * p[0] * xy + p[1] * (r2 + 2 * px2)
        ty = 2 * p[1] * xy + p[0] * (r2 + 2 * py2)
        return px * kr + tx, py * kr + ty

    def distort_points(self, xp, yp):
        xp2 = np.power(xp, 2)
        yp2 = np.power(yp, 2)
        r2 = xp2 + yp2
        r4 = np.power(r2, 2)
        r6 = np.power(r2, 3)

        k = self.distortion_coefficients[[0, 1, 4]]
        p = self.distortion_coefficients[[2, 3]]

        kr = 1 + k[0] * r2 + k[1] * r4 + k[2] * r6

        xpp = xp * kr + 2 * p[0] * xp * yp + p[1] * (r2 + 2 * xp2)

        ypp = yp * kr + p[0] * (r2 + 2 * yp2) + 2 * p[1] * xp * yp

        return xpp, ypp

    def convert_camera_to_pixel_coord_sys(self, cam_points):
        """
        In order for this function to make any sense all z coordinate e.g. cam_points[2] > 0
        :param cam_points: Nx3 matrix of points in camera coordiante system
        :return: Nx2 matrix of pixel coordinates
        """
        px = cam_points[:, 0] / cam_points[:, 2]
        py = cam_points[:, 1] / cam_points[:, 2]

        xpp, ypp = self.distort_points(px, py)

        x = self.camera_matrix[0] * xpp + self.camera_matrix[6]
        y = self.camera_matrix[4] * ypp + self.camera_matrix[7]

        return np.array([x, y]).T
