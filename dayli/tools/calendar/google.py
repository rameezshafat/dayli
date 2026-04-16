from __future__ import annotations

import logging
import os

import httpx

from dayli.domain.models.schedule import ScheduleChangeSet
from dayli.tools.calendar.base import CalendarProvider

logger = logging.getLogger(__name__)

_TOKEN_URL = "https://oauth2.googleapis.com/token"
_CALENDAR_API = "https://www.googleapis.com/calendar/v3"


class GoogleCalendarProvider(CalendarProvider):
    """Google Calendar provider using stored OAuth2 refresh token."""

    def __init__(self, client_id: str = "", client_secret: str = "", refresh_token: str = "") -> None:
        self._client_id = client_id or os.environ.get("GOOGLE_CLIENT_ID", "")
        self._client_secret = client_secret or os.environ.get("GOOGLE_CLIENT_SECRET", "")
        self._refresh_token = refresh_token or os.environ.get("GOOGLE_REFRESH_TOKEN", "")

    async def _get_access_token(self) -> str:
        client_id = self._client_id
        client_secret = self._client_secret
        refresh_token = self._refresh_token

        if not all([client_id, client_secret, refresh_token]):
            raise RuntimeError(
                "Google Calendar not configured. "
                "Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN in .env — "
                "run 'python scripts/google_auth.py' to get your refresh token."
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                _TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )
            response.raise_for_status()
            return response.json()["access_token"]

    async def apply_changes(self, user_id: str, changes: ScheduleChangeSet) -> None:
        if changes.mode != "apply" or not changes.events:
            return

        access_token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            for event in changes.events:
                body = {
                    "summary": event.title,
                    "start": {"dateTime": event.start, "timeZone": "UTC"},
                    "end": {"dateTime": event.end, "timeZone": "UTC"},
                }
                response = await client.post(
                    f"{_CALENDAR_API}/calendars/primary/events",
                    headers=headers,
                    json=body,
                )
                response.raise_for_status()
                logger.info("Created Google Calendar event: %s", event.title)
