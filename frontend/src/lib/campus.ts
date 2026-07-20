/** IIT Guwahati campus, North Guwahati, Assam — real OSM boundary (way
 * 52435139), fetched from the backend's /delivery-zone endpoint for the
 * authoritative polygon. These are just map-camera defaults: where to
 * center/fit the view before that polygon has loaded, and how far a picker
 * is allowed to pan away from campus. */
export const CAMPUS_CENTER = { lat: 26.1924788, lng: 91.6946357 };

export const CAMPUS_BOUNDS = {
  south: 26.1823597,
  west: 91.6860336,
  north: 26.2018409,
  east: 91.7042369,
};

/** Same bounds, padded, so a picker isn't clipped exactly at the campus
 * fence line — riders/customers near the edge still see some surrounding
 * context. */
export function paddedCampusBounds(paddingDegrees = 0.004) {
  return {
    south: CAMPUS_BOUNDS.south - paddingDegrees,
    west: CAMPUS_BOUNDS.west - paddingDegrees,
    north: CAMPUS_BOUNDS.north + paddingDegrees,
    east: CAMPUS_BOUNDS.east + paddingDegrees,
  };
}

export const CAMPUS_MAP_DEFAULT_ZOOM = 16;
