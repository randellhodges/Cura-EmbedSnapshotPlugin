import QtQuick 2.2
import QtQuick.Controls 1.2
import QtQuick.Controls.Styles 1.2
import QtQuick.Layouts 1.2
import QtQuick.Window 2.2

import UM 1.2 as UM

UM.Dialog {

    id: base

    title: catalog.i18nc("@title:window", "Thumbnail Settings")
    width: 200 * screenScaleFactor

    function boolCheck(value)  {
        if (value == "True") {
            return true
        }
        else if (value == "False" || value == undefined) {
            return false
        }
        else {
            return value
        }
    }

    onAccepted: {
        UM.Preferences.setValue("embed_snapshot/enabled", enabled.checked)
        UM.Preferences.setValue("embed_snapshot/formats", resolutionInput.text)
    }

    GridLayout {

        id: grid

        columns: 2
        columnSpacing: 16 * screenScaleFactor

        anchors {
            left: parent.left
            right: parent.right
            top: parent.top
        }

        Label {
            text: "Enabled:"
        }
        CheckBox {
            id: enabled
            checked: boolCheck(UM.Preferences.getValue("embed_snapshot/enabled"))
            Layout.fillWidth: true
        }

        Label {
            text: "Formats:"
        }
        TextField {
            id: resolutionInput
            text: UM.Preferences.getValue("embed_snapshot/formats")
            Layout.fillWidth: true
        }

        Label {
            text: "Width x Height; ImageType; Quality<br/><br/><b>Width:</b> Width of image in pixels<br/><b>Height:</b> Height of image in pixels<br/><b>ImageType:</b> QImage Save Format (probably want PNG)<br/><b>Quality:</b> 0-100 (default: -1)<br/><br/>Example: 300x300;PNG;90"
            textFormat: Text.StyledText
            Layout.columnSpan: 2
        }
    }

    rightButtons: [
        Button {
            id: cancelButton
            text: catalog.i18nc("@action:button","Cancel")
            onClicked: base.reject()
        },
        Button {
            text: catalog.i18nc("@action:button", "OK")
            onClicked: base.accept()
            isDefault: true
        }
    ]

    Item {
        UM.I18nCatalog { id: catalog; name: "embed_snapshot"; }
    }
}
