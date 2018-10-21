# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO
from elfin_pp import ElfinPp


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
        _on = self._io.size()
        if _on == 269:
            self._raw__raw_ax25_info = self._io.read_bytes_full()
            _process = ElfinPp()
            self._raw_ax25_info = _process.decode(self._raw__raw_ax25_info)
            io = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = self._root.ElfinTlmData(io, self, self._root)
        else:
            self._raw__raw_ax25_info = self._io.read_bytes_full()
            _process = ElfinPp()
            self._raw_ax25_info = _process.decode(self._raw__raw_ax25_info)
            io = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = self._root.ElfinCmdResponse(io, self, self._root)

    class DestCallsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_dest_callsign = self._io.read_bytes(6)
            self.dest_callsign = KaitaiStream.process_rotate_left(self._raw_dest_callsign, 8 - (1), 1)


    class ElfinCmdResponse(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.elfin_frame_start = self._io.read_u1()
            self.elfin_opcode = self._io.read_u1()
            _on = self.elfin_opcode
            if _on == 48:
                self.cmd_response = self._root.ElfinHskpPacket(self._io, self, self._root)
            self.elfin_fc_crc = self._io.read_u1()
            self.elfin_frame_end = self._io.read_u1()


    class Ax25Hdr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign = self._root.DestCallsign(self._io, self, self._root)
            self.dest_ssid = self._io.read_u1()
            self.src_callsign = self._root.SrcCallsign(self._io, self, self._root)
            self.src_ssid = self._io.read_u1()
            self.ctl = self._io.read_u1()
            self.pid = self._io.read_u1()


    class ElfinTlmData(KaitaiStruct):
        """
        .. seealso::
           Source - https://elfin.igpp.ucla.edu/s/Beacon-Format_v2.xlsx
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.elfin_frame_start = self._io.read_u1()
            self.elfin_beacon_setting = self._io.read_u1()
            self.elfin_status_1_safe_mode = self._io.read_bits_int(1) != 0
            self.elfin_status_1_reserved = self._io.read_bits_int(3)
            self.elfin_status_1_early_orbit = self._io.read_bits_int(4)
            self.elfin_status_2_payload_power = self._io.read_bits_int(1) != 0
            self.elfin_status_2_9v_boost = self._io.read_bits_int(1) != 0
            self.elfin_status_2_bat_htr_allow = self._io.read_bits_int(1) != 0
            self.elfin_status_2_htr_force = self._io.read_bits_int(1) != 0
            self.elfin_status_2_htr_alert = self._io.read_bits_int(1) != 0
            self.elfin_status_2_reserved = self._io.read_bits_int(3)
            self._io.align_to_byte()
            self.elfin_reserved = self._io.read_u1()
            self.elfin_hskp_pwr1_rtcc_year = self._io.read_u1()
            self.elfin_hskp_pwr1_rtcc_month = self._io.read_u1()
            self.elfin_hskp_pwr1_rtcc_day = self._io.read_u1()
            self.elfin_hskp_pwr1_rtcc_hour = self._io.read_u1()
            self.elfin_hskp_pwr1_rtcc_minute = self._io.read_u1()
            self.elfin_hskp_pwr1_rtcc_second = self._io.read_u1()
            self.elfin_hskp_pwr1_adc_data_adc_sa_volt_12 = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_adc_sa_volt_34 = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_adc_sa_volt_56 = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_sa_short_circuit_current = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_bat_2_volt = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_bat_1_volt = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_reg_sa_volt_1 = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_reg_sa_volt_2 = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_reg_sa_volt_3 = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_power_bus_current_1 = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_power_bus_current_2 = self._io.read_u2be()
            self.elfin_hskp_pwr1_bat_mon_1_avg_cur_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_1_temperature_register = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_1_volt_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_1_cur_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_1_acc_curr_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_2_avg_cur_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_2_temperature_register = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_2_volt_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_2_cur_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_2_acc_curr_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bv_mon = self._io.read_u2be()
            self.elfin_hskp_pwr1_tmps_tmp1 = self._io.read_s2be()
            self.elfin_hskp_pwr1_tmps_tmp2 = self._io.read_s2be()
            self.elfin_hskp_pwr1_tmps_tmp3 = self._io.read_s2be()
            self.elfin_hskp_pwr1_tmps_tmp4 = self._io.read_s2be()
            self.elfin_hskp_pwr1_accumulated_curr_bat1_rarc = self._io.read_u1()
            self.elfin_hskp_pwr1_accumulated_curr_bat1_rsrc = self._io.read_u1()
            self.elfin_hskp_pwr1_accumulated_curr_bat2_rarc = self._io.read_u1()
            self.elfin_hskp_pwr1_accumulated_curr_bat2_rsrc = self._io.read_u1()
            self.elfin_hskp_pwr2_rtcc_year = self._io.read_u1()
            self.elfin_hskp_pwr2_rtcc_month = self._io.read_u1()
            self.elfin_hskp_pwr2_rtcc_day = self._io.read_u1()
            self.elfin_hskp_pwr2_rtcc_hour = self._io.read_u1()
            self.elfin_hskp_pwr2_rtcc_minute = self._io.read_u1()
            self.elfin_hskp_pwr2_rtcc_second = self._io.read_u1()
            self.elfin_hskp_pwr2_adc_data_adc_sa_volt_12 = self._io.read_u2be()
            self.elfin_hskp_pwr2_adc_data_adc_sa_volt_34 = self._io.read_u2be()
            self.elfin_hskp_pwr2_adc_data_adc_sa_volt_56 = self._io.read_u2be()
            self.elfin_hskp_pwr2_adc_data_sa_short_circuit_current = self._io.read_u2be()
            self.elfin_hskp_pwr2_adc_data_bat_2_volt = self._io.read_u2be()
            self.elfin_hskp_pwr2_adc_data_bat_1_volt = self._io.read_u2be()
            self.elfin_hskp_pwr2_adc_data_reg_sa_volt_1 = self._io.read_u2be()
            self.elfin_hskp_pwr2_adc_data_reg_sa_volt_2 = self._io.read_u2be()
            self.elfin_hskp_pwr2_adc_data_reg_sa_volt_3 = self._io.read_u2be()
            self.elfin_hskp_pwr2_adc_data_power_bus_current_1 = self._io.read_u2be()
            self.elfin_hskp_pwr2_adc_data_power_bus_current_2 = self._io.read_u2be()
            self.elfin_hskp_pwr2_bat_mon_1_avg_cur_reg = self._io.read_s2be()
            self.elfin_hskp_pwr2_bat_mon_1_temperature_register = self._io.read_s2be()
            self.elfin_hskp_pwr2_bat_mon_1_volt_reg = self._io.read_s2be()
            self.elfin_hskp_pwr2_bat_mon_1_cur_reg = self._io.read_s2be()
            self.elfin_hskp_pwr2_bat_mon_1_acc_curr_reg = self._io.read_s2be()
            self.elfin_hskp_pwr2_bat_mon_2_avg_cur_reg = self._io.read_s2be()
            self.elfin_hskp_pwr2_bat_mon_2_temperature_register = self._io.read_s2be()
            self.elfin_hskp_pwr2_bat_mon_2_volt_reg = self._io.read_s2be()
            self.elfin_hskp_pwr2_bat_mon_2_cur_reg = self._io.read_s2be()
            self.elfin_hskp_pwr2_bat_mon_2_acc_curr_reg = self._io.read_s2be()
            self.elfin_hskp_pwr2_bv_mon = self._io.read_s2be()
            self.elfin_hskp_pwr2_tmps_tmp1 = self._io.read_s2be()
            self.elfin_hskp_pwr2_tmps_tmp2 = self._io.read_s2be()
            self.elfin_hskp_pwr2_tmps_tmp3 = self._io.read_s2be()
            self.elfin_hskp_pwr2_tmps_tmp4 = self._io.read_s2be()
            self.elfin_hskp_pwr2_accumulated_curr_bat1_rarc = self._io.read_u1()
            self.elfin_hskp_pwr2_accumulated_curr_bat1_rsrc = self._io.read_u1()
            self.elfin_hskp_pwr2_accumulated_curr_bat2_rarc = self._io.read_u1()
            self.elfin_hskp_pwr2_accumulated_curr_bat2_rsrc = self._io.read_u1()
            self.elfin_acb_pc_data1_rtcc_year = self._io.read_u1()
            self.elfin_acb_pc_data1_rtcc_month = self._io.read_u1()
            self.elfin_acb_pc_data1_rtcc_day = self._io.read_u1()
            self.elfin_acb_pc_data1_rtcc_hour = self._io.read_u1()
            self.elfin_acb_pc_data1_rtcc_minute = self._io.read_u1()
            self.elfin_acb_pc_data1_rtcc_second = self._io.read_u1()
            self.elfin_acb_pc_data1_acb_mrm_x = self._io.read_s2be()
            self.elfin_acb_pc_data1_acb_mrm_y = self._io.read_s2be()
            self.elfin_acb_pc_data1_acb_mrm_z = self._io.read_s2be()
            self.elfin_acb_pc_data1_ipdu_mrm_x = self._io.read_s2be()
            self.elfin_acb_pc_data1_ipdu_mrm_y = self._io.read_s2be()
            self.elfin_acb_pc_data1_ipdu_mrm_z = self._io.read_s2be()
            self.elfin_acb_pc_data1_tmps_tmp1 = self._io.read_u2be()
            self.elfin_acb_pc_data1_tmps_tmp2 = self._io.read_u2be()
            self.elfin_acb_pc_data1_tmps_tmp3 = self._io.read_u2be()
            self.elfin_acb_pc_data1_tmps_tmp4 = self._io.read_u2be()
            self.elfin_acb_pc_data2_rtcc_year = self._io.read_u1()
            self.elfin_acb_pc_data2_rtcc_month = self._io.read_u1()
            self.elfin_acb_pc_data2_rtcc_day = self._io.read_u1()
            self.elfin_acb_pc_data2_rtcc_hour = self._io.read_u1()
            self.elfin_acb_pc_data2_rtcc_minute = self._io.read_u1()
            self.elfin_acb_pc_data2_rtcc_second = self._io.read_u1()
            self.elfin_acb_pc_data2_acb_mrm_x = self._io.read_s2be()
            self.elfin_acb_pc_data2_acb_mrm_y = self._io.read_s2be()
            self.elfin_acb_pc_data2_acb_mrm_z = self._io.read_s2be()
            self.elfin_acb_pc_data2_ipdu_mrm_x = self._io.read_s2be()
            self.elfin_acb_pc_data2_ipdu_mrm_y = self._io.read_s2be()
            self.elfin_acb_pc_data2_ipdu_mrm_z = self._io.read_s2be()
            self.elfin_acb_pc_data2_tmps_tmp1 = self._io.read_u2be()
            self.elfin_acb_pc_data2_tmps_tmp2 = self._io.read_u2be()
            self.elfin_acb_pc_data2_tmps_tmp3 = self._io.read_u2be()
            self.elfin_acb_pc_data2_tmps_tmp4 = self._io.read_u2be()
            self.elfin_acb_sense_adc_data_current = self._io.read_u2le()
            self.elfin_acb_sense_adc_data_voltage = self._io.read_u2le()
            self.elfin_fc_counters_cmds_recv = self._io.read_u1()
            self.elfin_fc_counters_badcmds_recv = self._io.read_u1()
            self.elfin_fc_counters_badpkts_fm_radio = self._io.read_u1()
            self.elfin_fc_counters_fcpkts_fm_radio = self._io.read_u1()
            self.elfin_fc_counters_errors = self._io.read_u1()
            self.elfin_fc_counters_reboots = self._io.read_u1()
            self.elfin_fc_counters_intrnl_wdttmout = self._io.read_u1()
            self.elfin_fc_counters_brwnouts = self._io.read_u1()
            self.elfin_fc_counters_wdpicrst = self._io.read_u1()
            self.elfin_fc_counters_porst = self._io.read_u1()
            self.elfin_fc_counters_uart1_recvpkts = self._io.read_u1()
            self.elfin_fc_counters_uart1_parseerrs = self._io.read_u1()
            self.elfin_fc_counters_sips_ovcur_evts = self._io.read_u1()
            self.elfin_fc_counters_vu1_on = self._io.read_u1()
            self.elfin_fc_counters_vu1_off = self._io.read_u1()
            self.elfin_fc_counters_vu2_on = self._io.read_u1()
            self.elfin_fc_counters_vu2_off = self._io.read_u1()
            self.elfin_radio_tlm_rssi = self._io.read_u1()
            self.elfin_radio_tlm_bytes_rx = self._io.read_u4be()
            self.elfin_radio_tlm_bytes_tx = self._io.read_u4be()
            self.elfin_radio_cfg_read_radio_palvl = self._io.read_u1()
            self.elfin_errors_error1_day = self._io.read_u1()
            self.elfin_errors_error1_hour = self._io.read_u1()
            self.elfin_errors_error1_minute = self._io.read_u1()
            self.elfin_errors_error1_second = self._io.read_u1()
            self.elfin_errors_error1_error = self._io.read_u1()
            self.elfin_errors_error2_day = self._io.read_u1()
            self.elfin_errors_error2_hour = self._io.read_u1()
            self.elfin_errors_error2_minute = self._io.read_u1()
            self.elfin_errors_error2_second = self._io.read_u1()
            self.elfin_errors_error2_error = self._io.read_u1()
            self.elfin_errors_error3_day = self._io.read_u1()
            self.elfin_errors_error3_hour = self._io.read_u1()
            self.elfin_errors_error3_minute = self._io.read_u1()
            self.elfin_errors_error3_second = self._io.read_u1()
            self.elfin_errors_error3_error = self._io.read_u1()
            self.elfin_errors_error4_day = self._io.read_u1()
            self.elfin_errors_error4_hour = self._io.read_u1()
            self.elfin_errors_error4_minute = self._io.read_u1()
            self.elfin_errors_error4_second = self._io.read_u1()
            self.elfin_errors_error4_error = self._io.read_u1()
            self.elfin_errors_error5_day = self._io.read_u1()
            self.elfin_errors_error5_hour = self._io.read_u1()
            self.elfin_errors_error5_minute = self._io.read_u1()
            self.elfin_errors_error5_second = self._io.read_u1()
            self.elfin_errors_error5_error = self._io.read_u1()
            self.elfin_errors_error6_day = self._io.read_u1()
            self.elfin_errors_error6_hour = self._io.read_u1()
            self.elfin_errors_error6_minute = self._io.read_u1()
            self.elfin_errors_error6_second = self._io.read_u1()
            self.elfin_errors_error6_error = self._io.read_u1()
            self.elfin_errors_error7_day = self._io.read_u1()
            self.elfin_errors_error7_hour = self._io.read_u1()
            self.elfin_errors_error7_minute = self._io.read_u1()
            self.elfin_errors_error7_second = self._io.read_u1()
            self.elfin_errors_error7_error = self._io.read_u1()
            self.elfin_fc_salt = self._io.read_bytes(4)
            self.elfin_fc_crc = self._io.read_u1()
            self.elfin_frame_end = self._io.read_u1()


    class ElfinHskpPacket(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.elfin_hskp_pwr1_rtcc_year = self._io.read_u1()
            self.elfin_hskp_pwr1_rtcc_month = self._io.read_u1()
            self.elfin_hskp_pwr1_rtcc_day = self._io.read_u1()
            self.elfin_hskp_pwr1_rtcc_hour = self._io.read_u1()
            self.elfin_hskp_pwr1_rtcc_minute = self._io.read_u1()
            self.elfin_hskp_pwr1_rtcc_second = self._io.read_u1()
            self.elfin_hskp_pwr1_pwr_board_id = self._io.read_u1()
            self.elfin_hskp_pwr1_adc_data_adc_sa_volt_12 = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_adc_sa_volt_34 = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_adc_sa_volt_56 = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_sa_short_circuit_current = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_bat_2_volt = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_bat_1_volt = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_reg_sa_volt_1 = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_reg_sa_volt_2 = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_reg_sa_volt_3 = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_power_bus_current_1 = self._io.read_u2be()
            self.elfin_hskp_pwr1_adc_data_power_bus_current_2 = self._io.read_u2be()
            self.elfin_hskp_pwr1_bat_mon_1_avg_cur_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_1_temperature_register = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_1_volt_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_1_cur_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_1_acc_curr_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_2_avg_cur_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_2_temperature_register = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_2_volt_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_2_cur_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bat_mon_2_acc_curr_reg = self._io.read_s2be()
            self.elfin_hskp_pwr1_bv_mon = self._io.read_u2be()
            self.elfin_hskp_pwr1_tmps_tmp1 = self._io.read_s2be()
            self.elfin_hskp_pwr1_tmps_tmp2 = self._io.read_s2be()
            self.elfin_hskp_pwr1_tmps_tmp3 = self._io.read_s2be()
            self.elfin_hskp_pwr1_tmps_tmp4 = self._io.read_s2be()
            self.elfin_hskp_pwr1_accumulated_curr_bat1_rsrc = self._io.read_u1()
            self.elfin_hskp_pwr1_accumulated_curr_bat2_rsrc = self._io.read_u1()
            self.elfin_hskp_pwr1_accumulated_curr_bat1_rarc = self._io.read_u1()
            self.elfin_hskp_pwr1_accumulated_curr_bat2_rarc = self._io.read_u1()
            self.elfin_fc_status_safe_mode = self._io.read_bits_int(1) != 0
            self.elfin_fc_status_reserved = self._io.read_bits_int(3)
            self.elfin_fc_status_early_orbit = self._io.read_bits_int(4)


    class SrcCallsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_src_callsign = self._io.read_bytes(6)
            self.src_callsign = KaitaiStream.process_rotate_left(self._raw_src_callsign, 8 - (1), 1)



