# I used code from fieldOfView (https://github.com/fieldOfView) as a guide for plugin development as well as
# source from Cura (https://github.com/Ultimaker/Cura)

# This plugin would not be possible without their work.

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QImage

from UM.Extension import Extension
from UM.Logger import Logger

from cura.CuraApplication import CuraApplication
from cura.Snapshot import Snapshot

from UM.i18n import i18nCatalog

import os.path

catalog = i18nCatalog("embed_snapshot")

class EmbedSnapshotPlugin(Extension):

    def __init__(self) -> None:
        super().__init__()

        self._application = CuraApplication.getInstance()
        self._application.getOutputDeviceManager().writeStarted.connect(self._filterGcode)

        self._settings_dialog = None

        self.setMenuName(catalog.i18nc("@item:inmenu", "Thumbnail Settings"))
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Configure Thumbnail Settings"), self._showSettingsDialog)

        self._application.getPreferences().addPreference("embed_snapshot/enabled", False)
        self._application.getPreferences().addPreference("embed_snapshot/formats", "220x124;PNG;-1")

    def _showSettingsDialog(self):

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qml", "SettingsDialog.qml")

        self._settings_dialog = self._application.createQmlComponent(path, {"manager": self})
        self._settings_dialog.show()

    def _get_snapshot_image(self, width, height) -> QImage:

        # must be called from the main thread because of OpenGL
        try:
            return Snapshot.snapshot(width = width, height = height)
        except Exception:
            Logger.logException("w", "Failed to create snapshot image")

        return None

    def _get_snapshot_base64(self, data, image_width, image_height, image_format = "PNG", image_quality = -1):

        Logger.log("d",
            "Creating snapshot. Width: %d, Height: %d, Format: %s, Quality: %d",
            image_width, image_height, image_format, image_quality
        )

        snapshot = self._get_snapshot_image(image_width, image_height)

        if snapshot:

            ba = QtCore.QByteArray()
            buffer = QtCore.QBuffer(ba)
            buffer.open(QtCore.QIODevice.WriteOnly)

            snapshot.save(buffer, image_format, image_quality)
            base64_data = ba.toBase64().data()
            base64_string = str(base64_data, 'utf-8').strip()

            data.append("\n;")
            data.append(
                "; thumbnail begin {}x{} {}".format(
                    snapshot.width(),
                    snapshot.height(),
                    len(base64_data)
                )
            )

            chunk_size = 78
            for i in range(0, len(base64_string), chunk_size):
                data.append("; " + base64_string[i:i+chunk_size])

            data.append("; thumbnail end")
            data.append(";")

    def _filterGcode(self, output_device: "OutputDevice") -> None:

        if not self._application.getPreferences().getValue("embed_snapshot/enabled"):
            return

        # No need to go any further if we can't find any gcode
        scene = self._application.getController().getScene()
        gcode_dict = getattr(scene, "gcode_dict", {})

        if not gcode_dict:
            return

        # Loop thru and parse the resolutions
        def parse_formats(formats):

            supported_formats = {
                str(x.data(), encoding='utf-8').upper(): x for x in QtGui.QImageWriter.supportedImageFormats()
            }

            for r in [r.strip() for r in formats.split(',')]:
                v = [v.strip() for v in r.split(';')]
                if v:
                    s = [s.strip() for s in v[0].split('x')]
                    if len(s) == 2:
                        try:
                            image_width = int(s[0])
                            image_height = int(s[1])
                            image_format = supported_formats["PNG"]
                            image_quality = -1
                            if len(v) > 1:
                                image_format = supported_formats.get(v[1].upper(), None) or supported_formats["PNG"]
                                if len(v) > 2:
                                    try:
                                        image_quality = int(v[2])
                                    except ValueError:
                                        pass
                            yield (image_width, image_height, image_format, image_quality)
                        except ValueError:
                            pass

        formats = self._application.getPreferences().getValue("embed_snapshot/formats") or ""
        formats = list(parse_formats(formats))

        if not formats:
            return

        image_data = []

        for f in formats:
            self._get_snapshot_base64(image_data, f[0], f[1], f[2], f[3])

        if not image_data:
            return

        image_string = "\n".join(image_data)

        for plate_id in gcode_dict:
            gcode_list = gcode_dict[plate_id]

            if len(gcode_list) < 2:
                Logger.log("w", "Plate %s does not contain any layers", plate_id)
                continue

            gcode_list[0] += image_string
            gcode_dict[plate_id] = gcode_list
