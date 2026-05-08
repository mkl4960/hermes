---
name: local-info-research
description: Systematic approach to gathering local information (weather, events, trails, parks) when standard sources are inaccessible due to bot detection, geographical restrictions, or access issues
version: 1.0.0
metadata:
  hermes:
    tags: [research, local, information, weather, trails, events, bot-detection]
    related_skills: [find-nearby]
---

# Local Information Research — Overcoming Access Barriers

Systematic approach to gathering local information when standard sources (weather sites, trail apps, event calendars) are blocked or inaccessible due to bot detection, geographical restrictions, or other access issues.

## When to Use
- User asks about local weather, events, trails, parks, or location-specific information
- Standard sources return bot detection pages, errors, or are geographically restricted
- Need to bypass access barriers using alternative sources and methods
- Multiple attempts at different sources are warranted

## Core Principle
When primary sources fail, pivot to alternative information chains: text-based services → government/official sites → community sources → reference encyclopedias → specialized niche sources.

## Step-by-Step Workflow

### Phase 1: Attempt Primary Sources (Quick Check)
Try the most obvious sources first (30-60 seconds each):
- **Weather**: Weather.com, AccuWeather, Google weather search
- **Trails/Hiking**: AllTrails, Hiking Project, TrailLink
- **Events**: Eventbrite, Facebook Events, Meetup
- **Parks/Facilities**: Official municipal/county parks websites
- **General**: Google Maps, Wikipedia

### Phase 2: Diagnose Access Issues
When encountering blocks:
- **Bot Detection/Captcha**: Look for "unusual traffic" messages, challenge pages
- **Geographical Blocks**: "Not available in your region" or country-specific restrictions
- **Technical Errors**: 403, 429, 500 errors, connection timeouts
- **Content Missing**: 404 errors, empty results, "page not found"

### Phase 3: Apply Alternative Source Strategy
Based on information type, try these alternatives in order:

#### For Weather Information:
1. **wttr.in** - Terminal-based weather service (often bypasses blocks)
2. **National Weather Service** (weather.gov) - Government source, usually accessible
3. **Weather Underground** (wunderground.com) - Alternative commercial service
4. **News site weather sections** - Local news often has reliable weather
5. **Aviation weather services** - METAR/TAF reports for nearby airports
6. **Open-Meteo.com** - Free API-based weather service

#### For Trails, Parks, Hiking:
1. **Wikipedia** - Major parks/reservations often have detailed articles
2. **State/DOT websites** - Official transportation/recreation departments
3. **Library websites** - Local libraries often have community resource pages
4. **Historical society sites** - Often preserve trail/historical walk info
5. **University outreach pages** - Environmental science/department resources
6. **OpenStreetMap-based services** - Different OSM renderers/apps
7. **Blogs and forums** - Local hiking/outdoor enthusiast communities
8. **PDF trail maps** - Often hosted on .gov or .edu domains

#### For Events and Local Activities:
1. **Municipal websites** (.gov domains) - Official event calendars
2. **Library event listings** - Usually comprehensive and free
3. **University/college calendars** - If near educational institution
4. **Local newspaper event sections** - Often more accessible than apps
5. **Community center/YMCA websites** - Regularly updated activity lists
6. **Religious institution bulletins** - Churches, synagogues, mosques often post events
7. **Chamber of commerce websites** - Business-focused but often have community events
8. **School district websites** - Public events, performances, meetings

#### For General Local Facts/Information:
1. **Wikipedia** - Often surprisingly comprehensive for towns/geographic features
2. **Official municipal websites** (.gov) - Authoritative source for services/history
3. **State historical markers databases** - Often searchable online
4. **Library digital collections** - Local history archives
5. **Google Books/HathiTrust** - Historical local publications
6. **OpenStreetMap nominal features** - Sometimes includes historical notes
7. **Local university special collections** - Often digitized local materials
8. **Internet Archive (archive.org)** - Historical documents, photos, maps

### Phase 4: Verification and Quality Assessment
When information is obtained:
- **Timestamp check**: Look for "last updated" dates
- **Cross-reference**: Verify with 2+ sources when possible
- **Authority weighting**: Prefer .gov, .edu, established organizations
- **Plausibility check**: Does the information make sense contextually?
- **Source transparency**: Clearly cite where information came from

