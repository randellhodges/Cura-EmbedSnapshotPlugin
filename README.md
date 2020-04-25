# EmbedSnapshotPlugin

### What it does:

Creates a PrusaSlicer like embeded snapshot/thumbnail.

### How do I work this thing?

A menu option, "Thumbnail Settings", will be added until the Extenions menu. You can chose the "Configure Thumbnail Settings" option to enable/disable.

Enabled: Turn on/off the plugin

Formats: A comman delimited list of formats for each thumbnail you want to embed in the gcode file. The [OctoPrint-PrusaSlicerThumbnails](https://github.com/jneilliii/OctoPrint-PrusaSlicerThumbnails) by [jneilliii](https://github.com/jneilliii) currently supports the last one specified.

Examples:
```16x16, 200x200;JPG;90, 300x300;PNG;-1```

This would embed 3 thumbnails.
1) A 16 by 16 PNG with default quality
2) A 200 by 200 JPG with a quality of 90
3) 3 300 by 300 PNG with default quality

Note: You probably want to use PNG. It supports transparency and the OctoPrint plugin, while works with a JPG is going to internally treat it like a PNG. Ultimately the browser will see the bytes and render whatever.

See [QImageWriter::supportedImageFormats](https://doc.qt.io/archives/qt-4.8/qimagewriter.html#supportedImageFormats) for more information.

### Limitations:

The snapshot functionality does not show the build plate and does not clip the model by the buildplate.  Meaning, if you took an object 20mm tall and offset the Z by -10mm, you might expect the snapshot/thumbnail to only show the top 10mm, however, you will see the entire model.

### TODO:

I would love to figure out a way to include part of the build plate like PrusaSlicer does and to also clip the image by the build plate. Pull Request are welcome!

I don't have a full understanding of Cura plugins and the `scene.gcode_dict` and build plates. There might some issues around that.

More testing. This was created quickly while looking at the plugins of [fieldOfView](https://github.com/fieldOfView) for help, as well as the source of [Cura](https://github.com/Ultimaker/Cura)
