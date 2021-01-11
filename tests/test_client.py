"""Tests for aioekosystemwroclaw client."""
from datetime import date

import pytest
from aiohttp.client import ClientSession
from freezegun import freeze_time

from aioekosystemwroclaw.client import Client, PickupType
from aioekosystemwroclaw.errors import DataError, RequestError
from tests.common import TEST_LOCALIZATION_ID, TEST_STREET_ID, load_fixture


@pytest.mark.asyncio
async def test_create_client():
    """Create a client and verify its attributes."""
    client = Client(TEST_LOCALIZATION_ID, TEST_STREET_ID)

    assert client.localization_id == TEST_LOCALIZATION_ID
    assert client.street_id == TEST_STREET_ID


@pytest.mark.asyncio
async def test_async_get_pickup_events(aresponses):
    """Test getting pickup events."""
    response = aresponses.Response(
        text=load_fixture("pickup_data_response_1.json"),
        status=200,
        headers={"Content-Type": "text/html"},
    )
    aresponses.add(
        "ekosystem.wroc.pl",
        "/wp-admin/admin-ajax.php",
        "post",
        response,
    )

    async with ClientSession() as session:
        client = Client(TEST_LOCALIZATION_ID, TEST_STREET_ID, session=session)
        pickup_events = await client.async_get_pickup_events()

        assert len(pickup_events) == 36


@pytest.mark.asyncio
async def test_async_request_error(aresponses):
    """Test that checks if a RequestError is returned on an HTTP error."""
    response = aresponses.Response(text=None, status=400)
    aresponses.add(
        "ekosystem.wroc.pl",
        "/wp-admin/admin-ajax.php",
        "post",
        response,
    )

    async with ClientSession() as session:
        with pytest.raises(RequestError):
            client = Client(
                TEST_LOCALIZATION_ID, TEST_STREET_ID, session=session
            )
            await client.async_get_pickup_events()


@freeze_time("2021-01-11")
@pytest.mark.asyncio
async def test_async_get_next_pickup_event(aresponses):
    """Test getting the next pickup event. No event on this day."""
    response = aresponses.Response(
        text=load_fixture("pickup_data_response_1.json"),
        status=200,
        headers={"Content-Type": "text/html"},
    )
    aresponses.add(
        "ekosystem.wroc.pl",
        "/wp-admin/admin-ajax.php",
        "post",
        response,
    )

    async with ClientSession() as session:
        client = Client(TEST_LOCALIZATION_ID, TEST_STREET_ID, session=session)
        next_pickup_event = await client.async_get_next_pickup_event()

        assert next_pickup_event.date == date(2021, 1, 12)
        assert next_pickup_event.pickup_types == [
            PickupType("papier", "paper"),
            PickupType("tworzywa", "plastic"),
            PickupType("zmieszane", "mixed"),
        ]


@freeze_time("2021-01-12")
@pytest.mark.asyncio
async def test_async_get_next_pickup_event_omit_today(aresponses):
    """Test getting the next pickup event. Omit today's event. Useful for single-family home owners."""
    response = aresponses.Response(
        text=load_fixture("pickup_data_response_1.json"),
        status=200,
        headers={"Content-Type": "text/html"},
    )
    aresponses.add(
        "ekosystem.wroc.pl",
        "/wp-admin/admin-ajax.php",
        "post",
        response,
    )

    async with ClientSession() as session:
        client = Client(TEST_LOCALIZATION_ID, TEST_STREET_ID, session=session)
        next_pickup_event = await client.async_get_next_pickup_event(
            omit_today=True
        )

        assert next_pickup_event.date == date(2021, 1, 13)
        assert next_pickup_event.pickup_types == [
            PickupType("zmieszane", "mixed"),
        ]


@freeze_time("2021-03-15")
@pytest.mark.asyncio
async def test_async_get_next_pickup_event_no_event_left(aresponses):
    """Test getting the next pickup event. No event after today."""
    response = aresponses.Response(
        text=load_fixture("pickup_data_response_1.json"),
        status=200,
        headers={"Content-Type": "text/html"},
    )
    aresponses.add(
        "ekosystem.wroc.pl",
        "/wp-admin/admin-ajax.php",
        "post",
        response,
    )

    async with ClientSession() as session:
        client = Client(TEST_LOCALIZATION_ID, TEST_STREET_ID, session=session)
        with pytest.raises(DataError):
            await client.async_get_next_pickup_event()


@freeze_time("2021-01-11")
@pytest.mark.asyncio
async def test_async_get_next_pickup_event_makesession(aresponses):
    """Test getting the next pickup event. No event on this day. No session passed."""
    response = aresponses.Response(
        text=load_fixture("pickup_data_response_1.json"),
        status=200,
        headers={"Content-Type": "text/html"},
    )
    aresponses.add(
        "ekosystem.wroc.pl",
        "/wp-admin/admin-ajax.php",
        "post",
        response,
    )

    client = Client(TEST_LOCALIZATION_ID, TEST_STREET_ID)
    next_pickup_event = await client.async_get_next_pickup_event()

    assert next_pickup_event.date == date(2021, 1, 12)
    assert next_pickup_event.pickup_types == [
        PickupType("papier", "paper"),
        PickupType("tworzywa", "plastic"),
        PickupType("zmieszane", "mixed"),
    ]
