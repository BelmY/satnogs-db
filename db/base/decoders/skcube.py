# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Skcube(KaitaiStruct):
    """
    .. seealso::
       Source - http://www.skcube.sk/wp-content/uploads/2016/06/skcube_data_structures.xlsx
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25header = self._io.read_bytes(16)
        self.packet_type = self._io.read_u1()
        _on = self.packet_type
        if _on == 4:
            self.body = self._root.Block4Cam(self._io, self, self._root)
        elif _on == 6:
            self.body = self._root.Block6Exp(self._io, self, self._root)
        elif _on == 3:
            self.body = self._root.Block3Com(self._io, self, self._root)
        elif _on == 5:
            self.body = self._root.Block5Pwr(self._io, self, self._root)
        elif _on == 2:
            self.body = self._root.Block2Adcs(self._io, self, self._root)
        elif _on == 50:
            self.body = self._root.BlockMessage(self._io, self, self._root)

    class Block5Pwr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = self._io.read_u4le()
            self.fulluptime = self._io.read_u4le()
            self.uptime = self._io.read_u4le()
            self.active_procesor = self._io.read_u2le()
            self.fw_version = self._io.read_u2le()
            self.number_of_reboots = self._io.read_u2le()
            self.countcomerrors = self._io.read_u2le()
            self.countpsuerrors = self._io.read_u2le()
            self.solar_j_current = self._io.read_s2le()
            self.solar_k_current = self._io.read_s2le()
            self.solar_l_current = self._io.read_s2le()
            self.solar_m_current = self._io.read_s2le()
            self.solar_u_current = self._io.read_s2le()
            self.solar_d_current = self._io.read_s2le()
            self.solar_j_temp = self._io.read_s2le()
            self.solar_k_temp = self._io.read_s2le()
            self.solar_l_temp = self._io.read_s2le()
            self.solar_m_temp = self._io.read_s2le()
            self.solar_u_temp = self._io.read_s2le()
            self.solar_d_temp = self._io.read_s2le()
            self.battery_a_voltage = self._io.read_s2le()
            self.battery_b_voltage = self._io.read_s2le()
            self.battery_temp = self._io.read_s2le()
            self.battery_a_capacity = self._io.read_u2le()
            self.battery_b_capacity = self._io.read_u2le()
            self.bat_capacity = self._io.read_u2le()
            self.battery_a_current = self._io.read_s2le()
            self.battery_b_current = self._io.read_s2le()
            self.battery_a_min_current = self._io.read_s2le()
            self.battery_b_min_current = self._io.read_s2le()
            self.battery_a_max_current = self._io.read_s2le()
            self.battery_b_max_current = self._io.read_s2le()
            self.battery_a_avg_current = self._io.read_s2le()
            self.battery_b_avg_current = self._io.read_s2le()
            self.chds_min_current = self._io.read_s2le()
            self.chds_max_current = self._io.read_s2le()
            self.chds_avg_current = self._io.read_s2le()
            self.chds_actual_current = self._io.read_s2le()
            self.com_min_current = self._io.read_s2le()
            self.com_max_current = self._io.read_s2le()
            self.com_avg_current = self._io.read_s2le()
            self.com_actual_current = self._io.read_s2le()
            self.cam_min_current = self._io.read_s2le()
            self.cam_max_current = self._io.read_s2le()
            self.cam_avg_current = self._io.read_s2le()
            self.cam_actual_current = self._io.read_s2le()
            self.exp_min_current = self._io.read_s2le()
            self.exp_max_current = self._io.read_s2le()
            self.exp_avg_current = self._io.read_s2le()
            self.exp_actual_current = self._io.read_s2le()
            self.adcs_min_current = self._io.read_s2le()
            self.adcs_max_current = self._io.read_s2le()
            self.adcs_avg_current = self._io.read_s2le()
            self.adcs_actual_current = self._io.read_s2le()
            self.sys_voltage_min = self._io.read_u2le()
            self.sys_voltage_max = self._io.read_u2le()
            self.sys_voltage_actual = self._io.read_u2le()
            self.nadprudy = self._io.read_u2le()
            self.stav_pripojenia = self._io.read_u2le()
            self.ts_temp = self._io.read_s2le()
            self.countpacket = self._io.read_u4le()
            self.psu_error = self._io.read_u2le()
            self.psu_lasterror = self._io.read_u2le()
            self.com_error = self._io.read_u2le()
            self.com_lasterror = self._io.read_u2le()
            self.cdhs_i_limit = self._io.read_u1()
            self.com_i_limit = self._io.read_u1()
            self.cam_i_limit = self._io.read_u1()
            self.adcs_i_limit = self._io.read_u1()
            self.exp_i_limit = self._io.read_u1()
            self.cam_uv_limit = self._io.read_u1()
            self.exp_uv_limit = self._io.read_u1()
            self.adcs_uv_limit = self._io.read_u1()
            self.bat1_vmax = self._io.read_s2le()
            self.bat1_vmin = self._io.read_s2le()
            self.bat2_vmax = self._io.read_s2le()
            self.bat2_vmin = self._io.read_s2le()
            self.endofdata = self._io.read_u2le()


    class Block2Adcs(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adcs_mode = self._io.read_u1()
            self.bd_k = self._io.read_u1()
            self.max_pwm_coil_x = self._io.read_u1()
            self.max_pwm_coil_y = self._io.read_u1()
            self.max_pwm_coil_z = self._io.read_u1()
            self.sun_x_p_x = self._io.read_s2le()
            self.sun_x_p_y = self._io.read_s2le()
            self.sun_x_p_irradiation = self._io.read_u1()
            self.sun_x_m_x = self._io.read_s2le()
            self.sun_x_m_y = self._io.read_s2le()
            self.sun_x_m_irradiation = self._io.read_u1()
            self.sun_y_p_x = self._io.read_s2le()
            self.sun_y_p_y = self._io.read_s2le()
            self.sun_y_p_irradiation = self._io.read_u1()
            self.sun_y_m_x = self._io.read_s2le()
            self.sun_y_m_y = self._io.read_s2le()
            self.sun_y_m_irradiation = self._io.read_u1()
            self.sun_z_p_x = self._io.read_s2le()
            self.sun_z_p_y = self._io.read_s2le()
            self.sun_z_p_irradiation = self._io.read_u1()
            self.sun_z_m_x = self._io.read_s2le()
            self.sun_z_m_y = self._io.read_s2le()
            self.sun_z_m_irradiation = self._io.read_u1()
            self.gyroscope_x = self._io.read_u2le()
            self.gyroscope_y = self._io.read_u2le()
            self.gyroscope_z = self._io.read_u2le()
            self.gyroscope_temp = self._io.read_u2le()
            self.magnetometer_1_x = self._io.read_u2le()
            self.magnetometer_1_y = self._io.read_u2le()
            self.magnetometer_1_z = self._io.read_u2le()
            self.magnetometer_1_temp = self._io.read_u2le()
            self.magnetometer_2_x = self._io.read_u2le()
            self.magnetometer_2_y = self._io.read_u2le()
            self.magnetometer_2_z = self._io.read_u2le()
            self.magnetometer_2_temp = self._io.read_u2le()
            self.accelerometer_x = self._io.read_u2le()
            self.accelerometer_y = self._io.read_u2le()
            self.accelerometer_z = self._io.read_u2le()
            self.accel_temp = self._io.read_u2le()
            self.earth_sensor_x_p = self._io.read_u2le()
            self.earth_sensor_x_m = self._io.read_u2le()
            self.earth_sensor_y_p = self._io.read_u2le()
            self.earth_sensor_y_m = self._io.read_u2le()


    class Block3Com(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = self._io.read_u4le()
            self.fwversion = self._io.read_u2le()
            self.activecom = self._io.read_u1()
            self.digipeatermode = self._io.read_u1()
            self.noofreboots = self._io.read_u2le()
            self.outputreflpower = self._io.read_u2le()
            self.outputforwardpower = self._io.read_u2le()
            self.outputreflpowercw = self._io.read_u2le()
            self.outputforwardpowercw = self._io.read_u2le()
            self.rssi = self._io.read_u2le()
            self.rssinoise = self._io.read_u2le()
            self.mcutemperature = self._io.read_s1()
            self.patemperature = self._io.read_s1()
            self.cwbeaconsent = self._io.read_u2le()
            self.packetsent = self._io.read_u2le()
            self.correctpacketsreceived = self._io.read_u2le()
            self.brokenpacketsreceived = self._io.read_u2le()
            self.comprotocolerror = self._io.read_u2le()
            self.gsprotocolerror = self._io.read_u2le()
            self.txdisablestatus = self._io.read_u1()
            self.orbittime = self._io.read_u1()
            self.timeslotstart = self._io.read_u1()
            self.timeslotend = self._io.read_u1()


    class Block6Exp(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = self._io.read_u4le()
            self.fw_version = self._io.read_u2le()
            self.number_of_reboots = self._io.read_u2le()
            self.active_adc_channel = self._io.read_u1()
            self.fft_gain = self._io.read_u1()
            self.low_frequency = self._io.read_u1()
            self.high_frequency = self._io.read_u1()
            self.max_hold_sec = self._io.read_u2le()
            self.slow_position = self._io.read_u2le()
            self.postring_samples = self._io.read_u2le()
            self.psd = self._io.read_u2le()
            self.psd_max = self._io.read_u2le()
            self.psd_selected = self._io.read_u2le()
            self.psd_selected_max = self._io.read_u2le()
            self.peak_freq = self._io.read_u2le()
            self.peak_amp = self._io.read_u2le()
            self.psd_treshold = self._io.read_u2le()
            self.psd_selected_events = self._io.read_u2le()
            self.events_position = self._io.read_u1()
            self.event_time_1 = self._io.read_u4le()
            self.event_time_2 = self._io.read_u4le()
            self.event_time_3 = self._io.read_u4le()
            self.event_time_4 = self._io.read_u4le()
            self.event_time_5 = self._io.read_u4le()
            self.event_time_6 = self._io.read_u4le()
            self.event_time_7 = self._io.read_u4le()
            self.event_time_8 = self._io.read_u4le()
            self.event_time_9 = self._io.read_u4le()
            self.event_time_10 = self._io.read_u4le()


    class BlockMessage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.message = (self._io.read_bytes_full()).decode(u"utf-8")


    class Block4Cam(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = self._io.read_u4le()
            self.fw_version = self._io.read_u2le()
            self.number_of_reboots = self._io.read_u2le()
            self.jpeg_compression = self._io.read_u1()
            self.jpeg_scale = self._io.read_u1()
            self.mcu_temperature = self._io.read_s1()
            self.vref_internal = self._io.read_u2le()
            self.packets_sent = self._io.read_u2le()
            self.cw_sent = self._io.read_u2le()
            self.flash_image_position = self._io.read_u1()
            self.tx_datarate = self._io.read_u1()



