![Zoom Logo](./ZoomLogo.png)

# Python wrapper for Zoom API
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyzoom)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI](https://img.shields.io/pypi/v/pyzoom)](https://pypi.org/project/pyzoom/)

This library is work in progress, and that includes documentation. Not all of the implemented methods are documented here,
so please explore the `ZoomClient` class.

Links:
* [Api Reference](https://marketplace.zoom.us/docs/api-reference)
* [Using Zoom API](https://marketplace.zoom.us/docs/api-reference/using-zoom-apis)

## Installation

`pip install -U pyzoom`


## Usage

### Basic instantiation:

```python
from pyzoom import ZoomClient

client = ZoomClient('YOUR_ZOOM_API_KEY', 'YOUR_ZOOM_API_SECRET')
```

### Instantiation from environment variables

You can also create an instance of client when storing your key and secret in environment variables `ZOOM_API_KEY` 
and `ZOOM_API_SECRET`.

```python
from pyzoom import ZoomClient

client = ZoomClient.from_environment()
```


### Meetings

#### Create meeting and add registrant
```python
from pyzoom import ZoomClient
from datetime import datetime as dt

client = ZoomClient.from_environment()

# Creating a meeting
meeting = client.meetings.create_meeting('Auto created 1', start_time=dt.now().isoformat(), duration_min=60, password='not-secure')


# Adding registrants
client.meetings.add_meeting_registrant(meeting.id, first_name='John', last_name='Doe', email='john.doe@example.com')
```
You can use `client.meetings.add_and_confirm_registrant` to also confirm auto added
registrants to a closed meeting.

#### Raw API methods

You can also use the library for making raw requests to the API:

```python
from pyzoom import ZoomClient

client = ZoomClient.from_environment()

# Get self
response = client.raw.get('/me')

# Get all pages of meeting participants
result_dict = client.raw.get_all_pages('/past_meetings/{meetingUUID}/participants')
```

### Disclaimer
This library is not related to Zoom Video Communications, Inc. It's an open-source project that 
aims to simplify working with this suddenly very popular service.
