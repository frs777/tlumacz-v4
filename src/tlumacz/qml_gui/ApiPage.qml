import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

Page {
    id: page

    function tr(key) { bridge.applicationLanguage; return bridge.tr(key) }
    function longText(key) { bridge.applicationLanguage; return bridge.long_text(key) }
    function is(backend) { return bridge.backendType === backend }
    function isMozhi() { return is("cloud") && bridge.cloudProfile === "Mozhi" }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 5

        Label {
            text: tr("tab.api_server")
            font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            font.bold: true
            Layout.fillWidth: true
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 4
            visible: !is("apertium")

            Label { text: tr("settings.base_url"); font.pixelSize: ApplicationWindow.window.uiBaseFontSize }
            TextField {
                Layout.fillWidth: true
                text: is("llama") ? bridge.serverUrl : is("cloud") ? bridge.cloudServerUrl : bridge.baseUrl
                Accessible.name: tr("settings.base_url")
                enabled: !(is("cloud") && bridge.cloudProfile === "Mozhi")
                readOnly: is("llama") || (is("cloud") && bridge.cloudProfile === "Mozhi")
                opacity: enabled ? 1.0 : 0.55
                placeholderText: isMozhi() ? "auto" : ""
                onTextEdited: bridge.setBaseUrl(text)
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }

            Label { text: tr("settings.api_key"); font.pixelSize: ApplicationWindow.window.uiBaseFontSize }
            TextField {
                Layout.fillWidth: true
                echoMode: TextInput.Password
                Accessible.name: tr("settings.api_key")
                Accessible.passwordEdit: true
                text: bridge.apiKey
                enabled: !is("cloud") || bridge.cloudRequiresApiKey
                opacity: enabled ? 1.0 : 0.55
                onTextEdited: bridge.setApiKey(text)
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            visible: !is("apertium")
            spacing: 4

            Label { text: tr("settings.server"); font.pixelSize: ApplicationWindow.window.uiBaseFontSize }
            ComboBox {
                id: backendType
                Accessible.name: tr("settings.backend")
                Layout.fillWidth: true
                Layout.maximumWidth: 360
                model: bridge.backendTypes
                currentIndex: Math.max(0, model.indexOf(page.backendLabel))
                onActivated: bridge.setBackendTypeIndex(currentIndex)
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: visible
            visible: is("llama")
            spacing: 5

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: ApplicationWindow.window.palette.mid
            }

            Label {
                text: tr("settings.server_group")
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                font.bold: true
                Layout.fillWidth: true
            }

            Label { text: tr("settings.port"); font.pixelSize: ApplicationWindow.window.uiBaseFontSize }
            RowLayout {
                Layout.fillWidth: true
                spacing: 6

                SpinBox {
                    Layout.preferredWidth: 140
                    from: 1111
                    to: 65535
                    value: bridge.serverPort
                    onValueModified: bridge.setServerPort(value)
                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                }

                Button {
                    text: tr("settings.random_port")
                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                    onClicked: bridge.randomServerPort()
                }
            }

            Label { text: tr("settings.compute_mode"); font.pixelSize: ApplicationWindow.window.uiBaseFontSize }
            ComboBox {
                Layout.preferredWidth: 140
                model: bridge.computeModes
                currentIndex: Math.max(0, model.indexOf(bridge.computeMode))
                onActivated: bridge.setComputeMode(currentText)
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }

            Label { text: tr("settings.chat_template"); font.pixelSize: ApplicationWindow.window.uiBaseFontSize }
            ComboBox {
                objectName: "chatTemplateSelector"
                Layout.preferredWidth: 140
                model: bridge.chatTemplates
                currentIndex: bridge.chatTemplate === "TranslateGemma" ? 2
                             : bridge.chatTemplate === "chatml" ? 1 : 0
                onActivated: bridge.setChatTemplate(
                    index === 2 ? "TranslateGemma" : index === 1 ? "chatml" : "jinja"
                )
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }

            Label { text: tr("settings.parallel"); font.pixelSize: ApplicationWindow.window.uiBaseFontSize }
            SpinBox {
                Layout.preferredWidth: 140
                from: 1
                to: 8
                value: bridge.parallel
                onValueModified: bridge.setParallel(value)
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }

            Label { text: tr("settings.model"); font.pixelSize: ApplicationWindow.window.uiBaseFontSize }
            RowLayout {
                Layout.fillWidth: true
                spacing: 6
                TextField {
                    Layout.fillWidth: true
                    text: bridge.ggufPath
                    readOnly: true
                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                }
                Button {
                    text: tr("button.browse")
                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                    onClicked: ggufDialog.open()
                }
            }

            Item {
                Layout.fillHeight: true
            }

            GroupBox {
                objectName: "llamaBackendBehavior"
                title: ""
                Layout.fillWidth: true
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                label: Label {
                    text: tr("settings.backend_behavior_group")
                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                    font.bold: true
                }

                ColumnLayout {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    spacing: 2

                    CheckBox {
                        objectName: "autoStartServer"
                        text: tr("settings.auto_start")
                        checked: bridge.autoStartServer
                        onToggled: bridge.setAutoStartServer(checked)
                        font.pixelSize: 14
                        Layout.alignment: Qt.AlignLeft
                    }

                    CheckBox {
                        objectName: "cacheClearAfterTranslation"
                        text: tr("settings.clear_cache")
                        checked: bridge.cacheClearAfterTranslation
                        onToggled: bridge.setCacheClearAfterTranslation(checked)
                        font.pixelSize: 14
                        Layout.alignment: Qt.AlignLeft
                    }

                    CheckBox {
                        objectName: "restartLlamaAfterTranslation"
                        text: tr("settings.restart_llama_after_translation")
                        checked: bridge.restartLlamaAfterTranslation
                        onToggled: bridge.setRestartLlamaAfterTranslation(checked)
                        font.pixelSize: 14
                        Layout.alignment: Qt.AlignLeft
                    }
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: visible
            visible: is("apertium")
            spacing: 5

            GridLayout {
                Layout.fillWidth: true
                columns: 2
                columnSpacing: 24
                rowSpacing: 7

                Label {
                    text: tr("apertium.source_language")
                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                }

                ComboBox {
                    id: apertiumSourceLanguage
                    Layout.preferredWidth: 140
                    Layout.minimumWidth: 140
                    Layout.maximumWidth: 140
                    model: bridge.apertiumSourceLanguages
                    currentIndex: Math.max(0, model.indexOf(bridge.sourceLanguageLabel))
                    onActivated: bridge.setSourceLanguage(currentText)
                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                }

                Label {
                    text: tr("settings.target_language")
                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                }

                ComboBox {
                    id: apertiumTargetLanguage
                    Layout.preferredWidth: 140
                    Layout.minimumWidth: 140
                    Layout.maximumWidth: 140
                    model: bridge.apertiumTargetLanguages
                    currentIndex: Math.max(-1, model.indexOf(bridge.apertiumTargetLanguageLabel))
                    enabled: bridge.apertiumTargetSelectionEnabled
                    Accessible.name: tr("settings.target_language")
                    onActivated: bridge.setTargetLanguage(currentText)
                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: ApplicationWindow.window.palette.mid
            }

            Label { text: tr("settings.server"); font.pixelSize: ApplicationWindow.window.uiBaseFontSize }
            ComboBox {
                id: apertiumBackendType
                Layout.fillWidth: true
                Layout.maximumWidth: 360
                model: bridge.backendTypes
                currentIndex: Math.max(0, model.indexOf(page.backendLabel))
                onActivated: bridge.setBackendTypeIndex(currentIndex)
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }

            Label {
                objectName: "apertiumBackendBehaviorHeading"
                text: tr("settings.backend_behavior_group")
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                font.bold: true
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignLeft
            }

            TextArea {
                objectName: "apertiumBackendDescription"
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: 150
                Layout.alignment: Qt.AlignLeft
                readOnly: true
                wrapMode: TextArea.Wrap
                text: longText("apertium.description")
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }

            GroupBox {
                objectName: "apertiumBackendBehavior"
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignLeft
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize

                ColumnLayout {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    spacing: 2

                    CheckBox {
                        objectName: "cacheClearAfterTranslationApertium"
                        text: tr("settings.clear_cache")
                        checked: bridge.cacheClearAfterTranslation
                        onToggled: bridge.setCacheClearAfterTranslation(checked)
                        font.pixelSize: 14
                        Layout.alignment: Qt.AlignLeft
                    }

                    CheckBox {
                        objectName: "restartApertiumAfterTranslation"
                        text: tr("settings.restart_apertium_after_translation")
                        checked: bridge.restartApertiumAfterTranslation
                        onToggled: bridge.setRestartApertiumAfterTranslation(checked)
                        font.pixelSize: 14
                        Layout.alignment: Qt.AlignLeft
                    }
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: visible
            visible: is("cloud")
            spacing: 5

            Label {
                text: tr("cloud.provider")
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }

            ComboBox {
                Layout.preferredWidth: 180
                model: bridge.cloudProfiles
                currentIndex: Math.max(0, model.indexOf(bridge.cloudProfile))
                onActivated: bridge.setCloudProfile(currentText)
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }

            RowLayout {
                Layout.fillWidth: true
                visible: bridge.cloudProfile === "Mozhi"
                spacing: 10

                ColumnLayout {
                    Layout.fillWidth: true
                    Label { text: tr("cloud.engine"); font.pixelSize: ApplicationWindow.window.uiBaseFontSize }
                    ComboBox {
                        Layout.fillWidth: true
                        model: bridge.mozhiEngines
                        currentIndex: Math.max(0, model.indexOf(bridge.mozhiEngine))
                        onActivated: bridge.setMozhiEngine(currentText)
                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    Label { text: tr("cloud.instance"); font.pixelSize: ApplicationWindow.window.uiBaseFontSize }
                    ComboBox {
                        Layout.fillWidth: true
                        model: bridge.mozhiInstances
                        currentIndex: Math.max(0, model.indexOf(bridge.mozhiInstance))
                        onActivated: bridge.setMozhiInstance(currentText)
                        font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                    }
                }
            }

            Label {
                objectName: "cloudBackendBehaviorHeading"
                visible: isMozhi()
                text: tr("settings.backend_behavior_group")
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                font.bold: true
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignLeft
            }

            TextArea {
                objectName: "mozhiAutoInfo"
                visible: isMozhi()
                Layout.fillWidth: true
                Layout.fillHeight: visible
                Layout.minimumHeight: 92
                Layout.alignment: Qt.AlignLeft
                text: longText("cloud.mozhi_auto_info")
                readOnly: true
                wrapMode: TextArea.Wrap
                font.pixelSize: 14
            }

            Item {
                visible: !isMozhi()
                Layout.fillHeight: !isMozhi()
            }

            Label {
                objectName: "cloudBackendBehaviorHeadingNonMozhi"
                visible: !isMozhi()
                text: tr("settings.backend_behavior_group")
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                font.bold: true
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignLeft
            }

            GroupBox {
                objectName: "cloudBackendBehavior"
                title: ""
                Layout.fillWidth: true
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize

                CheckBox {
                    objectName: "reconnectCloudAfterTranslation"
                    text: tr("settings.reconnect_cloud_after_translation")
                    checked: bridge.reconnectCloudAfterTranslation
                    onToggled: bridge.setReconnectCloudAfterTranslation(checked)
                    font.pixelSize: 14
                    Layout.alignment: Qt.AlignLeft
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: visible
            visible: is("custom")
            spacing: 5

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: ApplicationWindow.window.palette.mid
            }

            Label {
                text: tr("settings.base_url")
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }

            TextField {
                Layout.fillWidth: true
                text: bridge.baseUrl
                Accessible.name: tr("settings.base_url")
                placeholderText: "http://127.0.0.1:port/v1"
                onTextEdited: bridge.setBaseUrl(text)
                font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: 220
                color: ApplicationWindow.window.palette.base
                border.width: 0.5
                border.color: ApplicationWindow.window.palette.mid
                radius: 3

                TextArea {
                    anchors.fill: parent
                    anchors.margins: 8
                    readOnly: true
                    wrapMode: TextArea.Wrap
                    color: ApplicationWindow.window.palette.text
                    font.pixelSize: ApplicationWindow.window.uiBaseFontSize
                    text: longText("custom.description")
                }
            }
        }

        Button {
            id: restartButton
            Layout.fillWidth: true
            visible: is("llama")
            enabled: !bridge.serverOperationBusy
            text: tr("button.restart_server")
            font.pixelSize: ApplicationWindow.window.uiBaseFontSize
            onClicked: bridge.restartServer()
        }
    }

    FileDialog {
        id: ggufDialog
        title: tr("ui.gguf_dialog")
        fileMode: FileDialog.OpenFile
        nameFilters: [tr("dialog.gguf_filter"), tr("dialog.all_files")]
        onAccepted: bridge.setGgufPath(selectedFile)
    }

    property string backendLabel: {
        switch (bridge.backendType) {
        case "llama": return "llama.cpp"
        case "apertium": return tr("backend.apertium_local_server")
        case "cloud": return tr("backend.cloud_server")
        default: return tr("custom.server_type")
        }
    }
}
