import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Page {
    id: page

    function tr(key) { bridge.applicationLanguage; return bridge.tr(key) }


    Dialog {
        id: aboutDialog
        title: tr("help.about")
        modal: true
        standardButtons: Dialog.Ok
        width: Math.min(parent.width - 40, 620)

        contentItem: ColumnLayout {
            spacing: 10

            Image {
                source: Qt.resolvedUrl("../frsststems_logo_full.svg")
                Layout.alignment: Qt.AlignRight
                Layout.preferredWidth: 220
                Layout.preferredHeight: 70
                fillMode: Image.PreserveAspectFit
                horizontalAlignment: Image.AlignRight
                verticalAlignment: Image.AlignVCenter
                smooth: true
            }

            Label {
                text: tr("window.title").toUpperCase()
                font.pixelSize: 22
                font.bold: true
            }

            Label {
                text: tr("help.version") + ": " + bridge.applicationVersion
                font.bold: true
            }

            Label {
                Layout.fillWidth: true
                text: bridge.aboutText
                wrapMode: Text.WordWrap
            }

            Text {
                Layout.fillWidth: true
                textFormat: Text.RichText
                text: '<a href="https://frs777.github.io/tlumacz-v4/zrzuty.html">Strona projektu</a>'
                onLinkActivated: (link) => Qt.openUrlExternally(link)
                wrapMode: Text.WordWrap
            }

            Label {
                text: tr("help.license")
                font.bold: true
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                Label {
                    text: tr("help.title")
                    font.pixelSize: 22
                    font.bold: true
                }

                Label {
                    Layout.fillWidth: true
                    text: tr("help.subtitle")
                    color: ApplicationWindow.window.palette.text
                    wrapMode: Text.WordWrap
                }
            }

            Button {
                objectName: "aboutButton"
                text: tr("help.about")
                onClicked: aboutDialog.open()
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: ApplicationWindow.window.palette.mid
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Label {
                text: tr("settings.language")
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }

            ComboBox {
                id: applicationLanguageSelector
                Accessible.name: tr("settings.language")
                Layout.preferredWidth: 110
                model: [tr("language.polish"), tr("language.english"), tr("language.german")]
                currentIndex: bridge.applicationLanguage === "en" ? 1 : bridge.applicationLanguage === "de" ? 2 : 0
                onActivated: bridge.setApplicationLanguage(["pl", "en", "de"][currentIndex])
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }

            Item { Layout.fillWidth: true }
        }

        RowLayout {
            id: helpTabs
            objectName: "helpTabs"
            property int currentIndex: 0
            Layout.fillWidth: true
            spacing: 2

            Rectangle {
                objectName: "helpTab1"
                Layout.fillWidth: true
                height: 44
                radius: 4
                color: ApplicationWindow.window.palette.button
                border.width: 0.5
                border.color: ApplicationWindow.window.palette.mid

                Rectangle {
                    anchors.fill: parent
                    radius: parent.radius
                    color: ApplicationWindow.window.palette.highlight
                    opacity: helpTabs.currentIndex === 0 ? 1 : 0
                }

                Text {
                    objectName: "helpTabText1"
                    anchors.fill: parent
                    anchors.margins: 4
                    z: 2
                    text: bridge.helpTopic1Title
                    color: helpTabs.currentIndex === 0 ? ApplicationWindow.window.palette.highlightedText : ApplicationWindow.window.palette.buttonText
                    font.pixelSize: 13
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    wrapMode: Text.Wrap
                    maximumLineCount: 2
                    elide: Text.ElideRight
                }

                ToolTip.visible: helpTabMouse1.containsMouse
                ToolTip.text: bridge.helpTopic1Content.split("\\n")[0]
                ToolTip.delay: 350

                MouseArea {
                    id: helpTabMouse1
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: helpTabs.currentIndex = 0
                }
            }

            Rectangle {
                objectName: "helpTab2"
                Layout.fillWidth: true
                height: 44
                radius: 4
                color: ApplicationWindow.window.palette.button
                border.width: 0.5
                border.color: ApplicationWindow.window.palette.mid

                Rectangle {
                    anchors.fill: parent
                    radius: parent.radius
                    color: ApplicationWindow.window.palette.highlight
                    opacity: helpTabs.currentIndex === 1 ? 1 : 0
                }

                Text {
                    objectName: "helpTabText2"
                    anchors.fill: parent
                    anchors.margins: 4
                    z: 2
                    text: bridge.helpTopic2Title
                    color: helpTabs.currentIndex === 1 ? ApplicationWindow.window.palette.highlightedText : ApplicationWindow.window.palette.buttonText
                    font.pixelSize: 13
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    wrapMode: Text.Wrap
                    maximumLineCount: 2
                    elide: Text.ElideRight
                }

                ToolTip.visible: helpTabMouse2.containsMouse
                ToolTip.text: bridge.helpTopic2Content.split("\\n")[0]
                ToolTip.delay: 350

                MouseArea {
                    id: helpTabMouse2
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: helpTabs.currentIndex = 1
                }
            }

            Rectangle {
                objectName: "helpTab3"
                Layout.fillWidth: true
                height: 44
                radius: 4
                color: ApplicationWindow.window.palette.button
                border.width: 0.5
                border.color: ApplicationWindow.window.palette.mid

                Rectangle {
                    anchors.fill: parent
                    radius: parent.radius
                    color: ApplicationWindow.window.palette.highlight
                    opacity: helpTabs.currentIndex === 2 ? 1 : 0
                }

                Text {
                    objectName: "helpTabText3"
                    anchors.fill: parent
                    anchors.margins: 4
                    z: 2
                    text: bridge.helpTopic3Title
                    color: helpTabs.currentIndex === 2 ? ApplicationWindow.window.palette.highlightedText : ApplicationWindow.window.palette.buttonText
                    font.pixelSize: 13
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    wrapMode: Text.Wrap
                    maximumLineCount: 2
                    elide: Text.ElideRight
                }

                ToolTip.visible: helpTabMouse3.containsMouse
                ToolTip.text: bridge.helpTopic3Content.split("\\n")[0]
                ToolTip.delay: 350

                MouseArea {
                    id: helpTabMouse3
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: helpTabs.currentIndex = 2
                }
            }

            Rectangle {
                objectName: "helpTab4"
                Layout.fillWidth: true
                height: 44
                radius: 4
                color: ApplicationWindow.window.palette.button
                border.width: 0.5
                border.color: ApplicationWindow.window.palette.mid

                Rectangle {
                    anchors.fill: parent
                    radius: parent.radius
                    color: ApplicationWindow.window.palette.highlight
                    opacity: helpTabs.currentIndex === 3 ? 1 : 0
                }

                Text {
                    objectName: "helpTabText4"
                    anchors.fill: parent
                    anchors.margins: 4
                    z: 2
                    text: bridge.helpTopic4Title
                    color: helpTabs.currentIndex === 3 ? ApplicationWindow.window.palette.highlightedText : ApplicationWindow.window.palette.buttonText
                    font.pixelSize: 13
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    wrapMode: Text.Wrap
                    maximumLineCount: 2
                    elide: Text.ElideRight
                }

                ToolTip.visible: helpTabMouse4.containsMouse
                ToolTip.text: bridge.helpTopic4Content.split("\\n")[0]
                ToolTip.delay: 350

                MouseArea {
                    id: helpTabMouse4
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: helpTabs.currentIndex = 3
                }
            }

            Rectangle {
                objectName: "helpTab5"
                Layout.fillWidth: true
                height: 44
                radius: 4
                color: ApplicationWindow.window.palette.button
                border.width: 0.5
                border.color: ApplicationWindow.window.palette.mid

                Rectangle {
                    anchors.fill: parent
                    radius: parent.radius
                    color: ApplicationWindow.window.palette.highlight
                    opacity: helpTabs.currentIndex === 4 ? 1 : 0
                }

                Text {
                    objectName: "helpTabText5"
                    anchors.fill: parent
                    anchors.margins: 4
                    z: 2
                    text: bridge.helpTopic5Title
                    color: helpTabs.currentIndex === 4 ? ApplicationWindow.window.palette.highlightedText : ApplicationWindow.window.palette.buttonText
                    font.pixelSize: 13
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    wrapMode: Text.Wrap
                    maximumLineCount: 2
                    elide: Text.ElideRight
                }

                ToolTip.visible: helpTabMouse5.containsMouse
                ToolTip.text: bridge.helpTopic5Content.split("\\n")[0]
                ToolTip.delay: 350

                MouseArea {
                    id: helpTabMouse5
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: helpTabs.currentIndex = 4
                }
            }
        }

        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: helpTabs.currentIndex

            HelpMarkdownView {
                markdown: bridge.helpTopic1Content
                emptyText: tr("help.empty")
            }

            HelpMarkdownView {
                markdown: bridge.helpTopic2Content
                emptyText: tr("help.empty")
            }

            HelpMarkdownView {
                markdown: bridge.helpTopic3Content
                emptyText: tr("help.empty")
            }

            HelpMarkdownView {
                markdown: bridge.helpTopic4Content
                emptyText: tr("help.empty")
            }

            HelpMarkdownView {
                markdown: bridge.helpTopic5Content
                emptyText: tr("help.empty")
            }
        }
    }
}