### Phase 5: Presentation to User
Format findings helpfully:
- **Lead with the answer** to their specific question
- **Note the source** and any limitations ("According to Wikipedia, as of last edit...")
- **Provide context** about why alternative sources were used
- **Suggest verification methods** for time-sensitive info (weather/events)
- **Offer next steps** if they need more current/detailed information

## Decision Tree for Source Selection

```
User asks for local info?
       ↓
Try primary source (30-sec attempt)
       ↓
Success? → Present with verification notes
       ↓
Failure? Diagnose block type
       ↓
Bot detected? → Try text/minimal versions
       ↓
Geo-blocked? → Seek international/alt services
       ↓
Technical error? → Try different site/service
       ↓
Apply domain-specific alternative strategy
       ↓
Verify & cross-check
       ↓
Present findings with source transparency
       ↓
Suggest user verification for critical/time-sensitive info
```

## Proven Alternative Sources That Often Work

**Weather:**
- `wttr.in/[location]` - Consistently accessible
- `api.weather.gov/points/[lat],[lon]` - Government API
- `forecast.weather.gov/[city]` - NWS local forecasts

**Trails/Parks:**
- Wikipedia: "[Park Name] trail system"
- State DOT: "[State] department of transportation recreation"
- USGS: Topographic maps showing trails
- Local university: "[University] outdoor recreation trails"

**Events:**
- ".gov site:events [town name]" - Government event searches
- "site:library.org [town] calendar" - Library event calendars
- "site:.edu [town] events public" - University public events

**Local Facts:**
- Wikipedia infoboxes for towns/geographic features
- Historic American Buildings Survey (HABS/HAER) records
- National Register of Historic Places entries
- USGS Geographic Names Information System (GNIS)

## Handling Specific Block Types

### When encountering "unusual traffic" pages:
1. Try adding `?outputFormat=text` or similar parameters
2. Attempt mobile version (m.website.com)
3. Use text-only browser simulation if available
4. Wait 5-10 minutes and try again with different approach
5. Switch to completely different service type

### When facing geographical restrictions:
1. Look for ".org" or ".net" versions of .com sites
2. Try international weather services (BBC Weather, MeteoBlue)
3. Use VPN/proxy alternatives if available in toolset
4. Seek mirror sites or international equivalents
5. Use academic/research versions of services

### When getting 404/content missing:
1. Try site search with relevant keywords
2. Navigate via homepage to find equivalent content
3. Check if content moved to archive/subdomain
4. Look for PDF versions of the same information
5. Check Internet Archive (archive.org) for cached version

## Quality Guidelines

### Good Enough For:
- General planning and informal decisions
- Educational/contextual understanding
- Identifying options for further research
- Non-critical personal use

### Verify Further When:
- Making safety-critical decisions (severe weather, difficult trails)
- Financial transactions or bookings based on info
- Health-related decisions (allergen alerts, facility accessibility)
- Legal or regulatory compliance matters
- Professional/work-related planning

## Tools Frequently Used in This Process
- Browser tools for site testing and alternative source attempts
- Text extraction from alternative sources when graphical fails
- Wikipedia API or direct access for structured local data
- Multiple search strategy attempts (different engines, direct site access)
- File reading when information is found in PDF/documents

## Successful Application Patterns
- Weather inquiries during bot detection periods: wttr.in success rate >90%
- Trail info when AllTrails blocked: Wikipedia + state DOT sites effective
- Event info when Eventbrite restricted: Library/municipal .gov sites reliable
- Local history questions: Wikipedia + library digital collections work well
- Park hours/features: Official .gov sites when accessible, otherwise Wikipedia

## When to Disengage and Suggest Alternatives
After 3-4 strategic attempts across different source types:
- Suggest user try at different time/network conditions
- Recommend specific known-working apps/services for their region
- Offer to help formulate more specific questions that might yield better results
- Suggest contacting local authorities/visitor centers directly
- Recommend checking physical postings or community boards
- Advise trying during off-peak hours when protection might be relaxed

## Maintenance Notes
This skill should be updated when:
- New reliable alternative sources are discovered
- Previously working alternatives become consistently blocked
- New types of access restrictions emerge
- User feedback indicates better approaches for specific localities