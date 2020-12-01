# Key Concepts

## Project

Project is the top-most concept when interfacing with the Annotell Platform. It is possible to have multiple ongoing projects, and they act as a container for other annotell resources.
Project setup is performed by the Annotell Professional Services team during the Guideline Agreement Process (GAP) of a new client engagement.

To use projects within the Annotell APIs, they can be identified using either a numeric annotell ID or by an external identifier which can be specified.

<aside class="notice">
Work in progress: To harmonize the APIs, annotell project IDs will be phased out in favour of external identifiers.
</aside>

## Batch

Input batches allow grouping of inputs into smaller batches within a project. By default, every project has at least one input batch.

Ongoing projects can benefit from using batches in two ways

- Group inputs collected at the same time
- Perform guideline or task definition changes without the need for retroactive changes.

### Batch Status

| Status      | Description                                                                                                            |
| ----------- | ---------------------------------------------------------------------------------------------------------------------- |
| pending     | Batch has been created but is still not fully configured by Annotell. Either during project setup or requested changes |
| open        | Batch is open for new inputs                                                                                           |
| ready       | Batch has been published and no longer open for new inputs.                                                            |
| in-progress | Annotell has started annotation of inputs within the batch.                                                            |
| completed   | Annotations has been completed.                                                                                        |

## Request

During GAP, projects are divided into different annotation types. E.g. a project of 2D images can be divided into lane annotation and object detection. Within Annotell this is represented as a **request**.
A Request can be viewed as a drawing tool - we divide big and complex projects into several independent annotation types.
This makes it possible to:

- Reduce the mental strain on annotators
- Higher bandwidth - more annotators can work on the same data in parallel
- Build simple user interfaces

### Guideline

In order for us to produce annotations we need to know what and how to annotate. This type of information is found in something that's called a Guideline. A guideline contains information on what to mark (e.g. vehicles and pedestrians) as well as how (e.g. bounding box). A guideline also includes information about how to interpret the data, i.e. what does it mean that a vehicle is "heavily occluded"?

### Task Definition

TaskDefinition - Describes what we’re annotating. How many objects? Bounding box, semantic segmentation or lines/splines? What are the properties? Used by the Annotell App to construct the drawing tool.

## Input

The Annotell Platform has support for annotating different types of data together, e.g:

- Two (or more) images of the same scene from different cameras
- Images (2D) + Lidar (3D)

An **input** specifies how these different resources belong together using metadata about the scene and calibrations (how sensors relate to each other).
Inputs can be created via Annotell's Input API, which has support for several different types of input types.

| Type                   | Description                                                 |
| ---------------------- | ----------------------------------------------------------- |
| IMAGES                 | One or several images                                       |
| VIDEO                  | Video in .mp4 format                                        |
| POINTCLOUD_WITH_IMAGES | Single frame point cloud with one or several images         |
| POINTCLOUD_WITH_VIDEO  | Sequence of frames with both (3D) pointcloud and (2D) video |

## Annotation
