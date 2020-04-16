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

## [0.2.0] - 2020-04-16
- Change constructor to disable legacy api token support and only accept an `auth` parameter

## [0.1.5] - 2020-04-07
- Method `get_input_jobs_status` now accepts lists of internal_ids and external_ids as arguments.

