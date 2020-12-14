---
title: Calibration
---

Inputs including both a 2D and 3D representation such as **point cloud with images** require a calibration relating the camera sensors with the lidar sensors in terms of location and rotation. The calibration should also contain the required information for projecting 3D points into the image plane of the camera.

A Calibration object consists of a set of key-value pairs where the key is the name of the source (i.e. sensor name) and the value is either a _LidarCalibrationExplicit_ object or a _CameraCalibrationExplicit_ object depending on the sensor.

A lidar calibration is represented as a _LidarCalibrationExplicit_ object and consists of a position expressed with three coordinates and a rotation in the form of a [Quaternion](https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation). See the code example below for creating a basic _LidarCalibrationExplicit_ object.

The Camera calibration format is based on [OpenCVs](https://docs.opencv.org/3.4/d4/d94/tutorial_camera_calibration.htm) format and this [paper](http://www.robots.ox.ac.uk/~cmei/articles/single_viewpoint_calib_mei_07.pdf). Currently three different camera types are supported: `PINHOLE`, `FISHEYE` and `KANNALA`. The camera calibration consists of the following set of key-value pairs.

| Key                       | Value                                                                                                                               |
| :------------------------ | :---------------------------------------------------------------------------------------------------------------------------------- |
| rotation_quaternion       | A RotationQuaternion object                                                                                                         |
| position                  | A Position object                                                                                                                   |
| camera_matrix             | A CameraMatrix object                                                                                                               |
| camera_properties         | A CameraProperty object                                                                                                             |
| distortion_coefficients   | A DistortionCoefficients object. Please note that the coefficient _k3_ should be equal to None if the camera type is _Kannala_**.** |
| image_height              | Integer                                                                                                                             |
| image_width               | Integer                                                                                                                             |
| undistortion_coefficients | \(**Optional\)** An UndistortionCoefficients object. This is only used for _Kannala_ cameras.                                       |


## Example: Creating a calibration
Let's say that we want to create a calibration where we have a single lidar and two cameras - one of type `PINHOLE` and the other of type `KANNALA`. We will refer to the lidar sensor as `lidar` while the camera sensors will be referred to as `CAM_PINHOLE` and `CAM_KANNALA` respectively - these will be our source names. 

### Creating a lidar calibration

As a first step we will create a _LidarCalibrationExplicit_ object for our lidar sensor. This amounts to specifying the position and rotation of the sensor.

```python
import annotell.input_api.model.calibration as Calibration

# Create lidar calibration
lidar_position = Calibration.Position(x=0.0, y=0.0, z=0.0)
lidar_rotation = Calibration.RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)
lidar_calibration = Calibration.LidarCalibrationExplicit(position=lidar_position,
                                                         rotation_quaternion=lidar_rotation)
```

### Creating camera calibrations

Next, we have to create a _CameraCalibrationExplicit_ object for each of our two cameras.

```python
cam_pinhole_properties = Calibration.CameraProperty(camera_type=Calibration.CameraType.PINHOLE)
cam_pinhole_position = Calibration.Position(x=0.0, y=0.0, z=0.0)
cam_pinhole_rotation = Calibration.RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)
cam_pinhole_camera_matrix = Calibration.CameraMatrix(fx=3450, fy=3250, cx=622, cy=400)
cam_pinhole_distortion_coefficients = Calibration.DistortionCoefficients(k1=0.0, k2=0.0, p1=0.0, p2=0.0, k3=0.0)

cam_pinhole_camera_calibration = Calibration.CameraCalibrationExplicit(position=cam_pinhole_position,
                                                                       rotation_quaternion=cam_pinhole_rotation,
                                                                       camera_matrix=cam_pinhole_camera_matrix,
                                                                       distortion_coefficients=cam_pinhole_distortion_coefficients,
                                                                       camera_properties=cam_pinhole_properties,
                                                                       image_height=920,
                                                                       image_width=1244)

cam_kannala_properties = Calibration.CameraProperty(camera_type=Calibration.CameraType.KANNALA)
cam_kannala_position = Calibration.Position(x=2.05, y=0.00, z=1.12)
cam_kannala_rotation = Calibration.RotationQuaternion(w=-0.51, x=0.49, y=-0.50, z=0.48)
cam_kannala_camera_matrix = Calibration.CameraMatrix(fx=1934.23, fy=1132.24, cx=1846.47, cy=1846.47)
# Note that k3 parameter is not present for cameras of type Kannala
cam_kannala_distortion_coefficients = Calibration.DistortionCoefficients(k1=-0.01, k2=-0.01, p1=0.02, p2=-0.01)  
# An extra set of undistortion coefficients are necessary for cameras of type Kannala
cam_kannala_undistortion_coefficients = Calibration.UndistortionCoefficients(l1=0.01, l2=0.01, l3=-0.03, l4=0.01)

cam_kannala_camera_calibration = Calibration.CameraCalibrationExplicit(position=cam_kannala_position,
                                                                       rotation_quaternion=cam_kannala_rotation,
                                                                       camera_matrix=cam_kannala_camera_matrix,
                                                                       distortion_coefficients=cam_kannala_distortion_coefficients,
                                                                       undistortion_coefficients=cam_kannala_undistortion_coefficients,
                                                                       camera_properties=cam_kannala_properties,
                                                                       image_height=920,
                                                                       image_width=1244)
```

### Creating the full calibration

At this point we have specified all of the necessary parameters for all of our sensors. The final step is to tie them all together by creating a dictionary mapping the source name to the corresponding calibration. We then create a Calibration object and a CalibrationSpecification object which we then use to create a calibration in the Annotell platform. The external id can be used for querying for the calibration file. 

<aside class="notice">
Note that you can, and should, reuse the same calibration for multiple scenes if possible.
</aside>

```python
import annotell.input_api.input_api_model as IAM

# Create calibration for the scene
calibration_dict = dict(CAM_PINHOLE=cam_pinhole_camera_calibration,
                        CAM_KANNALA=cam_kannala_camera_calibration,
                        lidar=lidar_calibration)

calibration = IAM.Calibration(calibration_dict=calibration_dict)
calibration_external_id = "Collection 2020-06-16"
calibration_spec = IAM.CalibrationSpec(external_id=calibration_external_id,
                                       calibration=calibration)

# Create the calibration using the Input API client
import annotell.input_api.input_api_client as IAC
client = IAC.InputApiClient()
created_calibration = client.create_calibration_data(calibration_spec=calibration_spec)
```

### Listing existing calibrations

As a final step we can fetch the calibration via the external id. This can either be done via the client, or via the CLI annoutil tool. 

```python
client.get_calibration_data(external_id="Collection 2020-06-16")
```

```bash
$ annoutil calibration
```