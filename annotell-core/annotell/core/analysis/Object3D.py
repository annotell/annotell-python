import os
import copy
import numpy as np
from scipy.spatial.transform import Rotation
from annotell.core.analysis.Annotation import Annotation
from annotell.core.analysis.LidarUtils import calculate_iou


class Constants:
    SCALE = 'scale'
    POSITION = 'position'
    ROTATION = 'rotation'
    XYZ = 'XYZ'
    ID = 'id'


class BoundingBox3D:
    def __init__(self, object_id, scale, position, rotation):
        self.object_id = object_id
        self.scale = scale
        self.position = position
        self.rotation = rotation

        self.__reference_coordinates = None
        self.__rotation_matrix = None
        self.__inverse_rotation_matrix = None

    @property
    def rotation_matrix(self):
        if self.__rotation_matrix is None:
            rotation_obj = Rotation.from_euler('xyz', self.rotation)
            self.__rotation_matrix = rotation_obj.as_dcm()
        return self.__rotation_matrix

    @property
    def inverse_rotation_matrix(self):
        if self.__inverse_rotation_matrix is None:
            self.__inverse_rotation_matrix = np.linalg.inv(self.rotation_matrix)
        return self.__inverse_rotation_matrix

    @property
    def box_coordinates(self):
        if self.__reference_coordinates is None:
            self.__reference_coordinates = self.calculate_reference_coordinates()
        return self.__reference_coordinates

    def update_box_size(self):
        self.__reference_coordinates = self.calculate_reference_coordinates()

    def box_corner_coordinates(self):
        size_x = self.scale[0]
        size_y = self.scale[1]
        size_z = self.scale[2]
        p1 = -self.scale / 2
        p2 = p1 + np.array([0, 0, size_z])
        p3 = p1 + np.array([size_x, 0, size_z])
        p4 = p1 + np.array([size_x, 0, 0])
        p5 = p1 + np.array([0, size_y, 0])
        p6 = p5 + np.array([0, 0, size_z])
        p7 = p5 + np.array([size_x, 0, size_z])
        p8 = p5 + np.array([size_x, 0, 0])

        return np.array([p1, p2, p3, p4, p5, p6, p7, p8])

    def calculate_reference_coordinates(self):
        points = self.box_corner_coordinates().transpose()
        rot_points = self.rotation_matrix @ points + self.position.reshape((3, -1))
        return rot_points

    def points_to_box_coordinate_system(self, points_ref):
        # points = N x 3 matrix in reference coordinates, e.g. point_cloud.data
        points_box = self.inverse_rotation_matrix @ (points_ref.T - self.position.reshape((3, -1)))
        return points_box.T

    def points_inside(self, points_box):
        # points_box = N x 3 matrix in box coordinates, eg points_to_box_coordinate_system(point_cloud.data)
        N = points_box.shape[0]
        condition = np.ones(N).astype(bool)
        for i in range(3):
            c1 = points_box[:, i] >= - self.scale[i] / 2
            c2 = points_box[:, i] <= self.scale[i] / 2
            condition = condition * c1 * c2
        return condition

    def distance_to_closest_lidar_point(self, points_within_box_in_box_sys):
        # points_in_box_in_box_sys = lidar points represented in box coordinate system only with points within the
        # current box, i.e. use both points_to_box_coordinate_system and points_inside
        min_vals = np.min(points_within_box_in_box_sys, axis=0)
        max_vals = np.max(points_within_box_in_box_sys, axis=0)
        diff_min = min_vals + self.scale / 2
        diff_max = self.scale / 2 - max_vals
        min_dist = np.min([diff_max, diff_min])
        return min_dist


class BoundingBox3DQuaternion(BoundingBox3D):
    @property
    def rotation_matrix(self):
        if self.__rotation_matrix is None:
            rotation_obj = Rotation.from_quat(self.rotation)
            self.__rotation_matrix = rotation_obj.as_dcm()
        return self.__rotation_matrix


class PointCloud:
    collection = dict()

    def __init__(self, input_id, point_cloud_name, storage_directory='point_cloud_folder'):
        self.input_id = input_id
        self.point_cloud_name = point_cloud_name
        self.storage_directory = storage_directory
        self.data = None
        self.intensity = None
        PointCloud.collection[self.input_id] = self

    def download_point_cloud(self):
        if not os.path.isdir(self.storage_directory):
            os.mkdir(self.storage_directory)
        if not os.path.isfile(f'{self.storage_directory}/{self.point_cloud_name}'):
            command = f'gsutil cp gs://annotell-files/pointclouds/{self.point_cloud_name} {self.storage_directory}/{self.point_cloud_name}'
            error_code = os.system(command)
            if error_code != 0:
                raise RuntimeError(f'Download of file {self.point_cloud_name} failed.')

    def load_point_cloud(self, cache_binary=False):
        """Loads point cloud from storage folder, downloading the the point cloud from GCS if necessary, and caching it.
        Binary caching is faster at load time, but slower at download/store time."""
        self.make_available(cache_binary=cache_binary)
        point_cloud_path = f'{self.storage_directory}/{self.point_cloud_name}'
        if self._has_binary():
            all_point_cloud_data = np.load(point_cloud_path + ".npy")
        else:
            all_point_cloud_data = np.loadtxt(point_cloud_path, skiprows=10)
        try:
            self.data = all_point_cloud_data[:, :3]
            self.intensity = all_point_cloud_data[:, 3]
        except IndexError:
            # empty lidar cloud
            pass

    def make_available(self, cache_binary=False):
        point_cloud_path = f'{self.storage_directory}/{self.point_cloud_name}'
        if not os.path.isfile(point_cloud_path):
            self.download_point_cloud()

        if cache_binary and not self._has_binary():
            np.save(point_cloud_path + ".npy", np.loadtxt(point_cloud_path, skiprows=10))

    def _has_binary(self):
        return os.path.isfile(f'{self.storage_directory}/{self.point_cloud_name}' + ".npy")

    @staticmethod
    def get(input_id):
        try:
            return PointCloud.collection[input_id]
        except KeyError:
            raise KeyError(f'Pointcloud to input {input_id} is not present')


