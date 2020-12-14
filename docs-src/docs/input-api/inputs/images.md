---
title: Images
---

### Single Image
Images inputs can be created from python via the _upload_and_create_images_input_job_ method.

The representation consists of the image name \(excluding the path to the image\) and the source of the image. In this case, we want to create a scene consisting of one image _image1_. We also specify a folder where the image is located.

We start out by creating a representation of our image.

```python
image1 = "filename1.jpg"
images = [IAM.Image(filename=image1)]
images_files = IAM.ImagesFiles(images)
folder = Path("/home/user_name/example_path")
```

Next we can upload the images to a project

```python
# Project
project = "<external_id>"

response = client.upload_and_create_images_input_job(
    folder=folder,
    images_files=iam.ImagesFiles(images),
    project=project)
```


:::tip Use dryrun to validate input
Setting `dryrun` parameter to true in the method call, will validate the input using the Input API but not create any inputs.
:::

### Image with Source Specification

In a Scene with several images, it is possible to specify custom source names, and in which order they should appear.

we do this by adding _**SceneMetaData**_ to the input, with the following properties.

| Property             | Description                                                                                                                                                                                                                                |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| external_id          | Id which can be used to track progress of annotations with.                                                                                                                                                                                |
| source_specification | Additional information about sources, includes `source_to_pretty_name` and `source_order`. Defines which source that should be shown first, the source_order, or a mapping of source names to a prettier name version displayed in the UI. |


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
# Create Input
response = client.upload_and_create_images_input_job(folder=folder,
                                                     images_files=iam.ImagesFiles(images),
                                                     metadata=images_metadata,
                                                     project=project)
```