import sys, os, math


def get_gpx_header(name):
    gpx_header = '<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:wptx1="http://www.garmin.com/xmlschemas/WaypointExtension/v1" xmlns:gpxtrx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:trp="http://www.garmin.com/xmlschemas/TripExtensions/v1" xmlns:adv="http://www.garmin.com/xmlschemas/AdventuresExtensions/v1" xmlns:prs="http://www.garmin.com/xmlschemas/PressureExtension/v1" xmlns:tmd="http://www.garmin.com/xmlschemas/TripMetaDataExtensions/v1" xmlns:vptm="http://www.garmin.com/xmlschemas/ViaPointTransportationModeExtensions/v1" xmlns:ctx="http://www.garmin.com/xmlschemas/CreationTimeExtension/v1" xmlns:gpxacc="http://www.garmin.com/xmlschemas/AccelerationExtension/v1" xmlns:gpxpx="http://www.garmin.com/xmlschemas/PowerExtension/v1" xmlns:vidx1="http://www.garmin.com/xmlschemas/VideoExtension/v1" version="1.1" creator="DogTrace GPS" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/WaypointExtension/v1 http://www8.garmin.com/xmlschemas/WaypointExtensionv1.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www8.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/ActivityExtension/v1 http://www8.garmin.com/xmlschemas/ActivityExtensionv1.xsd http://www.garmin.com/xmlschemas/AdventuresExtensions/v1 http://www8.garmin.com/xmlschemas/AdventuresExtensionv1.xsd http://www.garmin.com/xmlschemas/PressureExtension/v1 http://www.garmin.com/xmlschemas/PressureExtensionv1.xsd http://www.garmin.com/xmlschemas/TripExtensions/v1 http://www.garmin.com/xmlschemas/TripExtensionsv1.xsd http://www.garmin.com/xmlschemas/TripMetaDataExtensions/v1 http://www.garmin.com/xmlschemas/TripMetaDataExtensionsv1.xsd http://www.garmin.com/xmlschemas/ViaPointTransportationModeExtensions/v1 http://www.garmin.com/xmlschemas/ViaPointTransportationModeExtensionsv1.xsd http://www.garmin.com/xmlschemas/CreationTimeExtension/v1 http://www.garmin.com/xmlschemas/CreationTimeExtensionsv1.xsd http://www.garmin.com/xmlschemas/AccelerationExtension/v1 http://www.garmin.com/xmlschemas/AccelerationExtensionv1.xsd http://www.garmin.com/xmlschemas/PowerExtension/v1 http://www.garmin.com/xmlschemas/PowerExtensionv1.xsd http://www.garmin.com/xmlschemas/VideoExtension/v1 http://www.garmin.com/xmlschemas/VideoExtensionv1.xsd">'
    gpx_header += '<metadata>'
    gpx_header += '<name>' + name + '</name>'
    gpx_header += '</metadata>'
    gpx_header += '<trk>'
    gpx_header += '<name>' + name + '</name>'
    gpx_header += '<extensions>'
    gpx_header += '<gpxx:TrackExtension>'
    gpx_header += '<gpxx:DisplayColor>Black</gpxx:DisplayColor>'
    gpx_header += '</gpxx:TrackExtension>'
    gpx_header += '</extensions>'
    return gpx_header


def points_distance(lon1, lat1, lon2, lat2):
    lon1_float = float(lon1)
    lat1_float = float(lat1)
    lon2_float = float(lon2)
    lat2_float = float(lat2)
    return math.hypot(lon2_float - lon1_float, lat2_float - lat1_float)


def get_outputs(input, reduce_points):
    with open(input) as f:
        lines = f.readlines()
        timest = ''
        lon = ''
        lat = ''
        csv_output = ''
        gpx_output = '<trkseg>'
        prev_lon = ''
        prev_lat = ''
        for line in lines:
            if len(line) > 10 and line[:4].isnumeric():
                timest = line.strip()[:23]
                lon = ''
                lat = ''
            if '[latitude' in line:
                # Find where latitude starts
                start_latitude = line.find('[latitude')
                ii = line[start_latitude:]
                items = ii.strip().split(']')
                # print(items)
                # print(items[0][11:])
                lat = items[0].split(':')[1].strip()
                lon = items[1].split(':')[1].strip()
                items2 = items[2].split('abs_alt: ')
                if len(items2) > 1:
                    ele = items2[1][:-1].strip()
                else:
                    items2 = items[2].split('altitude: ')
                    if len(items2) > 1:
                        ele = items2[1][:-1].strip()
                    else:
                        ele = "0.0"
            if len(lon) > 0:
                append_point = True
                if reduce_points == '1' and prev_lat != '':
                    distance = points_distance(prev_lon, prev_lat, lon, lat)
                    if distance < 0.00005:
                        append_point = False
                if append_point:
                    timestz = timest.replace(' ', 'T').replace(',', '.') + 'Z'
                    csv_output += timestz + ';' + lon + ';' + lat + ';' + ele + '\n'
                    gpx_output += '<trkpt lat="' + str(lat) + '" lon="' + str(lon) + '">\n'
                    gpx_output += '<ele>' + str(ele) + '</ele>\n'
                    gpx_output += '<time>' + timestz + '</time>\n'
                    gpx_output += '</trkpt>\n'
                    prev_lon = lon
                    prev_lat = lat
        gpx_output += '</trkseg>\n'
        return [csv_output, gpx_output]


def process_single_file(reduce_points='0'):
    gpx_output = get_gpx_header(sys.argv[1])
    outputs = get_outputs(sys.argv[1], reduce_points)
    gpx_output += outputs[1]
    gpx_output += '</trk>\n'
    gpx_output += '</gpx>\n'
    with open(sys.argv[1] + '.gpx', 'w') as gpx_o:
        gpx_o.write(gpx_output)
    with open(sys.argv[1] + '.csv', 'w') as csv_o:
        csv_o.write(outputs[0])

try:
    if len(sys.argv) < 2:
        print('You have to specify input SRT file.')
    else:
        if len(sys.argv) == 3:
            process_single_file(sys.argv[2])
        else:
            process_single_file()
except:
    print("Something went wrong. Check the input file.")
