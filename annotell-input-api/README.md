# Annotell Input API Client

Python 3 library providing access to Annotell Input API

To install with pip run `pip install annotell-input-api`

# Getting Started

## Authentication

Set env ANNOTELL_CREDENTIALS to the credentials file provided to you by Annotell,
see [annotell-auth](https://github.com/annotell/annotell-python/tree/master/annotell-auth).

Once set, the easiest way to test if everything is working is to use the
command line util `annoutil` (this is a part of the pip package).

```console
$ annoutil projects
```

Alternatively, instantiate a client and use the correspondning method.

```python
import annotell.input_api.input_api_client as IAC
client = IAC.InputApiClient()
client.list_projects()
```

## Create Images

Images inputs can be created from python via the _upload_and_create_images_input_job_ method. An important feature here is the ability to add a _**dryrun**_ parameter to the method call, this will make a call to the Input API but only run the validation steps and not create any inputs.

**We start out by creating a representation of our images.** The representation consists of the image name \(excluding the path to the image\) and the source of the image. In this case, we want to create a scene consisting of two images _image1_ and _image2_. We also specify a folder where the image is located.

```python
image1 = "filename1.jpg"
image2 = "filename2.jpg"
images = [IAM.Image(filename=image1, source="CAM1"),
          IAM.Image(filename=image2, source="CAM2")]
images_files = IAM.ImagesFiles(images)
folder = Path("/home/user_name/example_path")
```

**We also need to create a** _**SceneMetaData**_ **object.** The only required field is the external id string which the client can use to identify the input. We can also add a _**SourceSpecification**_ object which defines which source that should be shown first, the _source_order_, or a mapping of source names to a prettier name version displayed in the UI.

```python
source_spec = IAM.SourceSpecification(source_to_pretty_name={"CAM1": "FC", "CAM2": "BC"},
                                          source_order=["CAM1", "CAM2"])
images_metadata = IAM.SceneMetaData(external_id="2020-06-16",
                                    source_specification=source_spec)
```

```python
# Create objects representing the images and the scene
image1 = "filename1.jpg"
image2 = "filename2.jpg"
images = [IAM.Image(filename=image1, source="CAM1"),
          IAM.Image(filename=image2, source="CAM2")]
images_files = IAM.ImagesFiles(images)
folder = Path("/home/user_name/example_path")

# Project
project = "<external_id>"

response = client.upload_and_create_images_input_job(folder=folder,
                                                     images_files=iam.ImagesFiles(images),
                                                     project=project)
```

Scene with several images and custom source names

```python
# Create objects representing the images and the scene
image1 = "filename1.jpg"
image2 = "filename2.jpg"
images = [IAM.Image(filename=image1, source="CAM1"),
          IAM.Image(filename=image2, source="CAM2")]
images_files = IAM.ImagesFiles(images)
folder = Path("/home/user_name/example_path")

# Project
project = "<external_id>"

# Create Scene meta data
source_spec = IAM.SourceSpecification(source_to_pretty_name={"CAM1": "FC", "CAM2": "BC"},
                                      source_order=["CAM1", "CAM2"])
images_metadata = IAM.SceneMetaData(external_id="2020-06-16",
                                    source_specification=source_spec)
response = client.upload_and_create_images_input_job(folder=folder,
                                                     images_files=iam.ImagesFiles(images),
                                                     metadata=images_metadata,
                                                     project=project)
```

## Create Point clouds with images

We start off by creating a representation of the images and the point cloud that make up the scene along with a SourceSpecification for the images.

```python
# Create representation of images and point clouds + source specification images
image1 = IAM.Image(filename="filename_image1.jpg", source="RFC01")
pc = IAM.PointCloud(filename="filename_pc.pcd")
point_clouds_with_images = IAM.PointCloudsWithImages(images=[image1],
                                                     point_clouds=[pc])
folder = Path("/home/user_name/example_path/")  # Folder to where the data is
```

### Scene metadata

Next, we can create a CalibratedSceneMetaData object and either select a project+input batch or input list for where we want to add the inputs. See calibration section for more information on how to retrieve a calibration_id.

Now everything required is prepared in order to use `create_inputs_point_cloud_with_images`.

```python
scene_external_id = "Scene X collection 2020-06-16"
metadata = IAM.CalibratedSceneMetaData(external_id=scene_external_id,
                                       source_specification=source_specification,
                                       calibration_id=created_calibration.id)
client.create_inputs_point_cloud_with_images(folder=folder,
                                             point_clouds_with_images=point_clouds_with_images,
                                             metadata=metadata,
                                             project="my_project")
```

### Full example code

Below is the full code for creating an input consisting of a point cloud and one images. Including creating a new calibration for the input.

```python
import annotell.input_api.input_api_model as IAM
import annotell.input_api.model.calibration as Calibration
import annotell.input_api.input_api_client as IAC
from pathlib import Path
client = IAC.InputApiClient()
# Create representation of images and point clouds + source specification images
image1 = IAM.Image(filename="filename_image1.jpg", source="RFC01")
pc = IAM.PointCloud(filename="filename_pc.pcd")
point_clouds_with_images = IAM.PointCloudsWithImages(images=[image1],
                                                     point_clouds=[pc])
folder = Path("/home/user_name/example_path/")  # Folder to where the data is
# Create lidar calibration
lidar_position = Calibration.Position(x=0.0, y=0.0, z=0.0)
lidar_rotation = Calibration.RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)
lidar_calibration = Calibration.LidarCalibrationExplicit(position=lidar_position,
                                                         rotation_quaternion=lidar_rotation)
# Create a camera calibration
rfc_01_camera_type = Calibration.CameraType.PINHOLE
rfc_01_position = Calibration.Position(x=0.0, y=0.0, z=0.0)  # similar to Lidar
rfc_01_rotation = Calibration.RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)  # similar to Lidar
rfc_01_camera_matrix = Calibration.CameraMatrix(fx=3450, fy=3250, cx=622, cy=400)
rfc_01_distortion_coefficients = Calibration.DistortionCoefficients(k1=0.0, k2=0.0, p1=0.0, p2=0.0, k3=0.0)
rfc_01_properties = Calibration.CameraProperty(camera_type=rfc_01_camera_type)
camera_calibration_rfc_01 = Calibration.CameraCalibrationExplicit(position=rfc_01_position,
                                                                  rotation_quaternion=rfc_01_rotation,
                                                                  camera_matrix=rfc_01_camera_matrix,
                                                                  distortion_coefficients=rfc_01_distortion_coefficients,
                                                                  camera_properties=rfc_01_properties,
                                                                  image_height=920,
                                                                  image_width=1244)

# Create calibration for the scene
calibration_dict = dict(RFC01=camera_calibration_rfc_01,
                        lidar=lidar_calibration)
calibration = IAM.Calibration(calibration_dict=calibration_dict)
calibration_external_id = "Collection 2020-06-16"
calibration_spec = IAM.CalibrationSpec(external_id=calibration_external_id,
                                       calibration=calibration)
# Create the calibration using the Input API client
created_calibration = client.create_calibration_data(calibration_spec=calibration_spec)

# Create metadata
scene_external_id = "Scene X collection 2020-06-16"
metadata = IAM.CalibratedSceneMetaData(external_id=scene_external_id,
                                       calibration_id=created_calibration.id)

# Add input                                       
client.create_inputs_point_cloud_with_images(folder=folder,
                                             point_clouds_with_images=point_clouds_with_images,
                                             metadata=metadata,
                                             project="my_project")
```

### Calibration
Inputs including both a 2D and 3D representation such as **point cloud with images** require a calibration relating the camera sensors with the lidar sensors in terms of location and rotation. The calibration file should also contain the required information for projecting 3D points into the image plane of the camera.

A Calibration object consists of a set of key-value pairs where the key is the name of the source and the value is either a _LidarCalibrationExplicit_ object or a _CameraCalibrationExplicit_ object depending on the sensor.

#### Listing existing calibrations
Previously created calibrations are available through either client or `annoutil`

```console
$ annoutil calibration
```

Or to get the calibration matching an external identifier
```python
client.get_calibration_data(external_id="Collection 2020-06-16")
```



#### Creating a lidar calibration

A lidar calibration is represented as a _LidarCalibrationExplicit_ object and consists of a position expressed with three coordinates and a rotation in the form of a [Quaternion](https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation). See the code example below for creating a basic _LidarCalibrationExplicit_ object.

```python
import annotell.input_api.model.calibration as Calibration
# Create lidar calibration
lidar_position = Calibration.Position(x=0.0, y=0.0, z=0.0)
lidar_rotation = Calibration.RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)
lidar_calibration = Calibration.LidarCalibrationExplicit(position=lidar_position,
                                                         rotation_quaternion=lidar_rotation)
```

#### Creating a camera calibration

A camera calibration is represented as a CameraCalibrationExplicit object. The Camera calibration format is based on [OpenCVs](https://docs.opencv.org/3.4/d4/d94/tutorial_camera_calibration.htm) format and this [paper](http://www.robots.ox.ac.uk/~cmei/articles/single_viewpoint_calib_mei_07.pdf). The camera calibration consists of the following set of key-value pairs.

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

Below is a code sample for representing a camera calibration using a CameraCalibrationExplicit object.

```python
rfc_01_camera_type = Calibration.CameraType.PINHOLE
rfc_01_position = Calibration.Position(x=0.0, y=0.0, z=0.0)  # similar to Lidar
rfc_01_rotation = Calibration.RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)  # similar to Lidar
rfc_01_camera_matrix = Calibration.CameraMatrix(fx=3450, fy=3250, cx=622, cy=400)
rfc_01_distortion_coefficients = Calibration.DistortionCoefficients(k1=0.0, k2=0.0, p1=0.0, p2=0.0, k3=0.0)
rfc_01_properties = Calibration.CameraProperty(camera_type=rfc_01_camera_type)
camera_calibration_rfc_01 = Calibration.CameraCalibrationExplicit(position=rfc_01_position,
                                                                  rotation_quaternion=rfc_01_rotation,
                                                                  camera_matrix=rfc_01_camera_matrix,
                                                                  distortion_coefficients=rfc_01_distortion_coefficients,
                                                                  camera_properties=rfc_01_properties,
                                                                  image_height=920,
                                                                  image_width=1244)
```

We tie the calibration together by creating a dictionary mapping the source name to the corresponding calibration. We then create a _Calibration_ object and a _CalibrationSpecification_ object which we then use to create a calibration in the Annotell platform. The external id can be used for querying for the calibration file and also for relating the calibration in our system to how the client refers to it.

```python
# Create calibration for the scene
calibration_dict = dict(RFC01=camera_calibration_rfc_01,
                        lidar=lidar_calibration)
calibration = IAM.Calibration(calibration_dict=calibration_dict)
calibration_external_id = "Collection 2020-06-16"
calibration_spec = IAM.CalibrationSpec(external_id=calibration_external_id,
                                       calibration=calibration)
# Create the calibration using the Input API client
created_calibration = client.create_calibration_data(calibration_spec=calibration_spec)
```

Note that you can, and should, reuse the same calibration for multiple scenes if possible.

## Dealing with errors

When the client sends a http request to the Input API and waits until it receives a response. If the response code is 2xx \(the status code for a successful call\) the client converts the received message into a python object which can be viewed or used. However if the Input API responds with an error code \(4xx or 5xx\) the python client will raise an error. It's up to the user to decide if and how the want to handle this error.


# Changelog

All notable changes to this project will be documented in this file.

## [0.3.11] - 2020-12-14
### Changed
- Deserialization bugfix in models for `InputBatch` and `InputBatch`.

## [0.3.10] - 2020-12-01
### Added
- Minor fix in annoutil

## [0.3.9] - 2020-11-26

### Added

- Bump of required python version to >=3.7
- New explicit models for `lidar` and `camera calibration` added.
- `publish_batch` which accepts project identifier and batch identifier and marks the batch as ready for annotation.

### Changed

- Deprecation warning for the old `lidar` and `camera calibration` models. No other change in functionality.

## [0.3.8] - 2020-11-13

### Added

- `get_inputs` which accepts a project ID or project identifier (external ID) and returns inputs connected to the project. `invalidated` filter parameter to optionally filter only invalidated inputs. Also exposed in annoutil as `annoutil projects 1 --invalidated`.

### Changed

- `invalidate_inputs` now accepts annotell `internal_ids (UUID)` instead of Annotell specific input ids.

## [0.3.7] - 2020-11-06

### Changed

- bug fix related to oauth session

## [0.3.6] - 2020-11-02

### Changed

- SLAM - add cuboid timespans, `dynamic_objects` not includes both `cuboids` and `cuboid_timespans`

## [0.3.5] - 2020-10-19

### Added

- Add support for `project` and `batch` identifiers for input request.
  Specifying project and batch adds input to specified batch.
  When only sending project, inputs are added to the latest open batch for the project.

### Deprecated

- `input_list_id` will be removed in the 0.4.x version

## [0.3.4] - 2020-09-10

### Changed

- SLAM - add required `sub_sequence_id` and optional `settings`

## [0.3.3] - 2020-09-10

### Changed

- SLAM - add required `sequence_id`

## [0.3.2] - 2020-09-01

### Changed

- SLAM - startTs and endTs not optional in Slam request

## [0.3.1] - 2020-07-16

### Changed

- If the upload of point clouds or images crashes and returns status code 429, 408 or 5xx the script will
  retry the upload before crashing. The default settings may be changed when initializing the `InputApiClient`
  by specifying values to the `max_upload_retry_attempts` and `max_upload_retry_wait_time` parameters.

## [0.3.0] - 2020-07-03

### Changed

- The method `create_inputs_point_cloud_with_images` in `InputApiClient` now takes an extra parameter: `dryrun: bool`.
  If set to `True` all the validation checks will be run but no inputJob will be created, and
  if it is set to `False` an inputJob will be created if the validation checks all pass.

### Bugfixes

- Fixed bug where the uploading of .csv files to GCS crashed if run on some windows machines.

## [0.2.9] - 2020-07-02

### Added

- New public method in `InputApiClient`: `count_inputs_for_external_ids`.

## [0.2.8] - 2020-06-30

### Added

- Docstrings for all public methods in the `InputApiClient` class

## [0.2.7] - 2020-06-29

### Added

- Require time specification to be send when posting slam requests

## [0.2.6] - 2020-06-26

### Changed

- Removed `CalibrationSpec` from `CalibratedSceneMetaData` and `SlamMetaData`. Updated
  so that `create_calibration_data` in `InputApiClient` only takes a `CalibrationSpec`
  as parameter.

## [0.2.5] - 2020-06-22

### Bugfixes

- Fixed issue where a path including a "~" would not expand correctly.

## [0.2.4] - 2020-06-17

### Changed

- Changed pointcloud_with_images model. Images and point clouds are now represented as `Image` and `PointCloud` containing filename and source. Consequently, `images_to_source` is removed from `SourceSpecification`.

### Added

- create Image inputs via `create_images_input_job`
- It's now possible to invalidate erroneous inputs via `invalidate_inputs`
- Support for removing specific inputs via `remove_inputs_from_input_list`
- SLAM support (not generally available)

### Bugfixes

- Fixed issue where annoutils would not deserialize datas correctly when querying datas by internalId

## [0.2.3] - 2020-04-21

### Changed

- Changed how timestamps are represented when receiving responses.

## [0.2.2] - 2020-04-17

### Added

- Methods `get_datas_for_inputs_by_internal_ids` and `get_datas_for_inputs_by_external_ids` can be used to get which `Data` are part of an `Input`, useful in order to check which images, lidar-files have been uploaded. Both are also available in the CLI via :

```console
$ annoutil inputs --get-datas <internal_ids>
$ annoutil inputs-externalid --get-datas <external_ids>
```

- Support has been added for `Kannala` camera types. Whenever adding calibration for `Kannala` undistortion coefficients must also be added.
- Calibration is now represented as a class and is no longer just a dictionary, making it easier to understand how the Annotell format is structured and used.

## [0.2.0] - 2020-04-16

### Changed

- Change constructor to disable legacy api token support and only accept an `auth` parameter

## [0.1.5] - 2020-04-07

### Added

- Method `get_input_jobs_status` now accepts lists of internal_ids and external_ids as arguments.