def view_cloud(cloud, *boxes, asynchronous=False, point_size=0.002):
    """cloud : Iterable[[x1, y1, z1], [x2, y2, z2], ...], *boxes : Iterable[BoundingBox3D]
    Use the pptk viewer to show a point cloud (in one color) together with an iterable of bounding boxes,
    where their corners are marked in another color. Blocks by default until enter/escape is pressed in the viewer,
    use asynchronous=True to be non-blocking. point_size is radius of ball around each point in the viewer.
    Requires pptk to be installed from pypi."""
    try:
        import pptk
    except ImportError as e:
        e.msg = "The module pptk needs to be installed to view point clouds. " \
                "See https://heremaps.github.io/pptk/install.html"
        raise e
    if len(boxes) > 0:
        box_coords = np.concatenate([x.calculate_reference_coordinates().transpose() for x in boxes])
        view_points = np.concatenate([cloud, box_coords])
    else:
        box_coords = np.array([[]])
        view_points = cloud

    viewer = pptk.viewer(view_points)
    viewer.set(point_size=point_size)
    colors = np.concatenate([np.zeros(len(cloud)), np.ones(len(box_coords))])
    viewer.attributes(colors)

    if not asynchronous:
        viewer.wait()


def bounding_box_3d_factory(jsonb):
    object_id = jsonb[Constants.ID]
    scale = np.abs(np.array(jsonb[Constants.SCALE]))
    position = np.array(jsonb[Constants.POSITION])
    rotation = np.array(jsonb[Constants.ROTATION][:3])
    assert jsonb[Constants.ROTATION][3] == Constants.XYZ
    return BoundingBox3D(object_id, scale, position, rotation)


def bounding_box_as_list(bbox):
    """Useful for storing boxes, for example as json"""
    return [np.array2string(x) if type(x) == np.ndarray else x for x in
            [bbox.object_id, bbox.scale, bbox.position, bbox.rotation]]


def list_as_bounding_box(data):
    """Inverse of bounding_box_as_list"""
    obj_id = data[0]
    scale = np.fromstring(data[1][1:-1], sep=" ")
    position = np.fromstring(data[2][1:-1], sep=" ")
    rotation = np.fromstring(data[3][1:-1], sep=" ")
    return BoundingBox3D(obj_id, scale, position, rotation)


def generate_objects_from_data(raw_data_annotations):
    list_of_lidar_annotations = list()
    for ix, data in enumerate(copy.deepcopy(raw_data_annotations)):
        assignments_id = data[0]
        users_id = data[1]
        assignments_completed = data[2]
        continue_chain = data[3]
        tasks_id = data[4]
        inputs_id = data[5]
        actions_name = data[6]
        builds_on_assignments_id = data[7]
        organizations_id = data[8]
        try:
            annotation_objects_raw = data[9]['result']['objects']
        except:
            continue

        data_content = list()
        for ao in annotation_objects_raw:
            if None in ao['rotation']:
                print('Warning! An object in assignment id %s had None in rotation.' % assignments_id)
                continue
            data_content.append(bounding_box_3d_factory(ao))

        anno = Annotation(assignments_id, users_id, assignments_completed, continue_chain, tasks_id, inputs_id,
                          actions_name, builds_on_assignments_id, organizations_id, data_content)

        list_of_lidar_annotations.append(anno)

    return list_of_lidar_annotations


def generate_point_cloud_objects(raw_data_point_clouds, display_progress=False, cache_binaries=False):
    list_of_pc = list()
    num_pcs = len(raw_data_point_clouds)
    for ix, data in enumerate(raw_data_point_clouds):
        point_cloud_name = data[0]
        input_id = data[1]
        tmp_pc = PointCloud(input_id, point_cloud_name)
        tmp_pc.make_available(cache_binary=cache_binaries)
        list_of_pc.append(tmp_pc)
        if (ix + 1) % 100 == 0:
            print(f"Generated pointcloud {ix + 1} out of {num_pcs}")
    return list_of_pc

def r_and_iou_on_pair(datas):
    l_boxes = list()
    for i, obj_data in enumerate(datas):
        tmp_pos = np.array([obj_data['x_coord'], obj_data['y_coord'], obj_data['z_coord']])
        tmp_rot = np.array([obj_data['roll'], obj_data['pitch'], obj_data['yaw']])
        tmp_scale = np.array([obj_data['width'], obj_data['length'], obj_data['height']])
        lidar_box = BoundingBox3D(position=tmp_pos,
                                  rotation=tmp_rot,
                                  scale=tmp_scale,
                                  object_id=i)
        l_boxes.append(lidar_box)

    r = np.linalg.norm(lidar_box.position)
    if len(datas)==2:
        iou = calculate_iou(*l_boxes)
    elif len(datas)==1:
        iou = 0
    else:
        iou = 0
    return r, iou
