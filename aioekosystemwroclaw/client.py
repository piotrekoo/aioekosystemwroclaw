"""Define a client to interact with Ekosystem Wrocław."""

import logging
import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional

from aiohttp import ClientSession
from aiohttp.client import ClientError, ClientTimeout

from .errors import DataError, RequestError

_LOGGER = logging.getLogger(__name__)

API_URL = "https://ekosystem.wroc.pl/wp-admin/admin-ajax.php"
DEFAULT_TIMEOUT = 10
WASTE_TYPES = {
    "BIO": "bio",
    "szkło": "glass",
    "zmieszane": "mixed",
    "papier": "paper",
    "tworzywa": "plastic",
}


@dataclass(frozen=True)
class PickupType:
    """Define a waste pickup type."""

    name: str
    friendly_name: Optional[str] = None


@dataclass(frozen=True)
class PickupEvent:
    """Define a waste pickup event."""

    date: date
    pickup_types: List[PickupType]

    def __lt__(self, other):
        """Compare objects by date."""
        return self.date < other.date


class Client:
    """Define a client."""

    def __init__(
        self,
        localization_id: int,
        street_id: int,
        *,
        session: ClientSession = None,
    ) -> None:
        """Initialize an object."""
        self._api_url = API_URL
        self._session = session
        self.localization_id = localization_id
        self.street_id = street_id

    async def _async_request(self, method: str, url: str, **kwargs) -> dict:
        """Make an API request."""
        use_running_session = self._session and not self._session.closed

        session: ClientSession = (
            self._session
            if use_running_session
            else ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))
        )

        try:
            async with session.request(method, url, **kwargs) as resp:
                data = await resp.json(content_type="text/html")
                resp.raise_for_status()
        except ClientError as error:
            raise RequestError(error)
        finally:
            if not use_running_session:
                await session.close()

        return data

    async def _async_get_pickup_data(self) -> dict:
        """Get pickup data."""
        url = self._api_url

        payload = {
            "action": "waste_disposal_form_get_schedule_direct",
            "id_numeru": self.localization_id,
            "id_ulicy": self.street_id,
        }

        return await self._async_request("post", url, data=payload)

    async def async_get_pickup_events(self) -> List[PickupEvent]:
        """Get pickup events."""
        pickup_data = await self._async_get_pickup_data()

        pickup_dates = set(
            re.findall(
                r"kiedy_\d*=(\d{4}-\d{2}-\d{2})", pickup_data["wiadomosc"]
            )
        )

        events = [
            PickupEvent(
                date.fromisoformat(pickup_date),
                [
                    PickupType(eko_type, WASTE_TYPES[eko_type])
                    for eko_type in re.findall(
                        r"kiedy_\d*={pickup_date}&co_\d*=(\w*)&".format(
                            pickup_date=pickup_date
                        ),
                        pickup_data["wiadomosc"],
                    )
                ],
            )
            for pickup_date in pickup_dates
        ]

        events.sort()
        return events

    async def async_get_next_pickup_event(
        self, omit_today=False
    ) -> PickupEvent:
        """Get the next pickup event."""
        pickup_events = await self.async_get_pickup_events()
        start_date = date.today() + timedelta(1) if omit_today else date.today()
        for event in pickup_events:
            if event.date >= start_date:
                return event
        raise DataError("No events found after today")
