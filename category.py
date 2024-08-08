#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 14:51:30 2024

@author: hu_xk
"""

def place_category(osm_type, osm_class):
    """
    Determine the category of place based on OSM type and class.

    Parameters:
    osm_type (str): The type of the OSM object.
    osm_class (str): The class of the OSM object.

    Returns:
    str: The determined place category.
    """
    admin_units = [
        "administrative", "admin units", "locality", "town", "sea", "village",
        "hamlet", "continent", "county", "islet", "ocean", "archipelago",
        "region", "city", "island"
    ]

    suburbs = ["neighbourhood", "suburb", "quarter"]

    traffic_ways = [
        "bridge", "station", "traffic", "train_station", "highway", "bridge",
        "railway", "aeroway", "junction", "tunnel"
    ]

    natural_features = [
        "river", "nature", "stream", "nature_reserve", "waterway", "natural"
    ]

    houses = ["house", "building"]

    pois = [
        "park", "POI", "aerodrome", "square", "marketplace", "pumping_rig",
        "place_of_worship", "golf_course", "stadium", "school", "nightclub",
        "office", "building", "shop", "club", "tourism", "leisure", "military",
        "man_made", "healthcare", "historic", "amenity", "landuse"
    ]

    if osm_type in admin_units or osm_class == 'boundary':
        return 'admin unit'
    elif osm_type in suburbs:
        return 'suburb'
    elif osm_type in traffic_ways or osm_class in traffic_ways:
        return 'traffic way'
    elif osm_type in natural_features or osm_class in natural_features:
        return 'natural feature'
    elif osm_type in houses or osm_class in houses:
        return 'house'
    elif osm_type in pois or osm_class in pois:
        return 'POI'
    elif osm_type == "none":
        return 'unknown'
    else:
        return 'others'

# Example usage
if __name__ == "__main__":
    print(place_category("town", "boundary"))  # Output: admin unit
    print(place_category("suburb", ""))        # Output: suburb
    print(place_category("river", "waterway")) # Output: natural feature
    print(place_category("house", "building")) # Output: house
    print(place_category("none", ""))          # Output: unknown
    print(place_category("unknown", "unknown"))# Output: others
