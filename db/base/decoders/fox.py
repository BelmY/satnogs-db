# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Fox(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self._raw_fox_raw = self._io.read_bytes_full()
        io = KaitaiStream(BytesIO(self._raw_fox_raw))
        self.fox_raw = self._root.FoxFrame(io, self, self._root)

    class FoxDebugDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.fox_debug_data = self._io.read_bytes_full()


    class FoxMinValsTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.b = []
            i = 0
            while not self._io.is_eof():
                self.b.append(self._io.read_u1())
                i += 1



    class FoxMinValsTlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.fox_min_vals_tlm = self._root.FoxMinValsTlm(self._io, self, self._root)


    class FoxFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_fox_hdr = self._io.read_bytes(6)
            io = KaitaiStream(BytesIO(self._raw_fox_hdr))
            self.fox_hdr = self._root.FoxHdr(io, self, self._root)
            _on = self.fox_hdr.fox_frm_type
            if _on == 0:
                self.fox_frame = self._root.FoxDebugDataT(self._io, self, self._root)
            elif _on == 4:
                self.fox_frame = self._root.FoxExpTlmT(self._io, self, self._root)
            elif _on == 1:
                self.fox_frame = self._root.FoxRtTlmT(self._io, self, self._root)
            elif _on == 3:
                self.fox_frame = self._root.FoxMinValsTlmT(self._io, self, self._root)
            elif _on == 5:
                self.fox_frame = self._root.FoxCamJpegDataT(self._io, self, self._root)
            elif _on == 2:
                self.fox_frame = self._root.FoxMaxValsTlmT(self._io, self, self._root)


    class FoxCamJpegDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.fox_cam_jpeg_data = self._io.read_bytes_full()


    class FoxRtTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.b = []
            i = 0
            while not self._io.is_eof():
                self.b.append(self._io.read_u1())
                i += 1


        @property
        def fox_sat_z_ang_vcty(self):
            if hasattr(self, '_m_fox_sat_z_ang_vcty'):
                return self._m_fox_sat_z_ang_vcty if hasattr(self, '_m_fox_sat_z_ang_vcty') else None

            self._m_fox_sat_z_ang_vcty = ((self.b[44] << 4) | (self.b[43] >> 4))
            return self._m_fox_sat_z_ang_vcty if hasattr(self, '_m_fox_sat_z_ang_vcty') else None

        @property
        def fox_neg_z_panel_v(self):
            if hasattr(self, '_m_fox_neg_z_panel_v'):
                return self._m_fox_neg_z_panel_v if hasattr(self, '_m_fox_neg_z_panel_v') else None

            self._m_fox_neg_z_panel_v = ((self.b[20] << 4) | (self.b[19] >> 4))
            return self._m_fox_neg_z_panel_v if hasattr(self, '_m_fox_neg_z_panel_v') else None

        @property
        def fox_batt_board_temp(self):
            if hasattr(self, '_m_fox_batt_board_temp'):
                return self._m_fox_batt_board_temp if hasattr(self, '_m_fox_batt_board_temp') else None

            self._m_fox_batt_board_temp = ((self.b[11] << 4) | (self.b[10] >> 4))
            return self._m_fox_batt_board_temp if hasattr(self, '_m_fox_batt_board_temp') else None

        @property
        def fox_sys_i2c_fail_ind(self):
            if hasattr(self, '_m_fox_sys_i2c_fail_ind'):
                return self._m_fox_sys_i2c_fail_ind if hasattr(self, '_m_fox_sys_i2c_fail_ind') else None

            self._m_fox_sys_i2c_fail_ind = ((self.b[52] >> 4) & 7)
            return self._m_fox_sys_i2c_fail_ind if hasattr(self, '_m_fox_sys_i2c_fail_ind') else None

        @property
        def fox_batt_a_t(self):
            if hasattr(self, '_m_fox_batt_a_t'):
                return self._m_fox_batt_a_t if hasattr(self, '_m_fox_batt_a_t') else None

            self._m_fox_batt_a_t = ((self.b[5] << 4) | (self.b[4] >> 4))
            return self._m_fox_batt_a_t if hasattr(self, '_m_fox_batt_a_t') else None

        @property
        def fox_neg_y_panel_t(self):
            if hasattr(self, '_m_fox_neg_y_panel_t'):
                return self._m_fox_neg_y_panel_t if hasattr(self, '_m_fox_neg_y_panel_t') else None

            self._m_fox_neg_y_panel_t = ((self.b[26] << 4) | (self.b[25] >> 4))
            return self._m_fox_neg_y_panel_t if hasattr(self, '_m_fox_neg_y_panel_t') else None

        @property
        def fox_batt_b_t(self):
            if hasattr(self, '_m_fox_batt_b_t'):
                return self._m_fox_batt_b_t if hasattr(self, '_m_fox_batt_b_t') else None

            self._m_fox_batt_b_t = (((self.b[7] & 15) << 8) | self.b[6])
            return self._m_fox_batt_b_t if hasattr(self, '_m_fox_batt_b_t') else None

        @property
        def fox_pos_x_panel_t(self):
            if hasattr(self, '_m_fox_pos_x_panel_t'):
                return self._m_fox_pos_x_panel_t if hasattr(self, '_m_fox_pos_x_panel_t') else None

            self._m_fox_pos_x_panel_t = (((self.b[22] & 15) << 8) | self.b[21])
            return self._m_fox_pos_x_panel_t if hasattr(self, '_m_fox_pos_x_panel_t') else None

        @property
        def fox_pos_y_panel_t(self):
            if hasattr(self, '_m_fox_pos_y_panel_t'):
                return self._m_fox_pos_y_panel_t if hasattr(self, '_m_fox_pos_y_panel_t') else None

            self._m_fox_pos_y_panel_t = (((self.b[25] & 15) << 8) | self.b[24])
            return self._m_fox_pos_y_panel_t if hasattr(self, '_m_fox_pos_y_panel_t') else None

        @property
        def fox_batt_c_t(self):
            if hasattr(self, '_m_fox_batt_c_t'):
                return self._m_fox_batt_c_t if hasattr(self, '_m_fox_batt_c_t') else None

            self._m_fox_batt_c_t = ((self.b[8] << 4) | (self.b[7] >> 4))
            return self._m_fox_batt_c_t if hasattr(self, '_m_fox_batt_c_t') else None

        @property
        def fox_neg_x_panel_t(self):
            if hasattr(self, '_m_fox_neg_x_panel_t'):
                return self._m_fox_neg_x_panel_t if hasattr(self, '_m_fox_neg_x_panel_t') else None

            self._m_fox_neg_x_panel_t = ((self.b[23] << 4) | (self.b[22] >> 4))
            return self._m_fox_neg_x_panel_t if hasattr(self, '_m_fox_neg_x_panel_t') else None

        @property
        def fox_rx_temp(self):
            if hasattr(self, '_m_fox_rx_temp'):
                return self._m_fox_rx_temp if hasattr(self, '_m_fox_rx_temp') else None

            self._m_fox_rx_temp = (((self.b[37] & 15) << 8) | self.b[36])
            return self._m_fox_rx_temp if hasattr(self, '_m_fox_rx_temp') else None

        @property
        def fox_exp_fail_ind(self):
            if hasattr(self, '_m_fox_exp_fail_ind'):
                return self._m_fox_exp_fail_ind if hasattr(self, '_m_fox_exp_fail_ind') else None

            self._m_fox_exp_fail_ind = (self.b[52] & 15)
            return self._m_fox_exp_fail_ind if hasattr(self, '_m_fox_exp_fail_ind') else None

        @property
        def fox_batt_a_v(self):
            if hasattr(self, '_m_fox_batt_a_v'):
                return self._m_fox_batt_a_v if hasattr(self, '_m_fox_batt_a_v') else None

            self._m_fox_batt_a_v = (((self.b[1] & 15) << 8) | self.b[0])
            return self._m_fox_batt_a_v if hasattr(self, '_m_fox_batt_a_v') else None

        @property
        def fox_neg_x_panel_v(self):
            if hasattr(self, '_m_fox_neg_x_panel_v'):
                return self._m_fox_neg_x_panel_v if hasattr(self, '_m_fox_neg_x_panel_v') else None

            self._m_fox_neg_x_panel_v = ((self.b[14] << 4) | (self.b[13] >> 4))
            return self._m_fox_neg_x_panel_v if hasattr(self, '_m_fox_neg_x_panel_v') else None

        @property
        def fox_ant_deploy_sensors(self):
            if hasattr(self, '_m_fox_ant_deploy_sensors'):
                return self._m_fox_ant_deploy_sensors if hasattr(self, '_m_fox_ant_deploy_sensors') else None

            self._m_fox_ant_deploy_sensors = ((self.b[53] >> 3) & 3)
            return self._m_fox_ant_deploy_sensors if hasattr(self, '_m_fox_ant_deploy_sensors') else None

        @property
        def fox_psu_curr(self):
            if hasattr(self, '_m_fox_psu_curr'):
                return self._m_fox_psu_curr if hasattr(self, '_m_fox_psu_curr') else None

            self._m_fox_psu_curr = ((self.b[47] << 4) | (self.b[46] >> 4))
            return self._m_fox_psu_curr if hasattr(self, '_m_fox_psu_curr') else None

        @property
        def fox_total_batt_i(self):
            if hasattr(self, '_m_fox_total_batt_i'):
                return self._m_fox_total_batt_i if hasattr(self, '_m_fox_total_batt_i') else None

            self._m_fox_total_batt_i = (((self.b[10] & 15) << 8) | self.b[9])
            return self._m_fox_total_batt_i if hasattr(self, '_m_fox_total_batt_i') else None

        @property
        def fox_neg_z_panel_t(self):
            if hasattr(self, '_m_fox_neg_z_panel_t'):
                return self._m_fox_neg_z_panel_t if hasattr(self, '_m_fox_neg_z_panel_t') else None

            self._m_fox_neg_z_panel_t = ((self.b[29] << 4) | (self.b[28] >> 4))
            return self._m_fox_neg_z_panel_t if hasattr(self, '_m_fox_neg_z_panel_t') else None

        @property
        def fox_pos_z_panel_t(self):
            if hasattr(self, '_m_fox_pos_z_panel_t'):
                return self._m_fox_pos_z_panel_t if hasattr(self, '_m_fox_pos_z_panel_t') else None

            self._m_fox_pos_z_panel_t = (((self.b[28] & 15) << 8) | self.b[27])
            return self._m_fox_pos_z_panel_t if hasattr(self, '_m_fox_pos_z_panel_t') else None

        @property
        def fox_ihu_cpu_temp(self):
            if hasattr(self, '_m_fox_ihu_cpu_temp'):
                return self._m_fox_ihu_cpu_temp if hasattr(self, '_m_fox_ihu_cpu_temp') else None

            self._m_fox_ihu_cpu_temp = (((self.b[40] & 15) << 8) | self.b[39])
            return self._m_fox_ihu_cpu_temp if hasattr(self, '_m_fox_ihu_cpu_temp') else None

        @property
        def fox_grnd_cmded_tlm_rsts(self):
            if hasattr(self, '_m_fox_grnd_cmded_tlm_rsts'):
                return self._m_fox_grnd_cmded_tlm_rsts if hasattr(self, '_m_fox_grnd_cmded_tlm_rsts') else None

            self._m_fox_grnd_cmded_tlm_rsts = ((((self.b[52] >> 7) & 1) | (self.b[53] << 1)) & 15)
            return self._m_fox_grnd_cmded_tlm_rsts if hasattr(self, '_m_fox_grnd_cmded_tlm_rsts') else None

        @property
        def fox_exp_4_temp(self):
            if hasattr(self, '_m_fox_exp_4_temp'):
                return self._m_fox_exp_4_temp if hasattr(self, '_m_fox_exp_4_temp') else None

            self._m_fox_exp_4_temp = (((self.b[46] & 15) << 8) | self.b[45])
            return self._m_fox_exp_4_temp if hasattr(self, '_m_fox_exp_4_temp') else None

        @property
        def fox_ihu_diag_data(self):
            if hasattr(self, '_m_fox_ihu_diag_data'):
                return self._m_fox_ihu_diag_data if hasattr(self, '_m_fox_ihu_diag_data') else None

            self._m_fox_ihu_diag_data = ((((self.b[51] << 24) | (self.b[50] << 16)) | (self.b[49] << 8)) | self.b[48])
            return self._m_fox_ihu_diag_data if hasattr(self, '_m_fox_ihu_diag_data') else None

        @property
        def fox_rssi(self):
            if hasattr(self, '_m_fox_rssi'):
                return self._m_fox_rssi if hasattr(self, '_m_fox_rssi') else None

            self._m_fox_rssi = ((self.b[38] << 4) | (self.b[37] >> 4))
            return self._m_fox_rssi if hasattr(self, '_m_fox_rssi') else None

        @property
        def fox_sat_y_ang_vcty(self):
            if hasattr(self, '_m_fox_sat_y_ang_vcty'):
                return self._m_fox_sat_y_ang_vcty if hasattr(self, '_m_fox_sat_y_ang_vcty') else None

            self._m_fox_sat_y_ang_vcty = (((self.b[43] & 15) << 8) | self.b[42])
            return self._m_fox_sat_y_ang_vcty if hasattr(self, '_m_fox_sat_y_ang_vcty') else None

        @property
        def fox_batt_c_v(self):
            if hasattr(self, '_m_fox_batt_c_v'):
                return self._m_fox_batt_c_v if hasattr(self, '_m_fox_batt_c_v') else None

            self._m_fox_batt_c_v = (((self.b[4] & 15) << 8) | self.b[3])
            return self._m_fox_batt_c_v if hasattr(self, '_m_fox_batt_c_v') else None

        @property
        def fox_tx_pa_curr(self):
            if hasattr(self, '_m_fox_tx_pa_curr'):
                return self._m_fox_tx_pa_curr if hasattr(self, '_m_fox_tx_pa_curr') else None

            self._m_fox_tx_pa_curr = (((self.b[34] & 15) << 8) | self.b[33])
            return self._m_fox_tx_pa_curr if hasattr(self, '_m_fox_tx_pa_curr') else None

        @property
        def fox_neg_y_panel_v(self):
            if hasattr(self, '_m_fox_neg_y_panel_v'):
                return self._m_fox_neg_y_panel_v if hasattr(self, '_m_fox_neg_y_panel_v') else None

            self._m_fox_neg_y_panel_v = ((self.b[17] << 4) | (self.b[16] >> 4))
            return self._m_fox_neg_y_panel_v if hasattr(self, '_m_fox_neg_y_panel_v') else None

        @property
        def fox_pos_z_panel_v(self):
            if hasattr(self, '_m_fox_pos_z_panel_v'):
                return self._m_fox_pos_z_panel_v if hasattr(self, '_m_fox_pos_z_panel_v') else None

            self._m_fox_pos_z_panel_v = (((self.b[19] & 15) << 8) | self.b[18])
            return self._m_fox_pos_z_panel_v if hasattr(self, '_m_fox_pos_z_panel_v') else None

        @property
        def fox_pos_y_panel_v(self):
            if hasattr(self, '_m_fox_pos_y_panel_v'):
                return self._m_fox_pos_y_panel_v if hasattr(self, '_m_fox_pos_y_panel_v') else None

            self._m_fox_pos_y_panel_v = (((self.b[16] & 15) << 8) | self.b[15])
            return self._m_fox_pos_y_panel_v if hasattr(self, '_m_fox_pos_y_panel_v') else None

        @property
        def fox_psu_temp(self):
            if hasattr(self, '_m_fox_psu_temp'):
                return self._m_fox_psu_temp if hasattr(self, '_m_fox_psu_temp') else None

            self._m_fox_psu_temp = (((self.b[31] & 15) << 8) | self.b[30])
            return self._m_fox_psu_temp if hasattr(self, '_m_fox_psu_temp') else None

        @property
        def fox_spin(self):
            if hasattr(self, '_m_fox_spin'):
                return self._m_fox_spin if hasattr(self, '_m_fox_spin') else None

            self._m_fox_spin = ((self.b[32] << 4) | (self.b[31] >> 4))
            return self._m_fox_spin if hasattr(self, '_m_fox_spin') else None

        @property
        def fox_sat_x_ang_vcty(self):
            if hasattr(self, '_m_fox_sat_x_ang_vcty'):
                return self._m_fox_sat_x_ang_vcty if hasattr(self, '_m_fox_sat_x_ang_vcty') else None

            self._m_fox_sat_x_ang_vcty = ((self.b[41] << 4) | (self.b[40] >> 4))
            return self._m_fox_sat_x_ang_vcty if hasattr(self, '_m_fox_sat_x_ang_vcty') else None

        @property
        def fox_batt_b_v(self):
            if hasattr(self, '_m_fox_batt_b_v'):
                return self._m_fox_batt_b_v if hasattr(self, '_m_fox_batt_b_v') else None

            self._m_fox_batt_b_v = ((self.b[2] << 4) | (self.b[1] >> 4))
            return self._m_fox_batt_b_v if hasattr(self, '_m_fox_batt_b_v') else None

        @property
        def fox_pos_x_panel_v(self):
            if hasattr(self, '_m_fox_pos_x_panel_v'):
                return self._m_fox_pos_x_panel_v if hasattr(self, '_m_fox_pos_x_panel_v') else None

            self._m_fox_pos_x_panel_v = (((self.b[13] & 15) << 8) | self.b[12])
            return self._m_fox_pos_x_panel_v if hasattr(self, '_m_fox_pos_x_panel_v') else None

        @property
        def fox_tx_temp(self):
            if hasattr(self, '_m_fox_tx_temp'):
                return self._m_fox_tx_temp if hasattr(self, '_m_fox_tx_temp') else None

            self._m_fox_tx_temp = ((self.b[35] << 4) | (self.b[34] >> 4))
            return self._m_fox_tx_temp if hasattr(self, '_m_fox_tx_temp') else None


    class FoxHdr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.b = [None] * (6)
            for i in range(6):
                self.b[i] = self._io.read_u1()


        @property
        def fox_id(self):
            if hasattr(self, '_m_fox_id'):
                return self._m_fox_id if hasattr(self, '_m_fox_id') else None

            self._m_fox_id = (self.b[0] & 7)
            return self._m_fox_id if hasattr(self, '_m_fox_id') else None

        @property
        def fox_reset_count(self):
            if hasattr(self, '_m_fox_reset_count'):
                return self._m_fox_reset_count if hasattr(self, '_m_fox_reset_count') else None

            self._m_fox_reset_count = (((((self.b[2] << 16) | (self.b[1] << 8)) | self.b[0]) >> 3) & 65535)
            return self._m_fox_reset_count if hasattr(self, '_m_fox_reset_count') else None

        @property
        def fox_uptime(self):
            if hasattr(self, '_m_fox_uptime'):
                return self._m_fox_uptime if hasattr(self, '_m_fox_uptime') else None

            self._m_fox_uptime = ((((((self.b[5] << 24) | (self.b[4] << 16)) | (self.b[3] << 8)) | self.b[2]) >> 3) & 33554431)
            return self._m_fox_uptime if hasattr(self, '_m_fox_uptime') else None

        @property
        def fox_frm_type(self):
            if hasattr(self, '_m_fox_frm_type'):
                return self._m_fox_frm_type if hasattr(self, '_m_fox_frm_type') else None

            self._m_fox_frm_type = ((self.b[5] >> 4) & 15)
            return self._m_fox_frm_type if hasattr(self, '_m_fox_frm_type') else None


    class FoxMaxValsTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.b = []
            i = 0
            while not self._io.is_eof():
                self.b.append(self._io.read_u1())
                i += 1



    class FoxExpTlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.fox_exp_tlm = self._io.read_bytes_full()


    class FoxRtTlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.fox_rt_tlm = self._root.FoxRtTlm(self._io, self, self._root)


    class FoxMaxValsTlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.fox_max_vals_tlm = self._root.FoxMaxValsTlm(self._io, self, self._root)



