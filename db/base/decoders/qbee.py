# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Qbee(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax_header = self._root.AxHeader(self._io, self, self._root)
        self.csp_header = self._io.read_bytes(4)
        self.beacon_data = self._root.BeaconData(self._io, self, self._root)
        self.rs_parity = self._io.read_bytes(32)

    class AxHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.qbee_destination = (self._io.read_bytes(6)).decode(u"ASCII")
            self.qbee_destination_ssid = self._io.read_u1()
            self.qbee_source = (self._io.read_bytes(6)).decode(u"ASCII")
            self.qbee_source_ssid = self._io.read_u1()
            self.qbee_control = self._io.read_u1()
            self.qbee_pid = self._io.read_u1()


    class QbeeServiceRunning(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.qbee_service_running_adcs = self._io.read_bits_int(1) != 0
            self.qbee_service_running_fipex = self._io.read_bits_int(1) != 0
            self.qbee_service_running_ocobc = self._io.read_bits_int(1) != 0
            self.qbee_service_running_reserved = self._io.read_bits_int(5)


    class QbeePowerInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.qbee_pwr_info_adcs = self._io.read_bits_int(1) != 0
            self.qbee_pwr_info_fipex = self._io.read_bits_int(1) != 0
            self.qbee_pwr_info_gps = self._io.read_bits_int(1) != 0
            self.qbee_pwr_info_ocobc = self._io.read_bits_int(1) != 0
            self.qbee_pwr_info_reserved = self._io.read_bits_int(4)


    class QbeeWod(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.qbee_wod_time = self._io.read_u4le()
            self.qbee_wod_mode = self._io.read_u1()
            self.qbee_wod_voltage_battery = self._io.read_u1()
            self.qbee_wod_current_battery = self._io.read_u1()
            self.qbee_wod_current_3v3 = self._io.read_u1()
            self.qbee_wod_current_5v = self._io.read_u1()
            self.qbee_wod_temperature_comms = self._io.read_u1()
            self.qbee_wod_temperature_eps = self._io.read_u1()
            self.qbee_wod_temperature_battery = self._io.read_u1()


    class QbeeServiceEnabled(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.qbee_service_enabled_adcs = self._io.read_bits_int(1) != 0
            self.qbee_service_enabled_fipex = self._io.read_bits_int(1) != 0
            self.qbee_service_enabled_ocobc = self._io.read_bits_int(1) != 0
            self.qbee_service_enabled_reserved = self._io.read_bits_int(5)


    class BeaconData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.qbee_wod = self._root.QbeeWod(self._io, self, self._root)
            self.qbee_power_info = self._root.QbeePowerInfo(self._io, self, self._root)
            self.qbee_service_enabled = self._root.QbeeServiceEnabled(self._io, self, self._root)
            self.qbee_service_running = self._root.QbeeServiceRunning(self._io, self, self._root)
            self.qbee_reserved = self._io.read_bytes(14)



