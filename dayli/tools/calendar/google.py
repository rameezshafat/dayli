from __future__ import annotations

import logging
import os

import httpx

from dayli.domain.models.schedule import ScheduleChangeSet, ScheduledEvent
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

    async def list_events(self, user_id: str) -> list[ScheduledEvent]:
        """Return today's calendar events with their Google Calendar event_id."""
        from datetime import datetime, timezone
        access_token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}

        now = datetime.now(timezone.utc)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        day_end   = now.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{_CALENDAR_API}/calendars/primary/events",
                headers=headers,
                params={
                    "timeMin": day_start,
                    "timeMax": day_end,
                    "singleEvents": "true",
                    "orderBy": "startTime",
                    "maxResults": "50",
                },
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])

        events = []
        for item in items:
            start_raw = item.get("start", {}).get("dateTime") or item.get("start", {}).get("date", "")
            end_raw   = item.get("end", {}).get("dateTime") or item.get("end", {}).get("date", "")
            events.append(ScheduledEvent(
                title=item.get("summary", "(no title)"),
                start=start_raw,
                end=end_raw,
                event_id=item["id"],
            ))
        return events

    async def delete_events(self, user_id: str, changes: ScheduleChangeSet) -> int:
        """Delete calendar events by event_id when available, otherwise fall back to title match."""
        if changes.mode != "apply":
            return 0

        access_token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        deleted = 0

        # Fast path: all events have explicit IDs (selected from list_events)
        events_with_ids = [e for e in changes.events if e.event_id]
        if events_with_ids:
            async with httpx.AsyncClient() as client:
                for event in events_with_ids:
                    del_resp = await client.delete(
                        f"{_CALENDAR_API}/calendars/primary/events/{event.event_id}",
                        headers=headers,
                    )
                    if del_resp.status_code in (200, 204):
                        deleted += 1
                        logger.info("Deleted Google Calendar event: %s", event.title)
            return deleted

        # Fallback: no IDs — list today's events and match by title (or delete all)
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        day_end   = now.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()

        titles_to_delete = {e.title.lower() for e in changes.events}

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{_CALENDAR_API}/calendars/primary/events",
                headers=headers,
                params={
                    "timeMin": day_start,
                    "timeMax": day_end,
                    "singleEvents": "true",
                    "maxResults": "50",
                },
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])

            for item in items:
                summary = item.get("summary", "").lower()
                if not titles_to_delete or summary in titles_to_delete:
                    del_resp = await client.delete(
                        f"{_CALENDAR_API}/calendars/primary/events/{item['id']}",
                        headers=headers,
                    )
                    if del_resp.status_code in (200, 204):
                        deleted += 1
                        logger.info("Deleted Google Calendar event: %s", item.get("summary"))

        return deleted

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
