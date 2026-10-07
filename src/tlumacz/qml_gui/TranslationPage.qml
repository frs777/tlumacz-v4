import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts

Page {
    id: page

    function tr(key) { bridge.applicationLanguage; return bridge.tr(key) }

    function formatTime(seconds) {
        var m = Math.floor(seconds / 60)
        var s = seconds % 60
        return (m < 10 ? "0" : "") + m + ":" +
               (s < 10 ? "0" : "") + s
    }

    FileDialog {
        id: inputDialog
        title: tr("ui.file_input_dialog")
        fileMode: FileDialog.OpenFile
        onAccepted: bridge.setInputPath(selectedFile)
    }

    FileDialog {
        id: outputDialog
        title: tr("ui.file_output_dialog")
        fileMode: FileDialog.SaveFile
        onAccepted: bridge.setOutputPath(selectedFile)
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: ApplicationWindow.window.uiCompactSpacing

        // Jedyna sekcja nagłówkowa przed właściwymi kontrolkami plików.
        Label {
            Layout.fillWidth: true
            text: tr("files.group")
            font.pixelSize: 20
            font.bold: true
        }

        GridLayout {
            Layout.fillWidth: true
            columns: 3
            columnSpacing: 10
            rowSpacing: 2

            Label {
                text: tr("files.input")
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }
            TextField {
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                Layout.minimumHeight: ApplicationWindow.window.uiControlHeight
                Layout.preferredHeight: ApplicationWindow.window.uiControlHeight
                Layout.maximumHeight: ApplicationWindow.window.uiControlHeight
                text: bridge.inputPath
                Accessible.name: tr("files.input")
                onTextEdited: bridge.setInputPath(text)
            }
            Button {
                Layout.preferredWidth: 130
                Layout.maximumWidth: 130
                text: tr("button.browse")
                Accessible.name: tr("files.input") + ": " + tr("button.browse")
                onClicked: inputDialog.open()
            }

            Label {
                text: tr("files.output")
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }
            TextField {
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                Layout.minimumHeight: ApplicationWindow.window.uiControlHeight
                Layout.preferredHeight: ApplicationWindow.window.uiControlHeight
                Layout.maximumHeight: ApplicationWindow.window.uiControlHeight
                text: bridge.outputPath
                Accessible.name: tr("files.output")
                onTextEdited: bridge.setOutputPath(text)
            }
            Button {
                Layout.preferredWidth: 130
                Layout.maximumWidth: 130
                text: tr("button.browse")
                Accessible.name: tr("files.output") + ": " + tr("button.browse")
                onClicked: outputDialog.open()
            }
        }

        // Postęp i statystyki są pod plikami, a sterowanie pozostaje bezpośrednio nad Logiem.
        ColumnLayout {
            objectName: "progressSection"
            Layout.fillWidth: true
            spacing: 2

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                ProgressBar {
                    Layout.fillWidth: true
                    from: 0
                    to: 100
                    value: bridge.progress
                }

                Label {
                    text: bridge.progress + "%"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                }
            }
        }

        ColumnLayout {
            objectName: "statisticsSection"
            Layout.fillWidth: true
            spacing: 2

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Item {
                    id: translationWorkOrb
                    objectName: "translationWorkOrb"
                    Layout.preferredWidth: 22
                    Layout.minimumWidth: 22
                    Layout.maximumWidth: 22
                    Layout.preferredHeight: 22
                    Layout.minimumHeight: 22
                    Layout.maximumHeight: 22
                    visible: bridge.isTranslating
                    opacity: visible ? 1 : 0
                    rotation: 0

                    Rectangle {
                        anchors.centerIn: parent
                        width: 16
                        height: 16
                        radius: 8
                        color: "transparent"
                        border.width: 2
                        border.color: orbCore.color
                    }

                    Rectangle {
                        id: orbCore
                        anchors.centerIn: parent
                        width: 6
                        height: 6
                        radius: 3
                        color: "#80cbc4"

                        SequentialAnimation on scale {
                            id: orbPulse
                            running: translationWorkOrb.visible
                            loops: Animation.Infinite
                            NumberAnimation { to: 1.35; duration: 650; easing.type: Easing.InOutSine }
                            NumberAnimation { to: 0.8; duration: 650; easing.type: Easing.InOutSine }
                        }

                        SequentialAnimation on color {
                            running: translationWorkOrb.visible
                            loops: Animation.Infinite
                            ColorAnimation { to: "#80cbc4"; duration: 700 }
                            ColorAnimation { to: "#90caf9"; duration: 700 }
                            ColorAnimation { to: "#ce93d8"; duration: 700 }
                        }
                    }

                    RotationAnimator on rotation {
                        running: translationWorkOrb.visible
                        from: 0
                        to: 360
                        duration: 1800
                        loops: Animation.Infinite
                    }

                    Accessible.ignored: true
                }

                Label {
                    text: tr("ui.time")
                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                }
                Label {
                    text: formatTime(bridge.elapsedSeconds)
                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize + 1
                    font.bold: true
                }

                RowLayout {
                    spacing: 4

                    Label {
                        text: tr("ui.translation_speed")
                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                    }

                    Label {
                        text: bridge.currentSpeed + tr("ui.chars_per_second")
                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize + 1
                        font.bold: true
                    }
                }

                Item { Layout.fillWidth: true }
            }
        }

        ColumnLayout {
            objectName: "translationControlsSection"
            Layout.fillWidth: true
            spacing: 2

            RowLayout {
                Layout.fillWidth: true
                Layout.topMargin: 0
                Layout.bottomMargin: 0
                spacing: 2

                Button {
                    objectName: "translateButton"
                    Layout.preferredWidth: 130
                    Layout.minimumWidth: 130
                    Layout.maximumWidth: 130
                    Layout.alignment: Qt.AlignBottom
                    text: tr("button.translate")
                    highlighted: true
                    enabled: !bridge.isTranslating
                    onClicked: bridge.startTranslation()
                }

                Button {
                    id: cancelButton
                    objectName: "cancelButton"
                    Layout.preferredWidth: 130
                    Layout.minimumWidth: 130
                    Layout.maximumWidth: 130
                    Layout.alignment: Qt.AlignBottom
                    text: tr("button.cancel")
                    enabled: bridge.isTranslating
                    onClicked: bridge.cancelTranslation()

                    background: Rectangle {
                        radius: 3
                        color: cancelButton.enabled ? "#c62828" : "#8e3a3a"
                    }

                    contentItem: Text {
                        text: cancelButton.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }

                Item { Layout.fillWidth: true }

                ColumnLayout {
                    visible: bridge.backendType === "apertium"
                    Layout.preferredWidth: 120
                    Layout.maximumWidth: 120
                    spacing: 2

                    Label {
                        text: tr("translation.source_language")
                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                    }

                    TextField {
                        id: apertiumSourceLanguage
                        Layout.fillWidth: true
                        Layout.minimumHeight: ApplicationWindow.window.uiControlHeight
                        Layout.preferredHeight: ApplicationWindow.window.uiControlHeight
                        Layout.maximumHeight: ApplicationWindow.window.uiControlHeight
                        text: bridge.apertiumSourceLanguageLabel
                        Accessible.name: tr("translation.source_language")
                        readOnly: true
                    }
                }

                ColumnLayout {
                    visible: bridge.backendType === "apertium"
                    Layout.preferredWidth: 120
                    Layout.maximumWidth: 120
                    spacing: 2

                    Label {
                        text: tr("translation.target_language")
                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                    }

                    TextField {
                        id: apertiumTargetLanguage
                        Layout.fillWidth: true
                        Layout.minimumHeight: ApplicationWindow.window.uiControlHeight
                        Layout.preferredHeight: ApplicationWindow.window.uiControlHeight
                        Layout.maximumHeight: ApplicationWindow.window.uiControlHeight
                        text: bridge.apertiumTargetLanguageLabel
                        Accessible.name: tr("translation.target_language")
                        readOnly: true
                    }
                }

                Label {
                    visible: bridge.backendType !== "apertium"
                    text: tr("settings.target_language")
                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                }

                ComboBox {
                    id: targetLanguage
                    Accessible.name: tr("settings.target_language")
                    visible: bridge.backendType !== "apertium"
                    Layout.preferredWidth: 110
                    Layout.maximumWidth: 110
                    Layout.minimumHeight: ApplicationWindow.window.uiControlHeight
                    Layout.preferredHeight: ApplicationWindow.window.uiControlHeight
                    Layout.maximumHeight: ApplicationWindow.window.uiControlHeight
                    model: bridge.targetLanguages
                    currentIndex: model.indexOf(bridge.targetLanguageLabel)
                    onActivated: bridge.setTargetLanguage(currentText)
                }
            }
        }

        Rectangle {
            objectName: "sectionSeparator"
            Layout.fillWidth: true
            height: 1
            color: ApplicationWindow.window.palette.mid
        }

        Label {
            Layout.fillWidth: true
            text: tr("files.log") + ":"
            font.pixelSize: 16
            font.bold: true
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 180
            Layout.preferredHeight: 300

            TextArea {
                readOnly: true
                wrapMode: TextArea.Wrap
                text: bridge.logText
                onTextChanged: cursorPosition = length
            }
        }

        // Wiążący separator pomiędzy Logiem a Podglądem.
        Rectangle {
            objectName: "sectionSeparator"
            Layout.fillWidth: true
            height: 1
            color: ApplicationWindow.window.palette.mid
        }

        Label {
            Layout.fillWidth: true
            text: tr("files.preview") + ":"
            font.pixelSize: 16
            font.bold: true
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 180
            Layout.preferredHeight: 300

            TextArea {
                readOnly: true
                wrapMode: TextArea.Wrap
                text: bridge.previewText
                placeholderText: tr("ui.preview_placeholder")
            }
        }
    }
}
