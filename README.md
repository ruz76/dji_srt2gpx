# dji_srt2gpx

Allows to convert from DJI SRT subtitles track of the flight into GPX and CSV file

The GUI is in Czech language only for now. 

![GUI](gui.png?raw=true "GUI")

You can use command line python file import_dron_srt.py as well.

## Compile on Windows
Start OSGeo4W Shell

```bat
py3_env
pyinstaller --onefile convert.py --paths C:\OSGeo4W64\apps\Qt5\bin
```

If the compilation does not work, you may try to downgrade QT to 5.10.
