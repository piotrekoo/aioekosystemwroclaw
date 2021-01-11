# aioekosystemwroclaw ♻️ A Python 3 library
`aioekosystemwroclaw` is a Python 3, asyncio-based library scrapping data off the Ekosystem Wrocław website. In the current version, it allows users to fetch the waste pickup schedule.

It's inspired by [aiorecollect](https://github.com/bachya/aiorecollect). Many thanks to @bachya!

## Installation
```sh
pip install aioekosystemwroclaw
```

## Usage

### Localization and Street IDs
To use `aioekosystemwroclaw`, you need to know your Localization ID and Street ID.

To obtain these, you need to open the schedule on the Ekosystem [website](https://ekosystem.wroc.pl/gospodarowanie-odpadami/harmonogram-wywozu-odpadow/) and select your street name and house number. You'll be presented with a URL. The Localization and Street IDs are embedded in it.

```
https://ekosystem.wroc.pl/gospodarowanie-odpadami/harmonogram-wywozu-odpadow/?lokalizacja=LOCALIZATION_ID&ulica=STREET_ID
```

### Example
```python
import asyncio

from aioekosystemwroclaw import Client


async def main() -> None:
    client = Client("LOCALIZATION_ID", "STREET_ID")

    # Get all pickup events:
    pickup_events = await client.async_get_pickup_events()

    # Get next pickup event:
    next_pickup_event = await client.async_get_next_pickup_event()

    # Get next pickup event, omit today:
    next_pickup_event = await client.async_get_next_pickup_event(omit_today=True)

asyncio.run(main())
```

### Objects

#### PickupEvent

The `PickupEvent` object is returned from the aforementioned calls. They have two properties:
* `date`: a `datetime.date` of the event
* `pickup_types`: a list of `PickupType` objects that will be happen on the date

#### PickupType

The `PickupType` object contains:
* `name`: an internal name of waste type
* `friendly_name`: a _friendly_, English name of waste type

### Connection pooling

You can pass an `aiohttp.ClientSession` object to the `aioekosystemwroclaw.Client` and the client will use it for all requests sent to the server. Otherwise, a new connection will be created with each request.