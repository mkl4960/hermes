# wttr.in vs Open-Meteo API Comparison for Weather Email Notifications

## wttr.in Issues Observed
- Frequent HTTP 500 Internal Server Errors when requesting JSON format
- Inconsistent availability across different location formats (city name, coordinates, etc.)
- Rate limiting or service interruptions affecting reliability
- Example error: `urllib.error.HTTPError: HTTP Error 500: Internal Server Error`

## Open-Meteo Advantages
- Consistent 200 OK responses for forecast requests
- Structured JSON response with clear data arrays
- No authentication required for basic forecasts
- Global coverage with high-resolution data
- Multiple weather parameters available (temperature, humidity, precipitation, weather codes, wind)
- Timezone support for local time display

## Implementation Changes Made
1. Switched from wttr.in to Open-Meteo API as primary source
2. Added weather code interpretation (WMO codes to descriptions)
3. Implemented unit conversion:
   - Celsius to Fahrenheit: (°C × 9/5) + 32
   - km/h to mph: km/h × 0.621371
   - Wind direction degrees to compass points
4. Limited forecast to today's hours only (first 24 entries)
5. Added graceful error handling for API failures

## Reliability Improvements
- Added retry mechanism with exponential backoff
- Graceful degradation when API fails (shows "Weather data unavailable")
- Continues sending emails even if one location fails
- Clear error logging to stderr for debugging

## Recommendations
1. Use Open-Meteo as primary weather source for Hermes weather email notifications
2. Keep wttr.in as fallback only if Open-Meteo fails (not implemented in this version)
3. Monitor API response times and adjust caching if needed
4. Consider API rate limits for high-frequency requests (Open-Meteo allows generous free tier)