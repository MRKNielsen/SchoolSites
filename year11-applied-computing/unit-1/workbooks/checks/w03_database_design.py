"""Workbook 03 - database design. Matches decks T10 and T11.
The student builds a database; SchemaCheck inspects its structure."""
import os
from contract import SchemaCheck

def build():
    return {
        # Progressive: each check adds one requirement to the one before it,
        # so the feedback always names the next thing to fix and nothing else.
        "3.1": SchemaCheck("3.1",
            tables=["region", "station", "observation"],
            naming=False,
            hint="Three tables. One for each kind of thing the data describes."),
        "3.2": SchemaCheck("3.2",
            tables=["region", "station", "observation"],
            primary_keys={"region": "region_id", "station": "station_id", "observation": "obs_id"},
            hint="Every table needs a primary key that is unique and never empty, "
                 "and every table and column name is lower_snake_case."),
        "3.3": SchemaCheck("3.3",
            tables=["region", "station", "observation"],
            primary_keys={"region": "region_id", "station": "station_id", "observation": "obs_id"},
            foreign_keys=[("station", "region_id", "region"),
                          ("observation", "station_id", "station")],
            hint="The foreign key lives on the many side: a station names its region, "
                 "an observation names its station."),
    }
