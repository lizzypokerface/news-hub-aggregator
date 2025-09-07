from regions import Region


def categorize_headline_region(headline: str) -> str:
    # Define a dictionary where the keys are regions, and the values are lists of countries/regions associated with that region.
    regions = {
        "International": Region.INTERNATIONAL,
        "China": Region.CHINA_REGIONS,
        "South Asia": Region.SOUTH_ASIA_REGIONS,
        "Southeast Asia": Region.SOUTHEAST_ASIA_REGIONS,
        "East Asia": Region.EAST_ASIA_REGIONS,
        "Central Asia": Region.CENTRAL_ASIA_REGIONS,
        "West Asia (Middle East)": Region.WEST_ASIA_REGIONS,
        "Russia": Region.RUSSIA_REGIONS,
        "Europe": Region.EUROPE_REGIONS,
        "Africa": Region.AFRICA_REGIONS,
        "North America": Region.NORTH_AMERICA_REGIONS,
        "Latin America and The Caribbean": Region.LATIN_AMERICA_AND_CARIBEAN_REGIONS,
        "Oceania": Region.LATIN_AMERICA_AND_CARIBEAN_REGIONS,
        "Miscellaneous": [],
    }
    # Convert the headline to lowercase for case-insensitive matching
    headline_lower = headline.lower()
    # Loop through each region and its associated keywords
    for region, keywords in regions.items():
        for keyword in keywords:
            if keyword in headline_lower:
                return region
    # If no match is found, return 'Miscellaneous'
    return "Miscellaneous"
