# Windows Logged-On Users Web Tool

## What is it?

A tool to display logged on users on your Windows machines via the QUSER tool.

## Requirements

Windows host computer

An account with sufficient access to make RemoteRPC calls to the computers, as well as RemoteRPC enabled (default on servers, must be activated through Registry on clients)

## Setup

```pip install -r requirements.txt```

## Run
```
.\db_create.py
.\run.py
```

## Test
```
.\db_create.py
test.py -v tests.py
```