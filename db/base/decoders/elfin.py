# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Elfin(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self._raw_ax25_header = self._io.read_bytes(16)
        io = KaitaiStream(BytesIO(self._raw_ax25_header))
        self.ax25_header = self._root.Ax25Hdr(io, self, self._root)
        self.ax25_info = self._root.ElfinTlmData(self._io, self, self._root)

    class BvMon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bus_voltage = self._root.BusVoltage(self._io, self, self._root)


    class Volt(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.voltage = self._io.read_u2be()


    class BatVolt(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.voltage = self._io.read_u2be()


    class Curr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.current = self._io.read_u2be()


    class AcbSense(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.acb_current = self._io.read_u2be()
            self.acb_voltage = self._io.read_u2be()


    class SaVolt(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.voltage = self._io.read_u2be()


    class HskpPwr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rtcc = self._root.BcdDate(self._io, self, self._root)
            self.adc_data = self._root.AdcData(self._io, self, self._root)
            self.bat_mon_1 = self._root.BatMon(self._io, self, self._root)
            self.bat_mon_2 = self._root.BatMon(self._io, self, self._root)
            self.bv_mon = self._root.BvMon(self._io, self, self._root)
            self.tmps = self._root.Tmps(self._io, self, self._root)
            self.accumulated_curr = self._root.AcuCurr(self._io, self, self._root)


    class FcCounters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cmds_rxed = self._io.read_u1()
            self.bad_cmds_rxed = self._io.read_u1()
            self.bad_pkts_fm_radio = self._io.read_u1()
            self.fc_pkts_fm_radio = self._io.read_u1()
            self.errors = self._io.read_u1()
            self.reboots = self._io.read_u1()
            self.int_wdt_timeout = self._io.read_u1()
            self.brownouts = self._io.read_u1()
            self.wd_pic_resets = self._io.read_u1()
            self.pwr_on_resets = self._io.read_u1()
            self.uart1_resets = self._io.read_u1()
            self.uart1_parse_errors = self._io.read_u1()
            self.sips_overcur_evts = self._io.read_u1()
            self.vu1_on = self._io.read_u1()
            self.vu1_off = self._io.read_u1()
            self.vu2_on = self._io.read_u1()
            self.vu2_off = self._io.read_u1()


    class AcbPcData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.acb_pc_data_rtcc = self._root.BcdDate(self._io, self, self._root)
            self.acb_pc_data_acb_mrm = self._root.MrmXyz(self._io, self, self._root)
            self.acb_pc_data_ipdu_mrm = self._root.MrmXyz(self._io, self, self._root)
            self.acb_pc_data_tmps = self._root.Tmps(self._io, self, self._root)


    class MrmXyz(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mrm_x = self._io.read_u2be()
            self.mrm_y = self._io.read_u2be()
            self.mrm_z = self._io.read_u2be()


    class Errors(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.error_1 = self._root.TimestampedError(self._io, self, self._root)
            self.error_2 = self._root.TimestampedError(self._io, self, self._root)
            self.error_3 = self._root.TimestampedError(self._io, self, self._root)
            self.error_4 = self._root.TimestampedError(self._io, self, self._root)
            self.error_5 = self._root.TimestampedError(self._io, self, self._root)
            self.error_6 = self._root.TimestampedError(self._io, self, self._root)
            self.error_7 = self._root.TimestampedError(self._io, self, self._root)


    class AdcData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc_sa_volt_12 = self._root.SaVolt(self._io, self, self._root)
            self.adc_sa_volt_34 = self._root.SaVolt(self._io, self, self._root)
            self.adc_sa_volt_56 = self._root.SaVolt(self._io, self, self._root)
            self.sa_short_circuit_current = self._root.SaCurrent(self._io, self, self._root)
            self.bat_2_volt = self._root.BatVolt(self._io, self, self._root)
            self.bat_1_volt = self._root.BatVolt(self._io, self, self._root)
            self.reg_sa_volt_1 = self._root.SaVolt(self._io, self, self._root)
            self.reg_sa_volt_2 = self._root.SaVolt(self._io, self, self._root)
            self.reg_sa_volt_3 = self._root.SaVolt(self._io, self, self._root)
            self.power_bus_current_1 = self._root.PbusCur(self._io, self, self._root)
            self.power_bus_current_2 = self._root.PbusCur(self._io, self, self._root)


    class Ax25Hdr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            self.dest_ssid = self._io.read_u1()
            self.src_callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            self.src_ssid = self._io.read_u1()
            self.ctl = self._io.read_u1()
            self.pid = self._io.read_u1()


    class RadioTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rssi = self._io.read_u1()
            self.bytes_rx = self._io.read_u4be()
            self.bytes_tx = self._io.read_u4be()


    class RadioCfgRead(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.radio_pa_lvl = self._io.read_u1()


    class PbusCur(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.current = self._io.read_u2be()


    class ElfinTlmData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.frame_start = self._io.read_u1()
            self.beacon_setting = self._io.read_u1()
            self.status_1 = self._io.read_u1()
            self.status_2 = self._io.read_u1()
            self.reserved = self._io.read_u1()
            self.hskp_pwr_1 = self._root.HskpPwr(self._io, self, self._root)
            self.hskp_pwr_2 = self._root.HskpPwr(self._io, self, self._root)
            self.acb_pc_data = self._root.AcbPcData(self._io, self, self._root)
            self.acb_pc_data_2 = self._root.AcbPcData2(self._io, self, self._root)
            self.acb_sense = self._root.AcbSense(self._io, self, self._root)
            self.fc_counters = self._root.FcCounters(self._io, self, self._root)
            self.radio_tlm = self._root.RadioTlm(self._io, self, self._root)
            self.radio_cfg_read = self._root.RadioCfgRead(self._io, self, self._root)
            self.errors = self._root.Errors(self._io, self, self._root)
            self.fc_salt = (self._io.read_bytes(4)).decode(u"ASCII")
            self.fc_crc = self._io.read_u1()
            self.frame_end = self._io.read_u1()


    class BcdClk(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.day = self._io.read_u1()
            self.hour = self._io.read_u1()
            self.minute = self._io.read_u1()
            self.second = self._io.read_u1()


    class BusVoltage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.voltage = self._io.read_u2be()


    class Temp(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.temperature = self._io.read_u2be()


    class Tmps(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tmp_1 = self._io.read_u2be()
            self.tmp_2 = self._io.read_u2be()
            self.tmp_3 = self._io.read_u2be()
            self.tmp_4 = self._io.read_u2be()


    class TimestampedError(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.e_time = self._root.BcdClk(self._io, self, self._root)
            self.errno = self._io.read_u1()


    class BcdDate(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.year = self._io.read_u1()
            self.month = self._io.read_u1()
            self.day = self._io.read_u1()
            self.hour = self._io.read_u1()
            self.minute = self._io.read_u1()
            self.second = self._io.read_u1()


    class BatMon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.avg_cur_reg = self._io.read_u2be()
            self.temperature_register = self._io.read_u2be()
            self.volt_reg = self._io.read_u2be()
            self.cur_reg = self._io.read_u2be()
            self.acc_curr_reg = self._io.read_u2be()


    class SaCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.current = self._io.read_u2be()


    class AcuCurr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bat_1_rarc = self._io.read_u1()
            self.bat_1_rsrc = self._io.read_u1()
            self.bat_2_rarc = self._io.read_u1()
            self.bat_2_rsrc = self._io.read_u1()


    class AcbPcData2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rtcc = self._root.BcdDate(self._io, self, self._root)
            self.mrm_a = self._root.MrmXyz(self._io, self, self._root)
            self.mrm_b = self._root.MrmXyz(self._io, self, self._root)
            self.tmps = self._root.Tmps(self._io, self, self._root)


    class AvgCur(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.current = self._io.read_u2be()



