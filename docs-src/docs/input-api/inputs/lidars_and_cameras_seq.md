---
title: LidarsAndCamerasSeq
---

A `LidarsAndCamerasSeq` input consists of a sequence of camera images and lidar point clouds. Unlike single-frame input types we also have to specify the sequential relationship between our _frames_, where each frame consists on 1-8 camera images, as well as lidar point clouds.

:::info no multi-lidar support currently
Currently there is only support for supplying a single point cloud per frame.
:::

## Creating a list of frames

The sequential relationship is expressed via a list of `Frame` objects. This representation expresses the ordering of the frames, but it does not include the _relative temporal_ relationship between the frames in the list.
```python
frame_1 = IAM.Frame(...)
frame_2 = IAM.Frame(...)
frames = [frame_1, frame_2]
```

In other words, this representation captures that `frame_1` comes before `frame_2`, but does not express how much time has passed between the two frames. In order to express how much time has passed between the frames we need to specify the field `relative_timestamp` for each frame object. If we for example know that we have collected and aggregated our sensor data at 2Hz, then we would express that as

```python
frame_1 = IAM.Frame(..., relative_timestamp=0)
frame_2 = IAM.Frame(..., relative_timestamp=500)
frames = [frame_1, frame_2]
```
:::tip Why is relative time important?
Specifying the time relationship between frames is important in order to enable different types of advanced annotator assistance tools in the Annotell platform. These tools enable a **significant** reduction in annotation time, while keeping quality high. 
:::

In addition to supplying the sequential and temporal information for our `Frame` objects we also need to specify the camera images and lidar point clouds that constitute each frame. This is done by passing a list of `PointCloudFrame` and `ImageFrame` objects, where each of these objects contains the path to the underlying file as well as the sensor name. Finally, we also need to specify the `frame_id` of each frame. 


```python
frame_1 = IAM.Frame(
    frame_id="1",
    point_cloud_frames=[
        IAM.PointCloudFrame("~/lidar_RFL01_1.pcd", sensor_name="RFL01"),
    ],
    image_frames=[
        IAM.ImageFrame("~/img_RFC01_1.jpg", sensor_name="RFC01"),
        IAM.ImageFrame("~/img_RFC02_2.jpg", sensor_name="RFC02"),
        IAM.ImageFrame("~/img_RFC03_3.jpg", sensor_name="RFC03")
    ]),
    relative_timestamp=0
)
frame_2 = IAM.Frame(
    frame_id="2",
    point_cloud_frames=[
        IAM.PointCloudFrame("~/lidar_RFL01_2.pcd", sensor_name="RFL01"),
    ],
    image_frames=[
        IAM.ImageFrame("~/img_RFC01_2.jpg", sensor_name="RFC01"),
        IAM.ImageFrame("~/img_RFC02_2.jpg", sensor_name="RFC02"),
        IAM.ImageFrame("~/img_RFC03_2.jpg", sensor_name="RFC03")
    ]),    
    relative_timestamp=500
)
frames = [frame_1, frame_2]
```
:::note Be careful with sensor names
Make sure that the provided sensor names for each image and lidar frame are present in the calibration supplied to the input. Otherwise the input cannot be created. For more information about this see the [Calibration](/input-api/calibration.md) section.
:::

## Creating the input
In order to create the input we need to use our list of `Frame` objects and specify the parameters `external_id` and `calibration_id` as well as the optional parameter `sensor_specification`.

| Parameter            | Description                                                                                                                                                                                                                                |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| external_id          | Id which can be used to track progress of annotations with.                                                                                                                                                                                |
| sensor_specification | Additional information about sensors, includes `sensor_to_pretty_name` and `sensor_order`. Defines which sensor that should be shown first, the sensor_order, or a mapping of sensor names to a prettier name version displayed in the Annotell Annotation Tool. |
| calibration_id       | Which calibration to use for the input.                                                                                                                                                                                                    |
:::tip reuse calibration
Note that you can, and should, reuse the same calibration for multiple inputs if possible.
:::

All that is left after creating the `LidarsAndCamerasSequence` object is selecting which project to upload the input to and then call the `create` method. 

```python
import annotell.input_api.input_api_client as IAC
import annotell.input_api.model as IAM

client = IAC.InputApiClient()

# Get existing calibration
calibration_external_id = "<calibration-identifier>"
calibration = client.calibration.get_calibration(external_id=calibration_external_id)[-1]

lidar_and_camera_seq = IAM.LidarsAndCamerasSequence(
    external_id="input1",
    frames=[
        IAM.Frame(
            frame_id="1",
            relative_timestamp=0,
            point_cloud_frames=[
                IAM.PointCloudFrame("~/lidar_1.pcd", sensor_name="lidar"),
            ],
            image_frames=[
                IAM.ImageFrame("~/img_RFC01_1.jpg", sensor_name="RFC01"),
                IAM.ImageFrame("~/img_RFC02_2.jpg", sensor_name="RFC02"),
                IAM.ImageFrame("~/img_RFC03_3.jpg", sensor_name="RFC03")
            ]),
        IAM.Frame(
            frame_id="2",
            relative_timestamp=500,
            point_cloud_frames=[
                IAM.PointCloudFrame("~/lidar_2.pcd", sensor_name="lidar"),
            ],
            image_frames=[
                IAM.ImageFrame("~/img_RFC01_2.jpg", sensor_name="RFC01"),
                IAM.ImageFrame("~/img_RFC02_2.jpg", sensor_name="RFC02"),
                IAM.ImageFrame("~/img_RFC03_2.jpg", sensor_name="RFC03")
            ]),
    ],
    calibration_id=calibration.id,
)

# Project - Available via `client.list_projects()`
project = "<project-identifier>"

# Add input
client.lidar_and_image_sequence.create(lidar_and_camera_seq,
                                       project=project,
                                       dryrun=True)
```
:::tip Use dryrun to validate input
Setting `dryrun` parameter to true in the method call, will validate the input using the Input API but not create any inputs.
:::
