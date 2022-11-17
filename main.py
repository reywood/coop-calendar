import json
import logging
import os.path
import re
import sys
from datetime import date, datetime, timedelta

import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger("coop_cal")

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.calendarlist.readonly",
    "https://www.googleapis.com/auth/calendar.events.owned.readonly",
]

TOKEN_FILE_NAME = "token.json"
COOP_CALENDAR_ID = "ljqrvhbv2eomhf0klojo5aflog@group.calendar.google.com"
TIMEZONE = pytz.timezone("US/Pacific")


def main(year: int, month: int):
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    events = _get_coop_events(year, month)
    logger.info(events)


def _build_event_from_event_result(event_result):
    is_all_day_event = "date" in event_result["start"]

    if is_all_day_event:
        return {
            "summary": event_result["summary"],
            "start": _parse_iso_date(event_result["start"]["date"]),
            "end": _parse_iso_date(event_result["end"]["date"]),
            "isAllDay": True,
        }

    return {
        "summary": event_result["summary"],
        "start": _parse_iso_date(event_result["start"]["dateTime"]),
        "end": _parse_iso_date(event_result["end"]["dateTime"]),
        "isAllDay": False,
    }


def _get_calendar_service():
    logger.info("Getting calendar service")
    creds = _get_credentials()
    return build("calendar", "v3", credentials=creds)


def _list_calendars(service):
    logger.info("Listing calendars")
    calendars_result = service.calendarList().list().execute()
    logger.info(json.dumps(calendars_result, indent=4))


def _get_coop_events(year: int, month: int):
    logger.info("Getting events")
    try:
        service = _get_calendar_service()

        time_min = _get_iso_date_of_start_of_month(month, year)
        time_max = _get_iso_date_of_end_of_month(month, year)

        events_result = (
            service.events()
            .list(
                calendarId=COOP_CALENDAR_ID,
                timeMin=time_min,
                timeMax=time_max,
                # maxResults=100,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        # logger.info(json.dumps(events_result, indent=4))

        return [_build_event_from_event_result(e) for e in events_result["items"]]
    except HttpError as err:
        raise Exception(f"Failed to get events: {err}")


def _get_credentials():
    creds = _get_credentials_from_token_file()

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE_NAME, "w") as token:
            token.write(creds.to_json())
    return creds


def _get_credentials_from_token_file():
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    if not os.path.exists(TOKEN_FILE_NAME):
        return

    with open(TOKEN_FILE_NAME, "r", encoding="utf8") as f:
        token = json.loads(f.read())

    for required_scope in SCOPES:
        if required_scope not in token["scopes"]:
            return

    return Credentials.from_authorized_user_file(TOKEN_FILE_NAME, SCOPES)


def _get_start_of_month(year: int, month: int) -> datetime:
    return TIMEZONE.localize(
        datetime.combine(date(year, month, 1), datetime.min.time())
    )


def _get_end_of_month(year: int, month: int) -> datetime:
    first_day_of_month = _get_start_of_month(year, month)
    return (first_day_of_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)


def _get_iso_date_of_start_of_month(month: int, year: int) -> str:
    return _get_start_of_month(year, month).isoformat()


def _get_iso_date_of_end_of_month(month: int, year: int) -> str:
    return _get_end_of_month(year, month).isoformat()


def _parse_iso_date(iso_date):
    # ex: 2022-11-02T14:00:00-07:00
    datetime_pattern = r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})([+-]\d{2}:?\d{2})$"
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"

    datetime_match = re.match(datetime_pattern, iso_date)
    if not datetime_match:
        date_match = re.match(date_pattern, iso_date)

        if not date_match:
            raise ValueError(f"Invalid ISO date: {iso_date}")

        return datetime.strptime(iso_date, "%Y-%m-%d").date

    normalized_iso_date = (
        f"{datetime_match.groups()[0]}{datetime_match.groups()[1].replace(':', '')}"
    )

    return datetime.strptime(normalized_iso_date, "%Y-%m-%dT%H:%M:%S%z")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) != 3:
        logger.error(f"Usage: {sys.argv[0]} YEAR MONTH")
        sys.exit(1)

    year = int(sys.argv[1])
    month = int(sys.argv[2])

    main(year, month)
