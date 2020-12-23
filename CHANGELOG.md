Changelog
=========

<!--next-version-placeholder-->

## v3.0.0 (2020-12-23)
### Feature
* **regex:** Replace REGEX_DISABLED environment variable with REBULK_REGEX_ENABLED ([`d5a8cad`](https://github.com/Toilal/rebulk/commit/d5a8cad6281533ee549a46ca70e1a25e5777eda3))
* Add python 3.8/3.9 support, drop python 2.7/3.4 support ([`048a15f`](https://github.com/Toilal/rebulk/commit/048a15f90833ba8d33ea84d56e9955d31b514dc3))

### Breaking
* regex module is now disabled by default, even if it's available in the python interpreter. You have to set REBULK_REGEX_ENABLED=1 in your environment to enable it, as this module may cause some issues.  ([`d5a8cad`](https://github.com/Toilal/rebulk/commit/d5a8cad6281533ee549a46ca70e1a25e5777eda3))
* Python 2.7 and 3.4 support have been dropped  ([`048a15f`](https://github.com/Toilal/rebulk/commit/048a15f90833ba8d33ea84d56e9955d31b514dc3))
