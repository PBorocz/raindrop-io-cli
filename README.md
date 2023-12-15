[![version](https://img.shields.io/badge/python-3.11+-green)](https://www.python.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![license](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/PBorocz/raindrop-io-py/blob/trunk/LICENSE)
|docs|

# Raindrop-IO-CLI

Simple terminal command-line interface to the [Raindrop.io](https://raindrop.io) Bookmark Manager.

## Background

I wanted to use an existing API for the Raindrop Bookmark Manager ([python-raindropio](https://github.com/atsuoishimoto/python-raindropio)) to perform some bulk operations through a simple command-line interface. However, the API available was incomplete and didn't contain any user-interface. Thus, I extended (and maintain) a _fork_ and significant extension of [python-raindropio](https://github.com/atsuoishimoto/python-raindropio) (ht [Atsuo Ishimoto](https://github.com/atsuoishimoto)).

This package is a proof-of-concept for this API that serves my needs to interact with Raindrop on an non-windowing basis.

## Requirements

Requires Python 3.10 or later (well, at least I'm developing against 3.11.3).

## Install

```shell
[.venv] python -m pip install raindrop-io-cli
```

## Setup

To use this package, besides your own account on [Raindrop](https://raindrop.io), you'll need to create an `integration app` on the Raindrop.io site from which you can create API token(s).

-   Go to [<https://app.draindrop.api/settings/integrations>](https://app.raindrop.io/settings/integrations) and select `+ create new app`.

-   Give it a descriptive name and then select the app you just created.

-   Select `Create test token` and copy the token provided. Note that the basis for calling it a _test_ token is that it only gives you access to bookmarks within *your own account*. Raindrop allows you to use their API against other people's environments using oAuth (see untested/unsupported `flask_oauth.py` file in /examples)

-   Save your token into your environment (we use python-dotenv so a simple .env/.envrc file containing your token should suffice), for example:

```shell
# If you use direnv or it's equivalent, place something like this in a .env file:
RAINDROP_TOKEN=01234567890-abcdefghf-aSample-API-Token-01234567890-abcdefghf

# Or for bash:
export RAINDROP_TOKEN=01234567890-abcdefghf-aSample-API-Token-01234567890-abcdefghf

# Or for fish:
set -gx RAINDROP_TOKEN 01234567890-abcdefghf-aSample-API-Token-01234567890-abcdefghf

# etc...
```

## Command-Line Interface Usage

```shell
[.venv] % raindropiocli/cli.py
```
Note: remember to setup `RAINDROP-TOKEN` in your environment!

## License

The project is licensed under the MIT License.

## Release History

### Unreleased

.. |docs| image:: https://readthedocs.org/projects/docs/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://docs.readthedocs.io/en/latest/?badge=latest
