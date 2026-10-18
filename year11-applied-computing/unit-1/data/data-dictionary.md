# Data dictionary — Victorian climate observations, 2025

Generated from the database schema. Do not edit by hand; regenerate with `docs.py`.

**Source and status.** This is a *synthetic* dataset built for teaching. Its structure mirrors the Bureau of Meteorology's daily observations, and each station's annual averages are calibrated to that station's published climate normals, so the figures are realistic. It is not a Bureau extract and must not be cited as one.

**Scale.** 4 regions, 6 stations, 2190 daily observations covering 1 January to 31 December 2025.

## `region`

| Column | Type | Key | Null | Validation | Meaning |
| --- | --- | --- | --- | --- | --- |
| `region_id` | INTEGER | PK | no | — | Surrogate primary key. |
| `region_name` | TEXT |  | no | unique | ABS-style statistical region. Unique. |
| `state` | TEXT |  | no | (length(state) BETWEEN 2 AND 3) | State or territory abbreviation. |

## `station`

| Column | Type | Key | Null | Validation | Meaning |
| --- | --- | --- | --- | --- | --- |
| `station_id` | INTEGER | PK | no | — | Bureau of Meteorology station number. Natural primary key. |
| `station_name` | TEXT |  | no | — | Site name as the Bureau publishes it. |
| `region_id` | INTEGER | FK → `region.region_id` | no | — | Foreign key to region. |
| `latitude` | REAL |  | no | (latitude  BETWEEN -44 AND -10) | Decimal degrees, negative south of the equator. |
| `longitude` | REAL |  | no | (longitude BETWEEN 112 AND 154) | Decimal degrees east. |
| `elevation_m` | REAL |  | no | — | Metres above sea level. |
| `opened` | TEXT |  | no | — | Date the site began recording (ISO 8601). |

## `observation`

| Column | Type | Key | Null | Validation | Meaning |
| --- | --- | --- | --- | --- | --- |
| `obs_id` | INTEGER | PK | no | — | Surrogate primary key. |
| `station_id` | INTEGER | FK → `station.station_id` | no | — | Foreign key to station. |
| `obs_date` | TEXT |  | no | — | Date of observation, ISO 8601 (YYYY-MM-DD). |
| `min_temp_c` | REAL |  | yes | (min_temp_c BETWEEN -15 AND 55) | Minimum air temperature, degrees Celsius. |
| `max_temp_c` | REAL |  | yes | (max_temp_c BETWEEN -15 AND 55) | Maximum air temperature, degrees Celsius. |
| `rainfall_mm` | REAL |  | yes | (rainfall_mm >= 0) | Rainfall in the 24 hours to 9am, millimetres. 0 means a dry day. |
| `humidity_9am` | INTEGER |  | yes | (humidity_9am BETWEEN 0 AND 100) | Relative humidity at 9am, whole per cent. |

## Relationships

```
region 1 ──< station 1 ──< observation
```

One region has many stations; one station has many observations. `observation` also carries a composite unique constraint on (`station_id`, `obs_date`) — a station records at most one observation per day.

## Referential integrity

SQLite does **not** enforce foreign keys unless you turn them on. Run `PRAGMA foreign_keys = ON;` at the start of every session, or orphan rows will insert silently.
