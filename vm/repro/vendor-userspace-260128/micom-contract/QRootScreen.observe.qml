import QtQuick                      2.0
import HMIEVENTS                    1.0

Item {
    /******************************************************************************
      ID
      *****************************************************************************/
    id: root
    readonly property int _GROUP_HEADER :    1
    readonly property int _GROUP_LEFT   :    2
    readonly property int _GROUP_FOOTER :    3
    readonly property int _GROUP_RIGHT  :    4
    readonly property int _GROUP_CENTER :    5

    property bool isOnTop: false
    /******************************************************************************

    /******************************************************************************
      Completed
      *****************************************************************************/
    Component.onCompleted: {

    }

    /******************************************************************************
      Destruction
      *****************************************************************************/
    Component.onDestruction: {

    }

    function _DLT_HIGH(){
        var dataLog = ""
        for(var cnt = 0; cnt < arguments.length; cnt++) {
            dataLog += arguments[cnt]
        }
        dataLog = "[3]" + "QML: >>> " + dataLog
        console.log(dataLog)
    }

    MouseArea{
        anchors.fill: parent
        z:1000
        propagateComposedEvents: true
        onPressed: {
            console.log("VM_OBSERVE_ROOT_MOUSE pressed", mouse.x, mouse.y,
                        "area", width, height, "root", root.width, root.height)
            QML_Handler.qmlSendEvtKey(HMIEVENTS.EVT_FOCUS_STATE_TO_THIS_APP)
            mouse.accepted = false
            console.log("VM_OBSERVE_ROOT_MOUSE rejected", mouse.accepted)
        }
    }
}
