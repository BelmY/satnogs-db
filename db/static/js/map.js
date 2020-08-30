/*global mapboxgl Sat_t gtk_sat_data_read_sat predict_calc julian_date Geodetic_t radians xkmper de2ra asin sin cos arccos degrees pio2 pi fabs */

$(document).ready(function() {
    'use strict';

    var name = $('div#map').data('name');
    var tle1 = $('div#map').data('tle1');
    var tle2 = $('div#map').data('tle2');
    var mapboxtoken = $('div#map').data('mapboxtoken');

    mapboxgl.accessToken = mapboxtoken;

    // Load satellite orbit data from TLE
    var sat = new Sat_t();
    gtk_sat_data_read_sat([name, tle1, tle2], sat);


    function get_orbits(sat) {
        // NOTE: This function has side effects (alters sat)!

        // Number of positions to compute
        var COUNT = 300;

        // Interval in ms between positions to compute
        var STEP = 60*1000;

        // Create satellite orbit
        var current_orbit = [];
        var all_orbits = [];

        var t = new Date();

        var previous = 0;
        for ( var i = 0; i < COUNT; i++) {
            predict_calc(sat, (0,0), julian_date(t));

            if (Math.abs(sat.ssplon - previous) > 180) {
                // orbit crossing -PI, PI
                all_orbits.push(current_orbit);
                current_orbit = [];
            }

            current_orbit.push([sat.ssplon, sat.ssplat]);
            previous = sat.ssplon;

            // Increase time for next point
            t.setTime(t.getTime() + STEP);
        }

        return all_orbits;
    }

    function get_range_circle(sat_ssplat, sat_ssplon, sat_footprint) {
        // NOTE: This function has side effects (alters sat)!

        var azi;
        // var msx, msy, ssx, ssy;
        var ssplat,
            ssplon,
            beta,
            azimuth,
            num,
            dem;
        // var rangelon, rangelat, mlon;

        var geo = new Geodetic_t();

        /* Range circle calculations.
         * Borrowed from gsat 0.9.0 by Xavier Crehueras, EB3CZS
         * who borrowed from John Magliacane, KD2BD.
         * Optimized by Alexandru Csete and William J Beksi.
         */
        ssplat = radians(sat_ssplat);
        ssplon = radians(sat_ssplon);
        beta = (0.5 * sat_footprint) / xkmper;

        var points = [];

        for (azi = 0; azi < 360; azi += 5) {
            azimuth = de2ra * azi;
            geo.lat = asin(sin(ssplat) * cos(beta) + cos(azimuth) * sin(beta)
                    * cos(ssplat));
            num = cos(beta) - (sin(ssplat) * sin(geo.lat));
            dem = cos(ssplat) * cos(geo.lat);

            if (azi == 0 && (beta > pio2 - ssplat)) {
                geo.lon = ssplon + pi;
            }
            else if (azi == 180 && (beta > pio2 + ssplat)) {
                geo.lon = ssplon + pi;
            }
            else if (fabs(num / dem) > 1.0) {
                geo.lon = ssplon;
            } else {
                if ((180 - azi) >= 0) {
                    geo.lon = ssplon - arccos(num, dem);
                } else {
                    geo.lon = ssplon + arccos(num, dem);
                }
            }

            points.push([degrees(geo.lon), degrees(geo.lat)]);
        }
        return points;
    }

    function get_location(sat) {
        // NOTE: This function has side effects (alters sat)!
        var now = new Date();
        predict_calc(sat, (0, 0), julian_date(now));

        return [sat.ssplon, sat.ssplat];
    }

    // Calculate orbits, footprint and current satellite location
    var sat_location = get_location(sat);
    var footprint = get_range_circle(sat.ssplat, sat.ssplon, sat.footprint);
    var all_orbits = get_orbits(sat);

    var map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/cshields/ckc1a24y45smb1ht9bbhrcrk6',
        zoom: 2,
        center: sat_location
    });

    map.addControl(new mapboxgl.NavigationControl());

    map.on('load', function () {

        map.loadImage('/static/img/satellite-marker.png', function(error, image) {
            map.addImage('sat_icon', image);
        });


        var location_data = {
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': sat_location
                }
            }]
        };

        map.addSource('sat_location', {
            'type': 'geojson',
            'data': location_data
        });

        map.addLayer({
            'id': 'sat_location',
            'type': 'symbol',
            'source': 'sat_location',
            'layout': {
                'icon-image': 'sat_icon',
                'icon-size': 0.4
            }
        });

        var orbit_data = {
            'type': 'FeatureCollection',
            'features': []
        };

        all_orbits.forEach(function(orbit){
            orbit_data.features.push({
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': orbit
                }
            });
        });

        map.addSource('sat_orbit', {
            'type': 'geojson',
            'data': orbit_data
        });

        map.addLayer({
            'id': 'sat_orbit',
            'type': 'line',
            'source': 'sat_orbit'
        });

        var footprint_data = {
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [footprint]
                }
            }]
        };

        map.addSource('sat_footprint', {
            'type': 'geojson',
            'data': footprint_data
        });

        map.addLayer({
            'id': 'sat_footprint',
            'type': 'fill',
            'source': 'sat_footprint',
            'paint': {
                'fill-opacity': 0.2
            }
        });

        function update_map() {
            // Recalculate footprint and current satellite location
            sat_location = get_location(sat);
            footprint = get_range_circle(sat.ssplat, sat.ssplon, sat.footprint);

            location_data.features[0].geometry.coordinates = sat_location;
            footprint_data.features[0].geometry.coordinates = [footprint];

            map.getSource('sat_location').setData(location_data);
            map.getSource('sat_footprint').setData(footprint_data);
        }
        setInterval(update_map, 5000);
    });

    // couldn't get this to work with shown.bs.tab, have to go with click
    // timeout is necessary for the first click for some reason
    document.getElementById('mapcontent-tab').addEventListener('click', function() {
        setTimeout( function() { map.resize();}, 200);
    });
    // for deep-linking of satellite tab anchors 
    $('#mapcontent-tab').on('shown.bs.tab', function() {
        setTimeout( function() { map.resize();}, 200);
    });
});
