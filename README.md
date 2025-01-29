<img src="https://raw.githubusercontent.com/pantos-io/client-cli/img/pantos-logo-full.svg" alt="Pantos logo" align="right" width="120" />

[![CI](https://github.com/pantos-io/client-cli/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/pantos-io/client-cli/actions/workflows/ci.yaml) 
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=pantos-io_client-cli2&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=pantos-io_client-cli2)



# Pantos Client CLI

## 1. Introduction

### 1.1 Overview

Welcome to the documentation for Pantos Client CLI, a powerful tool for engaging with the Pantos system. This documentation aims to provide developers with comprehensive information on how to use the features the CLI offers.

### 1.2 Features

The Pantos Client CLI offers the following functionalities:

1. Retrieve the balance of a token
2. Retrieve the service node bids
3. Transfer tokens

## 2. Installation

### 2.1  Prerequisites

Please make sure that your environment meets the following requirements:

#### Keystore File (Wallet)

The CLI requires a private key encrypted with a password.

Since, for the moment, the Pantos protocol supports only EVM blockchains, only an Ethereum account keystore file is sufficient. It can be created with tools such as https://vanity-eth.tk/.

One of the most significant advantages of using Pantos is that the protocol has been designed to require minimal user friction when cross-chain operations are performed. Therefore, when using the Pantos products, you must top up your wallet only with PAN tokens.

#### Python Version

The Pantos Client CLI supports **Python 3.10** or higher. Ensure that you have the correct Python version installed before the installation steps. You can download the latest version of Python from the official [Python website](https://www.python.org/downloads/).

#### Library Versions

The Pantos Client CLI has been tested with the library versions specified in **poetry.lock**.

#### Poetry

Poetry is our tool of choice for dependency management and packaging.

Installing: 
https://python-poetry.org/docs/#installing-with-the-official-installer
or
https://python-poetry.org/docs/#installing-with-pipx

By default poetry creates the venv directory under ```{cache-dir}/virtualenvs```. If you opt for creating the virtualenv inside the project’s root directory, execute the following command:

```bash
poetry config virtualenvs.in-project true
```

### 2.2  Installation Steps

#### Clone the repository

Clone the repository to your local machine:

```bash
$ git clone https://github.com/pantos-io/client-cli.git
$ cd client-cli
$ virtualenv env
$ source env/bin/activate
$ pip install poetry
```

#### Libraries

Create the virtual environment and install the dependencies:

```bash
$ poetry install --no-root
```

## 3. Usage

### 3.1 Configuration

The CLI comes with two configurations.

1. A configuration for the Pantos Client Library can be found in **client-library.yml**.
The library already has a set configuration for our testnet environment, but feel free to adapt it to your needs.

2. A configuration for the Pantos Client CLI can be found in **client-cli.yml**. Make sure to replace the keystore file path and the password with your private keystore.

### 3.2 Examples

The Pantos Client CLI can be used by executing the **pantos-client.sh** bash script.

```bash
$ pantos-client [-h] {balance,bids,transfer} ...

positional arguments:
  {balance,bids,transfer}
    balance             show the balance of your accounts
    bids                list the available service node bids
    transfer            transfer tokens to another account (possibly on another blockchain)
```

## 4. Contributing

Check the [code of conduct](CODE_OF_CONDUCT.md).
