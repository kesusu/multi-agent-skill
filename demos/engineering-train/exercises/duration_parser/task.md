# Duration Parser Exercise

Implement `parse_duration(text: str) -> int` in `duration_parser.py`.

Return the duration in seconds.

Supported inputs:

- Colon time:
  - `MM:SS`
  - `HH:MM:SS`
  - Whitespace around the full input is allowed.
- Unit time:
  - Units: `h`, `m`, `s`
  - Long forms: `hour`, `hours`, `minute`, `minutes`, `second`, `seconds`
  - Units may be separated by whitespace: `1h 30m`, `2 hours 5 seconds`
  - Units may be compact: `1h30m`, `2m10s`
  - Units may appear in any order, but duplicate units are invalid.
  - Whitespace around the full input is allowed.

Invalid input must raise `ValueError`.

Important edge cases:

- Empty input is invalid.
- Negative numbers are invalid.
- Decimal numbers are invalid.
- In colon format, minutes and seconds must be `0..59` when an hour field exists; seconds must be `0..59` in `MM:SS`.
- Plain numbers without units are invalid.
- Unknown units are invalid.

