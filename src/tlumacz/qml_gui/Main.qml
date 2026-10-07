import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    title: tr("window.title")
    function tr(key) { bridge.applicationLanguage; return bridge.tr(key) }
    readonly property int uiBaseFontSize: 15
    readonly property int uiControlHeight: 36
    readonly property int uiCompactSpacing: 2
    readonly property int uiPageMargin: 8
    visible: true
    font.pixelSize: uiBaseFontSize
    width: bridge.settingsWindowWidth > 0 ? bridge.settingsWindowWidth : 1120
    height: bridge.settingsWindowHeight > 0 ? bridge.settingsWindowHeight : 780
    Component.onCompleted: {
        if (bridge.settingsWindowX >= 0) root.x = bridge.settingsWindowX
        if (bridge.settingsWindowY >= 0) root.y = bridge.settingsWindowY
        bridge.showNextFilterDependencyWarning()
    }

    // Tło pochodzi z palety dostarczonej przez Qt. Nie definiujemy
    // lokalnych ról palety, aby Fusion mógł reagować na QStyleHints
    // dokładnie tak samo jak przy zmianie schematu systemowego.
    color: palette.window

    Timer {
        id: geometrySaveTimer
        interval: 500
        repeat: false
        onTriggered: bridge.saveWindowState(root.x, root.y, root.width, root.height)
    }

    onXChanged: geometrySaveTimer.restart()
    onYChanged: geometrySaveTimer.restart()
    onWidthChanged: geometrySaveTimer.restart()
    onHeightChanged: geometrySaveTimer.restart()

    onClosing: (close) => {
        bridge.saveSettings()
        bridge.saveWindowState(root.x, root.y, root.width, root.height)
        close.accepted = true
    }


    Dialog {
        id: filterDependencyWarningDialog
        objectName: "filterDependencyWarningDialog"
        title: tr("dialog.filter_dependency_title")
        modal: true
        width: Math.min(root.width - 40, 760)
        standardButtons: Dialog.Ok
        property string warningText: ""

        contentItem: Text {
            text: filterDependencyWarningDialog.warningText
            textFormat: Text.RichText
            wrapMode: Text.Wrap
            width: filterDependencyWarningDialog.width - 40
            padding: 10
            onLinkActivated: (link) => Qt.openUrlExternally(link)
        }

        onClosed: bridge.showNextFilterDependencyWarning()
    }

    Connections {
        target: bridge
        function onFilterDependencyWarning(message) {
            filterDependencyWarningDialog.warningText = message
            filterDependencyWarningDialog.open()
        }

    }


    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8

        TabBar {
            id: tabs
            objectName: "mainTabs"
            Layout.fillWidth: true
            TabButton { text: tr("tab.translation") }
            TabButton { text: tr("tab.api_server") }
            TabButton { text: tr("tab.switches") }
            TabButton { text: tr("tab.help") }
        }

        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabs.currentIndex
            TranslationPage {}
            ApiPage {}
            ExtrasPage {}
            HelpPage {}
        }
    }
}
