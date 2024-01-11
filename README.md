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

The Pantos Client CLI requires **Python 3.10**. Ensure that you have the correct Python version installed before the installation steps. You can download the latest version of Python from the official [Python website](https://www.python.org/downloads/).

### 2.2  Installation Steps

#### Clone the repository

Clone the repository to your local machine:

```bash
$ git clone https://github.com/pantos-io/client-library.git
$ cd client-library
$ git submodule init
$ git submodule update --remote
```

#### Virtual environment

Create a virtual environment from the repository's root directory:

```bash
$ python -m venv .venv
```

Activate the virtual environment:

```bash
$ source .venv/bin/activate
```

Install the required packages:
```bash
$ python -m pip install -r requirements.txt
```

## 3. Usage

### 3.1 Configuration

The CLI comes with two configurations.

1. A configuration for the Pantos Client Library can be found in **pantos-client-library.conf**.
The library already has a set configuration for our testnet environment, but feel free to adapt it to your needs.

2. A configuration for the Pantos Client CLI can be found in **pantos-client-cli.conf**. Make sure to replace the keystore file path and the password with your private keystore.

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

At the moment, contributing to this project is not available. 
