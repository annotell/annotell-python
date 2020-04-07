# Annotell Input Api

Python 3 library providing access to Annotell Input Api 

To install with pip run `pip install annotell-input-api`


## Example
Set env ANNOTELL_API_TOKEN to the API token provided to you by Annnotell.
Once set, the easiest way to test if everything is working is to use the
command line util `annoutil` (this is a part of the pip package). 
```console
$ annoutil projects
```


# Changelog

All notable changes to this project will be documented in this file.

## [0.1.5] - 2020-04-07

### Changed
- Method `get_input_jobs_status` now accepts lists of internal_ids and external_ids as arguments.
