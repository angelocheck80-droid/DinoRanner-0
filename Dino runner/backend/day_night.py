from datetime import datetime


MAX_NIGHT_OPACITY = 1500
DAWN_START_HOUR = 5
DAY_START_HOUR = 8
DUSK_START_HOUR = 16
NIGHT_START_HOUR = 19


def night_opacity(now=None):
    """Return the blue night overlay opacity for local time, from 0 to 150."""
    if now is None:
        now = datetime.now().astimezone()

    hour = now.hour + now.minute / 60 + now.second / 3600
    if hour < DAWN_START_HOUR or hour >= NIGHT_START_HOUR:
        return MAX_NIGHT_OPACITY
    if hour < DAY_START_HOUR:
        progress = (hour - DAWN_START_HOUR) / (
            DAY_START_HOUR - DAWN_START_HOUR
        )
        return round(MAX_NIGHT_OPACITY * (1 - _smoothstep(progress)))
    if hour < DUSK_START_HOUR:
        return 0

    progress = (hour - DUSK_START_HOUR) / (NIGHT_START_HOUR - DUSK_START_HOUR)
    return round(MAX_NIGHT_OPACITY * _smoothstep(progress))


def twilight_glow_strength(now=None):
    if now is None:
        now = datetime.now().astimezone()

    hour = now.hour + now.minute / 60 + now.second / 3600
    if DUSK_START_HOUR <= hour < NIGHT_START_HOUR:
        progress = (hour - DUSK_START_HOUR) / (
            NIGHT_START_HOUR - DUSK_START_HOUR
        )
        return _smoothstep(progress)
    if NIGHT_START_HOUR <= hour < 21:
        progress = (hour - NIGHT_START_HOUR) / 2
        return 1 - _smoothstep(progress)
    if 4 <= hour < DAWN_START_HOUR:
        return _smoothstep(hour - 4)
    if DAWN_START_HOUR <= hour < DAY_START_HOUR:
        progress = (hour - DAWN_START_HOUR) / (
            DAY_START_HOUR - DAWN_START_HOUR
        )
        return 1 - _smoothstep(progress)
    return 0


def night_gradient_strength(now=None):
    return night_opacity(now) / MAX_NIGHT_OPACITY


def _smoothstep(progress):
    progress = max(0, min(1, progress))
    return progress * progress * (3 - 2 * progress)
