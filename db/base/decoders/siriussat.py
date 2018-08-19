# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Siriussat(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25header = self._io.read_bytes(16)
        self.u_panel1 = self._io.read_u2le()
        self.u_panel2 = self._io.read_u2le()
        self.u_panel3 = self._io.read_u2le()
        self.i_panel1 = self._io.read_u2le()
        self.i_panel2 = self._io.read_u2le()
        self.i_panel3 = self._io.read_u2le()
        self.i_bat = self._io.read_s2le()
        self.i_ch1 = self._io.read_u2le()
        self.i_ch2 = self._io.read_u2le()
        self.i_ch3 = self._io.read_u2le()
        self.i_ch4 = self._io.read_u2le()
        self.t1_pw = self._io.read_s2le()
        self.t2_pw = self._io.read_s2le()
        self.t3_pw = self._io.read_s2le()
        self.t4_pw = self._io.read_s2le()
        self.u_bat_crit = self._io.read_bits_int(1) != 0
        self.u_bat_min = self._io.read_bits_int(1) != 0
        self.heater2_manual = self._io.read_bits_int(1) != 0
        self.heater1_manual = self._io.read_bits_int(1) != 0
        self.heater2_on = self._io.read_bits_int(1) != 0
        self.heater1_on = self._io.read_bits_int(1) != 0
        self.t_bat_max = self._io.read_bits_int(1) != 0
        self.t_bat_min = self._io.read_bits_int(1) != 0
        self.channel_on4 = self._io.read_bits_int(1) != 0
        self.channel_on3 = self._io.read_bits_int(1) != 0
        self.channel_on2 = self._io.read_bits_int(1) != 0
        self.channel_on1 = self._io.read_bits_int(1) != 0
        self.i_ch_limit4 = self._io.read_bits_int(1) != 0
        self.i_ch_limit3 = self._io.read_bits_int(1) != 0
        self.i_ch_limit2 = self._io.read_bits_int(1) != 0
        self.i_ch_limit1 = self._io.read_bits_int(1) != 0
        self.reserved0 = self._io.read_bits_int(7)
        self.charger = self._io.read_bits_int(1) != 0
        self._io.align_to_byte()
        self.reserved1 = self._io.read_u1()
        self.u_bat = self._io.read_s2le()
        self.reg_tel_id = self._io.read_u4le()
        self.pss_time = self._io.read_s4le()
        self.pss_n_reset = self._io.read_u1()
        self.pss_flags = self._io.read_u1()
        self.t_amp = self._io.read_s1()
        self.t_uhf = self._io.read_s1()
        self.rssi_rx = self._io.read_s1()
        self.rssi_idle = self._io.read_s1()
        self.power_forward = self._io.read_s1()
        self.power_reflected = self._io.read_s1()
        self.uhf_n_reset = self._io.read_u1()
        self.uhf_flags = self._io.read_u1()
        self.uhf_time = self._io.read_s4le()
        self.uptime = self._io.read_u4le()
        self.uhf_current = self._io.read_u2le()
        self.uhf_voltage = self._io.read_s2le()



