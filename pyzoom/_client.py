from __future__ import annotations

import os
from typing import List

import attr
import shortuuid
from typing_extensions import Literal

from pyzoom._base import APIClientBase
from pyzoom import schemas


@attr.s
class MeetingsComponent:
    _client: APIClientBase = attr.ib(repr=False)
    timezone: str = attr.ib(default="UTC")

    def list_meetings(self) -> schemas.ZoomMeetingShortList:
        endpoint = "/users/me/meetings"
        return schemas.ZoomMeetingShortList(**self._client.get(endpoint).json())

    def get_meeting(self, meeting_id: int) -> schemas.ZoomMeeting:
        endpoint = f"/meetings/{meeting_id}"
        return schemas.ZoomMeeting(**self._client.get(endpoint).json())
    """
    LineNumber:49 can be without Conversion to dict. Which may give user 
    an advantage to pass dictionary while creating the meeting in parameter 'settings'.
    """
    def create_meeting(
        self,
        topic: str,
        *,
        start_time: str,
        duration_min: int,
        timezone: str = None,
        type_: int = 2,
        password: str = None,
        settings: schemas.ZoomMeetingSettings = None,
    ) -> schemas.ZoomMeeting:
        endpoint = f"/users/me/meetings"
        body = {
            "topic": topic,
            "type": type_,
            "start_time": start_time,
            "duration": duration_min,
            "timezone": timezone or self.timezone,
            "password": password or shortuuid.random(6),
            "settings": settings.dict()
            if settings
            else schemas.ZoomMeetingSettings.default_settings().dict(),
        }
        response = self._client.post(endpoint, body=body)
        return schemas.ZoomMeeting(**response.json())

    """
    UpdateMeeting Should be passed with same parameters as create_meeting but
    meeting_id is an additional requirement when we wish to modify the meeting.
    In the return from we get a StatusCode and empty dictionary.
    """

    def update_meeting(
        self,
        topic: str,
        *,
        start_time: str,
        duration_min: int,
        timezone: str = None,
        type_: int = 2,
        password: str = None,
        settings: schemas.ZoomMeetingSettings = None,
        meeting_id: int,
    ) -> schemas.ZoomMeeting:
        endpoint = f"/meetings/{meeting_id}"
        body = {
            "topic": topic,
            "type": type_,
            "start_time": start_time,
            "duration": duration_min,
            "timezone": timezone or self.timezone,
            "password": password or shortuuid.random(6),
            "settings": settings.dict() 
            if settings
            else schemas.ZoomMeetingSettings.default_settings().dict(),
        }
        response = self._client.patch(endpoint, body=body)
        return {}

    def delete_meeting(self, meeting_id: int) -> bool:
        endpoint = f"/meetings/{meeting_id}"
        r = self._client.delete(endpoint)
        return r.status_code == 204

    def list_meeting_registrants(
        self, meeting_id: int
    ) -> schemas.MeetingRegistrantsList:
        endpoint = f"/meetings/{meeting_id}/registrants"
        return schemas.MeetingRegistrantsList(**self._client.get_all_pages(endpoint))

    def update_meeting_registrant_status(
        self,
        meeting_id: int,
        *,
        action: Literal["approve", "cancel", "deny"],
        registrants: List[schemas.MeetingRegistrantShort],
    ):
        endpoint = f"/meetings/{meeting_id}/registrants/status"
        body = {
            "action": action,
            "registrants": [registrant.dict() for registrant in registrants],
        }
        return self._client.put(endpoint, body=body)

    def add_meeting_registrant(
        self, meeting_id: int, *, first_name: str, last_name: str, email: str, **kwargs
    ) -> schemas.RegistrantConfirmation:
        endpoint = f"/meetings/{meeting_id}/registrants"
        registrant = schemas.MeetingRegistrant(
            first_name=first_name, last_name=last_name, email=email, **kwargs
        )
        return schemas.RegistrantConfirmation(
            **self._client.post(endpoint, body=registrant.dict()).json()
        )

    def add_and_confirm_registrant(
        self, meeting_id: int, *, first_name: str, last_name: str, email: str, **kwargs
    ) -> schemas.RegistrantConfirmation:
        confirmation = self.add_meeting_registrant(
            meeting_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            **kwargs,
        )
        self.update_meeting_registrant_status(
            meeting_id,
            action="approve",
            registrants=[
                schemas.MeetingRegistrantShort(
                    id=confirmation.registrant_id, email=email
                )
            ],
        )
        return confirmation

    def cancel_registration(self, meeting_id: int, *, registrant_id: str, email: str):
        self.update_meeting_registrant_status(
            meeting_id,
            action="cancel",
            registrants=[schemas.MeetingRegistrantShort(id=registrant_id, email=email)],
        )

    def approve_registration(self, meeting_id: int, *, registrant_id: str, email: str):
        self.update_meeting_registrant_status(
            meeting_id,
            action="approve",
            registrants=[schemas.MeetingRegistrantShort(id=registrant_id, email=email)],
        )

    def past_meeting_participants(
        self, meeting_id: int
    ) -> schemas.MeetingParticipantList:
        endpoint = f"/past_meetings/{meeting_id}/participants"
        return schemas.MeetingParticipantList(**self._client.get_all_pages(endpoint))

@attr.s
class UsersComponent:
    _client: APIClientBase = attr.ib(repr=False)

    def get_users(
        self, status: str
    ) -> schemas.ZoomUserList:
        endpoint = f"/users"
        query={
                "status": status,
        }
        return schemas.ZoomUserList(**self._client.get_all_pages(endpoint, query))

    def delete_user(self, user_id: int, ) -> bool:
        endpoint = f"/users/{user_id}"
        query={
            "action": "delete"
        }
        r = self._client.delete(endpoint, query)
        return r.status_code == 204

@attr.s(auto_attribs=True)
class ZoomClient:
    api_key: str = attr.ib(repr=False)
    api_secret: str = attr.ib(repr=False)
    base_url: str = attr.ib(repr=False, default="https://api.zoom.us/v2")

    raw: APIClientBase = attr.ib(init=False, repr=False)
    meetings: MeetingsComponent = attr.ib(init=False, repr=False)
    users: UsersComponent = attr.ib(init=False, repr=False)

    def __attrs_post_init__(self):
        self.raw: APIClientBase = APIClientBase(
            api_key=self.api_key, api_secret=self.api_secret, base_url=self.base_url
        )
        self.meetings: MeetingsComponent = MeetingsComponent(self.raw)
        self.users: UsersComponent = UsersComponent(self.raw)

    @classmethod
    def from_environment(cls) -> ZoomClient:
        env = os.environ
        return cls(api_key=env["ZOOM_API_KEY"], api_secret=env["ZOOM_API_SECRET"])

    def set_timezone(self, timezone: str):
        self.meetings.timezone = timezone
