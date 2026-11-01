import QtQuick                  2.0
import HMIEVENTS                1.0
import APPENUMS                 1.0
import "components"
import "components/common"

QRootScreen {

    /*========================================= USER-DEFINED PROPERTY & SIGNALS ===========================================*/
    property bool isWideScreen: AppStandbyClockModel.wideScreen
    property bool isDriving: AppStandbyClockModel.drivingRestriction
    property bool isDimmed: (AppStandbyClockModel.drivingRestriction
                            || AppStandbyClockModel.voiceMemoStatus ===  APPENUMS.E_VOICEMEMO_RECORDING
                            ||AppStandbyClockModel.driverTalkStatus ===1
                            || AppStandbyClockModel.isCalling)
    property bool isPressedConfirm: false
    property bool isCalling: AppStandbyClockModel.isCalling

    /*========================================= PROPERTY ===========================================*/
    id: root
    visible: true
    // VM-only layout repair: the authentic screen and its Loader otherwise
    // resolve to 0x0 even though explicit-size children render outside it.
    // This restores the full-screen parent hit-test bounds without changing
    // button state, handlers, or the legal-confirm action.
    width: isWideScreen ? ConstantModel.SCREEN_WIDE_WIDTH : ConstantModel.SCREEN_WIDTH
    height: 720

    /*========================================= VISUAL ELEMENTS ===========================================*/
    /*Background*/
    QThemeImage {
        id: idStandbyBackground
        x:0
        y:0
        width: sourceSize.width
        height: sourceSize.height
        themeSource: (isWideScreen) ? ImagesModel.home_main_bg_01 : ImagesModel.home_main_bg_02
    }
    QThemeImage {
        id: bg
        x: 9
        y:90
        themeSource: (isWideScreen) ? ImagesModel.pf_bg_welcome_w : ImagesModel.pf_bg_welcome_s
    }
    QItem{
        id: txtArea
        width: (isWideScreen)? 1450 :848
        height: 621
        anchors{
            top: bg.top
            right: bg.right
        }
        Item {
            id: txtDrive
            width: parent.width
            height: 531
            anchors.top: parent.top
            anchors.left: parent.left
            QText{
                id: txtDriveSafely
                text:AppStandbyClockModel.naviSupport ? isWideScreen ? TranslationModel.STR_PROFILE_WC_DETAIL_SAFETY_OBEY : TranslationModel.STR_PROFILE_WC_DETAIL_SAFETY_OBEY_8
                                                      : isWideScreen ? TranslationModel.STR_WC_DETAIL_SAFETY_OBEY_IKAV : TranslationModel.STR_WC_DETAIL_SAFETY_OBEY_IKAV_8INCH
                width: (isWideScreen) ? 1330 : 728
                font.pixelSize:39 // AppStandbyClockModel.generalLanguage === APPENUMS.E_LANGUAGE_RU  && !isWideScreen  ? 36: 39
                color: ThemeHelperSTAN.normalTextColor

                anchors.verticalCenter: txtDrive.verticalCenter
                anchors.horizontalCenter: txtDrive.horizontalCenter
                anchors.right: parent.right
                anchors.rightMargin: 46

                horizontalAlignment:    Text.AlignHCenter
                verticalAlignment:      Text.AlignVCenter

                wrapMode: Text.WordWrap
                lineHeightMode: Text.FixedHeight
                lineHeight: 45
            }
        }

        QHMI_ToggleButton {
            id: idButtonLanguage
            width: (parent.width- 34)/2
            height: (isWideScreen)? ConstantModel.BUTTON_CONFIRM_WIDE_HEIGHT : ConstantModel.BUTTON_CONFIRM_HEIGHT
            heightTopMultiple: 1.5
            anchors{
                right: parent.right
                rightMargin: 12
                bottom: parent.bottom
                bottomMargin: 12
            }
            label:          TranslationModel.STR_PROFILE_WC_LANGUAGE
            labelSize:      ConstantModel.FONT_SIZE_39
            labelBold:      false
            focus:          false
            enabled:        AppStandbyClockModel.enableBtn
            onBtnClicked: {
                QML_Handler.qmlSendEvtKey(HMIEVENTS.KEY_EVT_CONFIRMSCREEN_BUTTON_LANGUAGE_CLICKED)
            }
        }

        /* Confirm button */
        QHMI_ToggleButton {
            id: idButtonConfirm
            width: (parent.width- 34)/2
            height: (isWideScreen)? ConstantModel.BUTTON_CONFIRM_WIDE_HEIGHT : ConstantModel.BUTTON_CONFIRM_HEIGHT
            heightTopMultiple: 1.5
            anchors{
                left: parent.left
                leftMargin: 10
                bottom: parent.bottom
                bottomMargin: 12
            }
            label:          TranslationModel.STR_PROFILE_WC_CONFIRM
            labelSize:      ConstantModel.FONT_SIZE_39
            labelBold:      false
            focus:          false //true
            enabled:        AppStandbyClockModel.enableBtn
            onBtnClicked: {
                if(isDriving){
                    if(AppStandbyClockModel.modelProfile.crtDriver !== AppStandbyClockModel.modelProfile.firstDriverID){
                        console.log("[3] isDriving crtDriver<>firstDriverID")
                        QML_Handler.qmlSendEvtKey(HMIEVENTS.KEY_EVT_SHOW_POPUP_DRIVING_LOCKOUT)
                        return
                    }
                }
                if(isCalling){
                    if(AppStandbyClockModel.modelProfile.crtDriver !== AppStandbyClockModel.modelProfile.firstDriverID){
                        console.log("[3] isCalling crtDriver<>firstDriverID")
                        return
                    }
                }

                isPressedConfirm = true
                QML_Handler.qmlSendEvtKey(HMIEVENTS.KEY_EVT_CONFIRMSCREEN_BUTTON_CONFIRM_CLICKED)
            }
        }
    }

    QItem{
        id: userProfileArea
        height: 621
        width: (isWideScreen) ? 452 : 414
        anchors{
            top: bg.top
            left: bg.left
        }

        QHMI_ProfileImage{
            id: drv1
            anchors.top: parent.top
            anchors.topMargin: getDrv1Offset()
            anchors.horizontalCenter: parent.horizontalCenter
            pfImage:AppStandbyClockModel.modelProfile.drv1Image
            itemIndex: 0
            driverName: (AppStandbyClockModel.modelProfile.driver1 !== "") ? AppStandbyClockModel.modelProfile.driver1 :TranslationModel.STR_PROFILE_WC_DRIVER1
            isItemDimmed: isDimmed && !drv1.isFocus
            onButtonRealeased:{
                if(!AppStandbyClockEngine.isTransitionTime())
                {
                    AppStandbyClockEngine.restartTimerGeneral()
                    if(!drv1.isFocus){
                        AppStandbyClockModel.modelProfile.cacheDrv = APPENUMS.E_DRIVER1_PROFILE_ID
                        AppStandbyClockModel.modelProfile.crtDriver = APPENUMS.E_DRIVER1_PROFILE_ID
                        AppStandbyClockModel.sendVcrmWithKey("onFocusChanged",1)
                    }
                    if(drv2.isFocus)drv2.isFocus = false
                    if(guest.isFocus)guest.isFocus = false
                    drv1.isFocus = true
                }
            }
        }
        QHMI_ProfileImage{
            id: drv2
            anchors.top: drv1.top
            anchors.topMargin: getDrv2Offset()
            anchors.horizontalCenter: parent.horizontalCenter
            pfImage: AppStandbyClockModel.modelProfile.drv2Image
            itemIndex: 1
            driverName: (AppStandbyClockModel.modelProfile.driver2 !== "") ? AppStandbyClockModel.modelProfile.driver2 :TranslationModel.STR_PROFILE_WC_DRIVER2
            isItemDimmed: isDimmed && !drv2.isFocus
            onButtonRealeased:{
                if(!AppStandbyClockEngine.isTransitionTime())
                {
                    AppStandbyClockEngine.restartTimerGeneral()
                    if(!drv2.isFocus){
                        AppStandbyClockModel.modelProfile.cacheDrv = APPENUMS.E_DRIVER2_PROFILE_ID
                        AppStandbyClockModel.modelProfile.crtDriver = APPENUMS.E_DRIVER2_PROFILE_ID
                        AppStandbyClockModel.sendVcrmWithKey("onFocusChanged",1)
                    }
                    if(drv1.isFocus)drv1.isFocus = false
                    if(guest.isFocus)guest.isFocus = false
                    drv2.isFocus = true
                }
            }
        }
        QHMI_ProfileImage{
            id: guest
            anchors.top: drv2.top
            anchors.topMargin: getGuestOffset()
            anchors.horizontalCenter: parent.horizontalCenter
            pfImage: "Image04"
            itemIndex: 2
            driverName: TranslationModel.STR_PROFILE_WC_GUEST
            isItemDimmed: isDimmed && !guest.isFocus
            onButtonRealeased:{
                if(!AppStandbyClockEngine.isTransitionTime())
                {
                    AppStandbyClockEngine.restartTimerGeneral()
                    if(!guest.isFocus){
                        AppStandbyClockModel.modelProfile.cacheDrv = APPENUMS.E_GUEST_PROFILE_ID
                        AppStandbyClockModel.modelProfile.crtDriver = APPENUMS.E_GUEST_PROFILE_ID
                        AppStandbyClockModel.sendVcrmWithKey("onFocusChanged",1)
                    }
                    if(drv1.isFocus)drv1.isFocus = false
                    if(drv2.isFocus)drv2.isFocus = false
                    guest.isFocus = true
                }
            }
        }
        Connections{
            target: AppStandbyClockModel
            onConfirmIsStartChanged:{
                isPressedConfirm = true
            }
            onDrivingRestrictionChanged:{
                console.log("[3] drivingRestriction:" + AppStandbyClockModel.drivingRestriction + ",AppID: " + AppStandbyClockModel.appIDFromAppMainFront)
                //10 = AppID_t::eAPP_STANDBY
                if(AppStandbyClockModel.drivingRestriction && (AppStandbyClockModel.appIDFromAppMainFront === 10) && !isPressedConfirm){
                    if(AppStandbyClockModel.modelProfile.firstDriverID !== AppStandbyClockModel.modelProfile.crtDriver){
                        AppStandbyClockModel.modelProfile.cacheDrv = AppStandbyClockModel.modelProfile.firstDriverID
                        AppStandbyClockModel.modelProfile.crtDriver = AppStandbyClockModel.modelProfile.firstDriverID
                        AppStandbyClockModel.sendVcrmWithKey("onFocusChanged", 6)
                        AppStandbyClockModel.sendVcrmWithKey("onForcedFocusRestoration")
                        if(drv1.isFocus)drv1.isFocus = false
                        if(drv2.isFocus)drv2.isFocus = false
                        if(guest.isFocus)guest.isFocus = false
                        switch (AppStandbyClockModel.modelProfile.firstDriverID ){
                        case APPENUMS.E_DRIVER1_PROFILE_ID:
                            drv1.isFocus = true
                            break
                        case APPENUMS.E_DRIVER2_PROFILE_ID:
                            drv2.isFocus = true
                            break
                        default:
                            guest.isFocus = true
                        }
                        //E_ONSID_POPUP_LANGUAGE = 4
                        if(AppStandbyClockModel.currentPopupID == 4)
                        {
                            AppStandbyClockModel.varTempIndexLang = -1;
                            QML_Handler.qmlSendEvtKey(HMIEVENTS.KEY_EVT_POPUP_FEEDBACK_CANCEL)
                        }
                        QML_Handler.qmlSendEvtKey(HMIEVENTS.KEY_EVT_SHOW_POPUP_NOTI_DRIVING_LOCK_FOCUSCHANGE)
                        AppStandbyClockEngine.restartTimerGeneral()
                    }
                }
            }
            onIsCallingChanged:{
                console.log("[3] Calling")
                //10 = AppID_t::eAPP_STANDBY
                if(AppStandbyClockModel.isCalling && (AppStandbyClockModel.appIDFromAppMainFront === 10) && !isPressedConfirm){
                    if(AppStandbyClockModel.modelProfile.firstDriverID !== AppStandbyClockModel.modelProfile.crtDriver){
                        AppStandbyClockModel.modelProfile.cacheDrv = AppStandbyClockModel.modelProfile.firstDriverID
                        AppStandbyClockModel.modelProfile.crtDriver = AppStandbyClockModel.modelProfile.firstDriverID

                        if(drv1.isFocus)drv1.isFocus = false
                        if(drv2.isFocus)drv2.isFocus = false
                        if(guest.isFocus)guest.isFocus = false
                        switch (AppStandbyClockModel.modelProfile.firstDriverID ){
                        case APPENUMS.E_DRIVER1_PROFILE_ID:
                            drv1.isFocus = true
                            break
                        case APPENUMS.E_DRIVER2_PROFILE_ID:
                            drv2.isFocus = true
                            break
                        default:
                            guest.isFocus = true
                        }
                        //E_ONSID_POPUP_LANGUAGE = 4
                        if(AppStandbyClockModel.currentPopupID == 4)
                        {
                            AppStandbyClockModel.varTempIndexLang = -1;
                            QML_Handler.qmlSendEvtKey(HMIEVENTS.KEY_EVT_POPUP_FEEDBACK_CANCEL)
                        }
                        AppStandbyClockEngine.restartTimerGeneral()
                    }
                }
            }
        }
    }
    property bool xong: false
    Connections{
        target: AppStandbyClockModel.modelProfile
        onCrtDriverChanged:{
            if (AppStandbyClockModel.modelProfile.crtDriver === APPENUMS.E_GUEST_PROFILE_ID){
                guest.isFocus = true
                drv1.isFocus = false
                drv2.isFocus = false
            }
            else if (AppStandbyClockModel.modelProfile.crtDriver === APPENUMS.E_DRIVER1_PROFILE_ID){
                drv1.isFocus = true
                guest.isFocus = false
                drv2.isFocus = false
            }
            else if (AppStandbyClockModel.modelProfile.crtDriver === APPENUMS.E_DRIVER2_PROFILE_ID) {
                drv2.isFocus = true
                guest.isFocus = false
                drv1.isFocus = false
            }
        }
        onDriver1Changed:{
            drv1.pfImage = AppStandbyClockModel.modelProfile.drv1Image
        }
        onDriver2Changed:{
            drv2.pfImage = AppStandbyClockModel.modelProfile.drv2Image
        }
    }

    // Observational event catcher. It changes no model state or legal handler;
    // rejection allows lower stacked MouseAreas to remain eligible.
    MouseArea {
        id: vmInputObserver
        anchors.fill: parent
        z: 100000
        hoverEnabled: true
        onEntered: console.log("VM_OBSERVE_INPUT entered", mouseX, mouseY, width, height)
        onExited: console.log("VM_OBSERVE_INPUT exited", mouseX, mouseY)
        onPressed: {
            console.log("VM_OBSERVE_INPUT pressed", mouse.x, mouse.y, width, height)
            mouse.accepted = false
        }
        onClicked: {
            console.log("VM_OBSERVE_INPUT clicked", mouse.x, mouse.y)
            mouse.accepted = false
        }
    }
    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: root.vmObserveConfirm()
    }
    Connections {
        target: idButtonConfirm
        onEnabledChanged: console.log("VM_OBSERVE_CONFIRM enabledChanged", idButtonConfirm.enabled, AppStandbyClockModel.enableBtn)
        onVisibleChanged: console.log("VM_OBSERVE_CONFIRM visibleChanged", idButtonConfirm.visible)
    }
    Component.onCompleted: {
        console.log("[3] -------------------------onCompleted-----")
        root.vmObserveConfirm()
        if (AppStandbyClockModel.modelProfile.crtDriver === APPENUMS.E_GUEST_PROFILE_ID){
            guest.isFocus = true
        }
        else if (AppStandbyClockModel.modelProfile.crtDriver === APPENUMS.E_DRIVER1_PROFILE_ID){
            drv1.isFocus = true
        }
        else if (AppStandbyClockModel.modelProfile.crtDriver === APPENUMS.E_DRIVER2_PROFILE_ID) {
            drv2.isFocus = true
        }
        else if(AppStandbyClockModel.modelProfile.crtDriver === -1){
            if (AppStandbyClockModel.modelProfile.firstDriverID === APPENUMS.E_GUEST_PROFILE_ID){
                guest.isFocus = true
            }
            else if (AppStandbyClockModel.modelProfile.firstDriverID === APPENUMS.E_DRIVER1_PROFILE_ID){
                drv1.isFocus = true
            }
            else if (AppStandbyClockModel.modelProfile.firstDriverID === APPENUMS.E_DRIVER2_PROFILE_ID) {
                drv2.isFocus = true
            }
        }
    }
    function vmObserveConfirm(){
        var p = idButtonConfirm.mapToItem(root, 0, 0)
        console.log("VM_OBSERVE_CONFIRM geometry",
                    "root", root.x, root.y, root.width, root.height,
                    "bg", bg.x, bg.y, bg.width, bg.height,
                    "txt", txtArea.x, txtArea.y, txtArea.width, txtArea.height,
                    "buttonLocal", idButtonConfirm.x, idButtonConfirm.y, idButtonConfirm.width, idButtonConfirm.height,
                    "buttonRoot", p.x, p.y,
                    "enabled", idButtonConfirm.enabled,
                    "modelEnableBtn", AppStandbyClockModel.enableBtn,
                    "visible", idButtonConfirm.visible,
                    "wide", root.isWideScreen,
                    "dimmed", root.isDimmed,
                    "driving", root.isDriving,
                    "calling", root.isCalling,
                    "sysPopup", AppStandbyClockModel.isSysPopupOn,
                    "parent", root.parent ? root.parent.width : -1, root.parent ? root.parent.height : -1,
                    "grandparent", root.parent && root.parent.parent ? root.parent.parent.width : -1,
                                   root.parent && root.parent.parent ? root.parent.parent.height : -1)
    }

    function getDriveSafelyOffset(){
        if(txtDriveSafely.lineCount == 1) return 91
        else return  91 + (txtDriveSafely.lineCount - 1)*45/2
    }

    function getMakeSelectOffset(){
        if(txtMakeselect.lineCount == 1) return 181 + (txtDriveSafely.lineCount - 1)*45
        else return 181 + (txtDriveSafely.lineCount - 1)*45 + (txtMakeselect.lineCount - 1)*45/2
    }

    function getPleaseReadOffset(){
        if(txtPleaseRead.lineCount == 1) return 271 + (txtDriveSafely.lineCount + txtMakeselect.lineCount - 2)*45
        else return  271 + (txtDriveSafely.lineCount + txtMakeselect.lineCount - 2)*45 + (txtPleaseRead.lineCount - 1)*45/2
    }

    function getDrv1Offset(){
        if(drv1.isFocus) return 18
        else return 18
    }
    function getDrv2Offset(){
        if(drv1.isFocus) return 285
        else return 151
    }
    function getGuestOffset(){
        if(drv2.isFocus) return 285
        else return 151
    }
}
