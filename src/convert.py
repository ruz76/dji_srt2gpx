from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from pathlib import Path
import sys, os, math

class Convert(QThread):

    progressChanged = pyqtSignal(int)
    statusChanged = pyqtSignal(str)
    inputs = []
    reduce = True
    output_dir = ''

    def set_inputs(self, inputs):
        self.inputs = inputs

    def set_reduce(self, reduce):
        self.reduce = reduce

    def set_output_dir(self, output_dir):
        self.output_dir = output_dir

    def run(self):
        try:
            gpx_output = self.get_gpx_header('test name')
            csv_output = ''
            progress = 10
            self.progressChanged.emit(10)
            self.statusChanged.emit('Zahajuji konverzi')
            step = 90 / len(self.inputs)
            for file_name in self.inputs:
                outputs = self.get_outputs(file_name)
                csv_output += outputs[0]
                gpx_output += outputs[1]
                progress += step
                self.progressChanged.emit(round(progress))
                self.statusChanged.emit('Dokončen soubor ' + file_name)
            gpx_output += '</trk>\n'
            gpx_output += '</gpx>\n'
            with open(os.path.join(self.output_dir, 'track.gpx'), 'w') as gpx_o:
                gpx_o.write(gpx_output)
            with open(os.path.join(self.output_dir, 'track.csv'), 'w') as csv_o:
                csv_o.write(csv_output)
            self.progressChanged.emit(100)
            self.statusChanged.emit('Dokončen export do GPX a CSV')
        except Exception as e:
            print(e)
            self.statusChanged.emit('Export se nezdařil. Ověřte vstupní data.')

    def points_distance(self, lon1, lat1, lon2, lat2):
        lon1_float = float(lon1)
        lat1_float = float(lat1)
        lon2_float = float(lon2)
        lat2_float = float(lat2)
        return math.hypot(lon2_float - lon1_float, lat2_float - lat1_float)

    def get_gpx_header(self, name):
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

    def get_outputs(self, input):
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
                    if self.reduce and prev_lat != '':
                        distance = self.points_distance(prev_lon, prev_lat, lon, lat)
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


class Runner(QtWidgets.QDialog):
    window = None

    def __init__(self):
        super().__init__()
        with open('convert.ui', encoding="utf-8") as f:
            uic.loadUi(f, self)
        self.pushButtonConvert.clicked.connect(self.onConvertClick)
        self.pushButtonBrowseInputs.clicked.connect(self.onBrowseInputsClick)
        self.pushButtonBrowseOutput.clicked.connect(self.onBrowseOutputClick)
        self.inputs = []
        self.output_dir = ''

    def onConvertClick(self):
        self.convert = Convert()
        self.convert.progressChanged.connect(self.onProgressChanged)
        self.convert.statusChanged.connect(self.onStatusChanged)
        self.convert.set_inputs(self.inputs)
        self.convert.set_reduce(self.checkBoxReduce.isChecked())
        self.convert.set_output_dir(self.output_dir)
        self.convert.start()

    def onBrowseInputsClick(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("SRT (*.srt *.SRT)")
        if dialog.exec_():
            self.plainTextEdit.clear()
            self.inputs = []
            fileNames = dialog.selectedFiles()
            for fileName in fileNames:
                self.plainTextEdit.appendPlainText(fileName)
                self.inputs.append(fileName)

    def onBrowseOutputClick(self):
        dir_name = QFileDialog.getExistingDirectory(self, "Select a Directory")
        if dir_name:
            path = Path(dir_name)
            self.lineEdit.setText(str(path))
            self.output_dir = str(path)

    def onProgressChanged(self, value):
        self.progressBar.setValue(value)

    def onStatusChanged(self, value):
        self.labelStatus.setText(value)

def main():
    app = QtWidgets.QApplication([])
    window = Runner()
    window.show()
    return app.exec()

main()
