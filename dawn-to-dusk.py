from datetime import date, timedelta
from astral import LocationInfo
from astral.sun import sun
from icalendar import Calendar, Event
import pytz


def dawn_to_dusk_ical(
    lat, lon, location_name, start_date, end_date, filename="dawn_to_dusk_ical.ics"
):
    # Setup location
    location = LocationInfo(
        name=location_name,
        region="USA",
        latitude=lat,
        longitude=lon,
        timezone="America/Los_Angeles",
    )
    tz = pytz.timezone(location.timezone)

    # Create calendar
    cal = Calendar()
    # cal.add('prodid', '-//SunriseSunset Calendar//example//')
    # cal.add('version', '2.0')

    current_date = start_date
    while current_date <= end_date:
        s = sun(location.observer, date=current_date, tzinfo=tz)

        # Sunrise event
        sunrise_event = Event()
        sunrise_event.add("summary", "☀️ Sunrise")
        sunrise_event.add("dtstart", s["sunrise"])
        sunrise_event.add("dtend", s["sunrise"] + timedelta(minutes=15))
        sunrise_event.add("dtstamp", date.today())
        sunrise_event.add("location", location_name)
        cal.add_component(sunrise_event)

        # Sunset event
        sunset_event = Event()
        sunset_event.add("summary", "🌙 Sunset")
        sunset_event.add("dtstart", s["sunset"])
        sunset_event.add("dtend", s["sunset"] + timedelta(minutes=15))
        sunset_event.add("dtstamp", date.today())
        sunset_event.add("location", location_name)
        cal.add_component(sunset_event)

        current_date += timedelta(days=1)

    # Write to file
    with open(filename, "wb") as f:
        f.write(cal.to_ical())


# Example usage:
if __name__ == "__main__":
    dawn_to_dusk_ical(
        lat=37.7749,
        lon=-122.4194,
        location_name="San Francisco",
        start_date=date(2025, 1, 1),
        end_date=date(2030, 12, 31),
    )
