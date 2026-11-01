/*#############################################################################
 * Copyright 2015 FPT Software
 * This is UNPUBLISHED PROPRIETARY SOURCE CODE of FPT Software.
 * No part of this file may be copied, modified, sold, and distributed in any
 * form or by any means without prior explicit permission in writing from
 * FPT Software.
 *****************************
 *
 * File name            : main.qml
 *
 * Decription           : This file contains source code of main component
 *
 * Author               : TuNA8
 *
 * Created date         : 10/11/2015
 *
 * History
 *
 *  Date(DDMMYYY)   PIC	      Description
 *
 *  10112015      TuNA8 	First creation
 *  24112015      TuNA8 	update
 *
############################################################################*/
import QtQuick          2.0
import APPENUMS         1.0
import HMIEVENTS        1.0

Rectangle {
    id: root
    width:  DEVICE_WIDTH
    height: DEVICE_HEIGHT
    property var current_loader: loader_1
    property bool isDrawed: false
    property bool isShowingPopup: getShowingPopup()

    Loader {
        id: loader_1
        // VM-only layout compatibility: give the dynamic screen Loader the
        // full root size so Qt can size and hit-test its loaded item.
        anchors.fill: parent
        asynchronous: false
        onLoaded: {
            switch_current_loader( loader_2, loader_1 );
        }
    }

    Loader {
        id: loader_2
        // Same contract for the alternating transition Loader.
        anchors.fill: parent
        asynchronous: false
        onLoaded: {
            switch_current_loader( loader_1, loader_2 );
        }
    }

    // Loader for Status bar
    Loader {
        id: loader_4
        asynchronous: false
        width: AppStandbyClockModel.wideScreen ? ConstantModel.SCREEN_WIDE_WIDTH : ConstantModel.SCREEN_WIDTH
        height: 90
        z: 2
        // VM-only rendering compatibility: the live status bar continuously
        // invalidates the scene while x86 softpipe is still rasterizing a frame.
        visible: false
        sourceComponent: STComponent
    }

    Item {
        id: dimStatusBar
        anchors.fill: loader_4
        visible: isShowingPopup || AppStandbyClockModel.isSysPopupOn
        z: loader_4.z + 1
        Rectangle {
            id : dimStatusbarBtn
            anchors.fill: parent
            color: "#000000"
            opacity:0.7
        }
        MouseArea
        {
            anchors.fill: parent
        }

    }

    Rectangle {
        id: dimBG
        anchors.top: parent.top
        anchors.topMargin: 90
        width:  AppStandbyClockModel.wideScreen ? ConstantModel.SCREEN_WIDE_WIDTH : ConstantModel.SCREEN_WIDTH
        height: parent.height - 90
        visible: AppStandbyClockModel.isSysPopupOn
        opacity:0.7
        color: "#000000"
        z: dimStatusBar.z
        MouseArea
        {
            anchors.fill: parent
        }
    }

    ListModel {
        id: onsDataList
        ListElement{osdSource:""}
        ListElement{osdSource:""}
        ListElement{osdSource:""}
        ListElement{osdSource:""}
    }

    Repeater {
        id:ons_Creator
        // model for onscreen
        model:onsDataList
        Loader {
            id: osd_Loader
            z: dimStatusBar.z + 1
            width:  AppStandbyClockModel.wideScreen? 1920: 1280
            height: 720
            source: osdSource
        }
    }
    Timer{
        id: timer
        interval: 100
        running: false
        repeat: false
        onRunningChanged: {
            if(running){
                // do nothing
            }
            else{
                AppStandbyClockModel.loadingCompleted()
            }
        }
    }
    Component.onCompleted: {
        timer.start()
    }

    /******************************************************************************
      Functions
      *****************************************************************************/
    function screen_Transition() {
        isDrawed = false
        console.log("[3] SCREEN_STATE: START DRAW")
        current_loader.sourceComponent = null
        current_loader.sourceComponent = screenNext
    }

    function switch_current_loader(from, to) {
        if ( from.item !== null ) {
            from.item.visible = false
            from.sourceComponent = null
        }
        if ( to.item !== null ) {
            to.item.visible = true
        }
        console.log("[3] SCREEN_STATE: "+to.source)
        current_loader = from;
        isDrawed = true
        console.log("[3] SCREEN_STATE: DRAW FINISHED")
    }

    function load_OSD(Onsdata) {
        for(var onsCnt = 0; onsCnt < onsDataList.count; onsCnt++ )
        {
            if (onsDataList.get(onsCnt).osdSource !== ""
                    && Onsdata[onsCnt] === "")
            {
                var osdItem = ons_Creator.itemAt(onsCnt).item;
                if (osdItem.startFadeoutAni != null)
                {
                    ons_Creator.itemAt(onsCnt).item.startFadeoutAni(onsCnt);
                    ons_Creator.itemAt(onsCnt).item.fadeoutAniFinished.connect(unload_OSD_After_Ani);
                }
                else
                {
                    onsDataList.setProperty(onsCnt,"osdSource",Onsdata[onsCnt])
                }
            }
            else
            {
                onsDataList.setProperty(onsCnt,"osdSource",Onsdata[onsCnt])
            }
        }
    }
    function unload_OSD_After_Ani(index) {
        onsDataList.setProperty(index,"osdSource","");
    }

    function getShowingPopup () {
        for(var onsCnt = 0; onsCnt < onsDataList.count; onsCnt++ )
        {
            if (onsDataList.get(onsCnt).osdSource !== "")
            {
                if(onsDataList.get(onsCnt).osdSource.indexOf("QHMI_AppStandbyClockPopup_OptionMenu.qml") !== -1 ){
                    return false
                }
                 return true
            }
        }

        return false
    }
}
