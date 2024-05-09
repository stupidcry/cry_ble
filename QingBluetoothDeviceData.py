from bluetooth_sensor_state_data import BluetoothData


class QingBluetoothDeviceData(BluetoothData):
    def __init__(self, bindkey: bytes | None = None) -> None:
        super().__init__()
