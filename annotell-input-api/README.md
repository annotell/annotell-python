# Annotell Input Api

Python 3 library providing access to Annotell Input Api 

To install with pip run `pip install annotell-input-api`


## Example
Set env ANNOTELL_CREDENTIALS to the credentials file provided to you by Annotell,
see [annotell-auth](https://github.com/annotell/annotell-python/tree/master/annotell-auth).

Once set, the easiest way to test if everything is working is to use the
command line util `annoutil` (this is a part of the pip package). 
```console
$ annoutil projects
```


# Changelog

All notable changes to this project will be documented in this file.
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

