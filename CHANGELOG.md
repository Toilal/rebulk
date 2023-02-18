Changelog
=========

<!--next-version-placeholder-->

## v3.2.0 (2023-02-18)
### Feature
* **dependencies:** Add python 3.11 support and drop python 3.6 support ([`e4cb0d8`](https://github.com/Toilal/rebulk/commit/e4cb0d854cd8ea80da9abe46d2b3405a873e2020))

### Fix
* Remove pytest-runner from setup_requires ([`4483d17`](https://github.com/Toilal/rebulk/commit/4483d1777f6a61d20ed83da760663aec67e22042))

## v3.1.0 (2021-11-04)
### Feature
* **defaults:** Add overrides support ([#25](https://github.com/Toilal/rebulk/issues/25)) ([`f79e5ea`](https://github.com/Toilal/rebulk/commit/f79e5eab0806787ff19a4c668bf9f88413b67288))
* **python:** Add python 3.10 support, drop python 3.5 support ([`a5e6eb7`](https://github.com/Toilal/rebulk/commit/a5e6eb7bba979ee51e1c6c1e186bd224c989dfdc))

## v3.0.1 (2020-12-25)
### Fix
* **package:** Fix broken package `No such file or directory: 'CHANGELOG.md'` ([#24](https://github.com/Toilal/rebulk/issues/24)) ([`33895ff`](https://github.com/Toilal/rebulk/commit/33895ff358ff5051768fb98d4e840691e7af9bdf))

### Documentation
* **readme:** Add semantic release badge ([`78baca0`](https://github.com/Toilal/rebulk/commit/78baca0c529083d7f583ffec58aeb23734d67ce5))
* **readme:** Fix title ([`d5d4db5`](https://github.com/Toilal/rebulk/commit/d5d4db5cd7f6e2cb1308acd26bfb98838815fad4))

## v3.0.0 (2020-12-23)
### Feature
* **regex:** Replace REGEX_DISABLED environment variable with REBULK_REGEX_ENABLED ([`d5a8cad`](https://github.com/Toilal/rebulk/commit/d5a8cad6281533ee549a46ca70e1a25e5777eda3))
* Add python 3.8/3.9 support, drop python 2.7/3.4 support ([`048a15f`](https://github.com/Toilal/rebulk/commit/048a15f90833ba8d33ea84d56e9955d31b514dc3))

### Breaking
* regex module is now disabled by default, even if it's available in the python interpreter. You have to set REBULK_REGEX_ENABLED=1 in your environment to enable it, as this module may cause some issues.  ([`d5a8cad`](https://github.com/Toilal/rebulk/commit/d5a8cad6281533ee549a46ca70e1a25e5777eda3))
* Python 2.7 and 3.4 support have been dropped  ([`048a15f`](https://github.com/Toilal/rebulk/commit/048a15f90833ba8d33ea84d56e9955d31b514dc3))
