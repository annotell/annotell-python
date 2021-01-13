# Annotell Input API Client

Python 3 library providing access to Annotell Input API

To install with pip run `pip install annotell-input-api`

# Documentation
All available documentation for the Annotell Input API Client can be found here:
https://annotell.github.io/annotell-python/docs/

# Changelog
All notable changes to this project will be documented in this file.

## [0.3.12] - 2021-01-13
### Changed
- Removed getting started documentation from README.md and instead link to new docs.

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
