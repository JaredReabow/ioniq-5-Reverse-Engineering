mkdir /vm-qml
write work/vm/vendor-userspace-260128/qml-input-override/QHMI_HomeScreenMain_Advanced.qml /vm-qml/QHMI_HomeScreenMain_Advanced.qml
rm /hmi-input-probe.sh
write work/vm/vendor-userspace-260128/hmi-input-probe.sh /hmi-input-probe.sh
sif /hmi-input-probe.sh mode 0100755
