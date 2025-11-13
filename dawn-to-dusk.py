from datetime import date, timedelta, datetime
from astral import LocationInfo
from astral.sun import sun
from icalendar import Calendar, Event
import pytz


def dawn_to_dusk_ical(
    lat,
    lon,
    location_name,
    start_date,
    end_date,
    date_in_file_name=False,
    filename="dawn_to_dusk_ical.ics",
):
    if date_in_file_name:
        date_range = f"{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}"
        if filename.endswith(".ics"):
            filename = filename.replace(".ics", f"_{date_range}.ics")
        else:
            filename = f"{filename}_{date_range}.ics"

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

    current_date = start_date
    while current_date <= end_date:
        s = sun(location.observer, date=current_date, tzinfo=tz)
        dawn = s["dawn"]
        sunrise = s["sunrise"]
        sunset = s["sunset"]
        dusk = s["dusk"]

        # Sunrise event (dawn → sunrise)
        sunrise_event = Event()
        sunrise_event.add("summary", f"☀️ Sunrise at {sunrise.strftime('%H:%M')}")
        sunrise_event.add("dtstart", dawn)
        sunrise_event.add("dtend", sunrise)
        sunrise_event.add("dtstamp", datetime.now(tz))
        sunrise_event.add("location", location_name)
        cal.add_component(sunrise_event)

        # Sunset event (sunset → dusk)
        sunset_event = Event()
        sunset_event.add("summary", f"🌙 Sunset at {sunset.strftime('%H:%M')}")
        sunset_event.add("dtstart", sunset)
        sunset_event.add("dtend", dusk)
        sunset_event.add("dtstamp", datetime.now(tz))
        sunset_event.add("location", location_name)
        cal.add_component(sunset_event)

        current_date += timedelta(days=1)

    # Add daylight saving transitions
    year = start_date.year
    while year <= end_date.year:
        # U.S. daylight saving: starts 2nd Sunday in March, ends 1st Sunday in November
        # Find 2nd Sunday in March
        march = date(year, 3, 1)
        second_sunday_march = march + timedelta(days=(6 - march.weekday()) % 7 + 7)

        # Find 1st Sunday in November
        november = date(year, 11, 1)
        first_sunday_november = november + timedelta(days=(6 - november.weekday()) % 7)

        # Add DST Start (Spring Forward)
        if start_date <= second_sunday_march <= end_date:
            dst_start = Event()
            dst_start.add("summary", "⏰ Daylight Saving Time Begins")
            dst_start.add("dtstart", second_sunday_march)
            dst_start.add("dtend", second_sunday_march + timedelta(days=1))
            dst_start.add("dtstamp", datetime.now(tz))
            dst_start.add("transp", "TRANSPARENT")
            dst_start.add("description", "Clocks spring forward 1 hour.")
            dst_start.add("location", location_name)
            dst_start["dtstart"].params["VALUE"] = "DATE"
            dst_start["dtend"].params["VALUE"] = "DATE"
            cal.add_component(dst_start)

        # Add DST End (Fall Back)
        if start_date <= first_sunday_november <= end_date:
            dst_end = Event()
            dst_end.add("summary", "⏰ Daylight Saving Time Ends")
            dst_end.add("dtstart", first_sunday_november)
            dst_end.add("dtend", first_sunday_november + timedelta(days=1))
            dst_end.add("dtstamp", datetime.now(tz))
            dst_end.add("transp", "TRANSPARENT")
            dst_end.add("description", "Clocks fall back 1 hour.")
            dst_end.add("location", location_name)
            dst_end["dtstart"].params["VALUE"] = "DATE"
            dst_end["dtend"].params["VALUE"] = "DATE"
            cal.add_component(dst_end)

        year += 1

    # Write to file
    with open(filename, "wb") as f:
        f.write(cal.to_ical())


# Example usage
if __name__ == "__main__":
    dawn_to_dusk_ical(
        lat=37.7749,
        lon=-122.4194,
        location_name="San Francisco",
        start_date=date(2025, 7, 1),
        end_date=date(2026, 12, 31),
        date_in_file_name=False,
    )
