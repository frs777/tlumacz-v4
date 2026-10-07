import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts

Page {
    id: page

    // Karta używa regularnej wagi; pogrubienie jest zarezerwowane dla nagłówków sekcji.
    font.weight: Font.Normal

    function tr(key) { bridge.applicationLanguage; return bridge.tr(key) }

    FileDialog {
        id: glossaryDialog
        title: tr("ui.glossary_dialog")
        fileMode: FileDialog.OpenFile
        nameFilters: [tr("ui.glossary_filter")]
        onAccepted: bridge.setGlossaryPath(selectedFile)
    }

    FileDialog {
        id: skillDialog
        title: tr("ui.skill_import_dialog")
        fileMode: FileDialog.OpenFile
        nameFilters: [tr("dialog.skill_filter"), tr("dialog.all_files")]
        onAccepted: bridge.importSkill(selectedFile)
    }

    Dialog {
        id: skillTemplateDialog
        title: tr("skill.template_title")
        modal: true
        width: Math.min(page.width - 30, 760)
        height: Math.min(page.height - 30, 620)
        standardButtons: Dialog.Save | Dialog.Cancel

        property string content: bridge.skillTemplate
        onOpened: content = bridge.skillTemplate
        onAccepted: bridge.saveSkillTemplate(content)

        TextArea {
            anchors.fill: parent
            anchors.margins: 8
            wrapMode: TextArea.Wrap
            font.pixelSize: 14
            text: skillTemplateDialog.content
            onTextChanged: skillTemplateDialog.content = text
        }
    }


    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 4
        spacing: 8

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            ColumnLayout {
                width: Math.min(parent.width, 760)
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 8

            GroupBox {
                title: tr("settings.glossary_group")
                Layout.fillWidth: true
                font.pixelSize: 16
                label: Label {
                    text: tr("settings.glossary_group")
                    font.pixelSize: 16
                    font.bold: true
                }

                ColumnLayout {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    spacing: 6

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6

                        TextField {
                            Layout.fillWidth: true
                            Layout.minimumWidth: 0
                            placeholderText: tr("settings.glossary_path_hint")
                            text: bridge.glossaryPath
                            readOnly: true
                            font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                        }

                        Button {
                            Layout.preferredWidth: 120
                            Layout.minimumWidth: 120
                            Layout.maximumWidth: 120
                            text: tr("button.browse")
                            font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                            onClicked: glossaryDialog.open()
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6

                        TextField {
                            id: glossarySource
                            Accessible.name: tr("glossary.source")
                            Layout.fillWidth: true
                            Layout.minimumWidth: 0
                            placeholderText: tr("glossary.source")
                            font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                        }

                        TextField {
                            id: glossaryTranslation
                            Layout.fillWidth: true
                            Layout.minimumWidth: 0
                            placeholderText: tr("glossary.translation")
                            Accessible.name: tr("glossary.translation")
                            font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                        }

                        Button {
                            Layout.preferredWidth: 120
                            Layout.minimumWidth: 120
                            Layout.maximumWidth: 120
                            text: tr("button.add")
                            font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                            enabled: glossarySource.text.trim() !== "" &&
                                     glossaryTranslation.text.trim() !== "" &&
                                     bridge.glossaryPath !== ""
                            onClicked: {
                                bridge.addGlossaryEntry(glossarySource.text, glossaryTranslation.text)
                                glossarySource.clear()
                                glossaryTranslation.clear()
                            }
                        }
                    }

                    Label {
                        Layout.fillWidth: true
                        text: bridge.glossaryStatus.replace(/\d+ - pary? wyrazów/, function(match) {
                            var count = match.match(/\d+/)
                            return count ? "Lini " + count[0] : "Lini"
                        }).replace(/\d+ - par wyrazów/, "Lini")
                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: ApplicationWindow.window.palette.mid
            }

            GroupBox {
                title: tr("settings.skills_group")
                Layout.fillWidth: true
                font.pixelSize: 16
                label: Label {
                    text: tr("settings.skills_group")
                    font.pixelSize: 16
                    font.bold: true
                }

                ColumnLayout {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    spacing: 7

                    GridLayout {
                        Layout.fillWidth: true
                        columns: 2
                        columnSpacing: 8
                        rowSpacing: 0

                        Frame {
                            Layout.fillWidth: true
                            Layout.alignment: Qt.AlignTop
                            padding: 6

                            ColumnLayout {
                                anchors.left: parent.left
                                anchors.right: parent.right
                                spacing: 2

                                Label {
                                    text: tr("ui.system_skills")
                                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                                }

                                Repeater {
                                    model: bridge.skillOptions

                                    delegate: CheckBox {
                                        text: modelData
                                        checked: bridge.skillEnabled(modelData)
                                        onToggled: bridge.setSkillEnabled(modelData, checked)
                                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                                        Layout.fillWidth: true
                                    }
                                }
                            }
                        }

                        Frame {
                            Layout.fillWidth: true
                            Layout.alignment: Qt.AlignTop
                            padding: 6

                            ColumnLayout {
                                anchors.left: parent.left
                                anchors.right: parent.right
                                spacing: 2

                                Label {
                                    text: tr("ui.user_skills")
                                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                                }

                                Repeater {
                                    model: bridge.userSkills

                                    delegate: RowLayout {
                                        spacing: 2
                                        Layout.fillWidth: true

                                        CheckBox {
                                            text: modelData
                                            checked: bridge.skillEnabled(modelData)
                                            onToggled: bridge.setSkillEnabled(modelData, checked)
                                            font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                                            Layout.fillWidth: true
                                        }

                                        ToolButton {
                                            icon.name: "window-close"
                                            icon.width: 16
                                            icon.height: 16
                                            Layout.preferredWidth: 28
                                            Layout.maximumWidth: 28
                                            Accessible.name: tr("ui.delete_skill")
                                            ToolTip.visible: hovered
                                            ToolTip.text: tr("ui.delete_skill")
                                            onClicked: bridge.deleteSkill(modelData)
                                        }
                                    }
                                }

                                Label {
                                    visible: bridge.userSkills.length === 0
                                    text: tr("ui.no_user_skills")
                                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                                    opacity: 0.65
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: ApplicationWindow.window.palette.mid
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6

                        Button {
                            text: tr("button.import_skill")
                            font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                            Layout.preferredWidth: 180
                            Layout.minimumWidth: 180
                            Layout.maximumWidth: 180
                            onClicked: skillDialog.open()
                        }

                        Button {
                            text: tr("button.new_skill")
                            font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                            Layout.preferredWidth: 180
                            Layout.minimumWidth: 180
                            Layout.maximumWidth: 180
                            onClicked: skillTemplateDialog.open()
                        }

                        Button {
                            text: tr("button.refresh")
                            font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                            Layout.preferredWidth: 180
                            Layout.minimumWidth: 180
                            Layout.maximumWidth: 180
                            onClicked: bridge.refreshSkills()
                        }

                        Item { Layout.fillWidth: true }
                    }
                }
            }




            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: ApplicationWindow.window.palette.mid
            }

            Rectangle {
                objectName: "llmSectionSeparator"
                Layout.fillWidth: true
                height: 1
                color: ApplicationWindow.window.palette.mid
                visible: bridge.backendType !== "apertium"
            }

            GroupBox {
                title: tr("settings.llm_group")
                visible: bridge.backendType !== "apertium"
                Layout.fillWidth: true
                font.pixelSize: 16
                label: Label {
                    text: tr("settings.llm_group")
                    font.pixelSize: 16
                    font.bold: true
                }

                GridLayout {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    columns: 2
                    columnSpacing: 10
                    rowSpacing: 6

                    Label {
                        text: tr("settings.block_size")
                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                    }

                    SpinBox {
                        Layout.preferredWidth: 120
                        Layout.minimumWidth: 120
                        Layout.maximumWidth: 120
                        from: 500
                        to: 8000
                        stepSize: 500
                        value: bridge.chunkSize
                        editable: true
                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                        onValueModified: bridge.setChunkSize(value)
                    }

                    Label {
                        text: tr("settings.temperature")
                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                    }

                    SpinBox {
                        Layout.preferredWidth: 120
                        Layout.minimumWidth: 120
                        Layout.maximumWidth: 120
                        from: 0
                        to: 10
                        stepSize: 1
                        value: Math.round(bridge.temperature * 10)
                        editable: true
                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                        textFromValue: function(value, locale) { return (value / 10).toFixed(1) }
                        valueFromText: function(text, locale) { return Math.round(parseFloat(text) * 10) }
                        onValueModified: bridge.setTemperature(value / 10)
                    }

                    Label {
                        text: tr("settings.custom_prompt")
                        Layout.alignment: Qt.AlignTop
                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                    }

                    TextArea {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 70
                        placeholderText: tr("ui.optional_prompt")
                        text: bridge.systemPrompt
                        wrapMode: TextArea.Wrap
                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                        onTextChanged: if (activeFocus) bridge.setSystemPrompt(text)
                    }

                    Label {
                        text: tr("settings.skip_patterns")
                        Layout.alignment: Qt.AlignTop
                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                    }

                    TextArea {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 60
                        text: bridge.skipPatterns
                        wrapMode: TextArea.Wrap
                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                        onTextChanged: if (activeFocus) bridge.setSkipPatterns(text)
                    }
                }
            }

            }
        }

        RowLayout {
            id: settingsActions
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignLeft
            spacing: 6

            Button {
                text: tr("button.restore_defaults")
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                Layout.alignment: Qt.AlignLeft
                onClicked: bridge.resetSettings()
            }

            Button {
                text: tr("button.save_settings")
                highlighted: true
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                Layout.alignment: Qt.AlignLeft
                onClicked: bridge.saveSettings()
            }

            Item { Layout.fillWidth: true }
        }
    }
}
