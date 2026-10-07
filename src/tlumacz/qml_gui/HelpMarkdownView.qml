import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: view

    property string markdown: ""
    property string emptyText: "Brak treści pomocy."

    clip: true
    contentWidth: Math.max(availableWidth, reader.width)
    contentHeight: reader.height
    ScrollBar.vertical.policy: ScrollBar.AsNeeded
    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

    Rectangle {
        id: surface
        x: Math.max(0, (view.availableWidth - width) / 2)
        width: Math.min(view.availableWidth, 880)
        height: reader.height + 40
        radius: 10
        color: ApplicationWindow.window.palette.base
        border.width: 0
        border.color: ApplicationWindow.window.palette.mid

        TextEdit {
            id: reader
            x: 20
            y: 20
            width: Math.max(0, surface.width - 40)
            height: Math.max(80, implicitHeight)
            readOnly: true
            selectByMouse: true
            persistentSelection: true
            wrapMode: TextEdit.Wrap
            textFormat: TextEdit.MarkdownText
            text: view.markdown || view.emptyText
            color: ApplicationWindow.window.palette.text
            selectionColor: ApplicationWindow.window.palette.highlight
            selectedTextColor: ApplicationWindow.window.palette.highlightedText
            font.pixelSize: 16
            font.weight: Font.Normal
            padding: 0
        }
    }
}
