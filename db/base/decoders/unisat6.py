#!/usr/bin/env python
from datetime import datetime
from struct import unpack


def find_sync_index(data):
    sync_bytes = bytearray([0x55, 0x53, 0x36])  # U S 6 or 0x55 0x53 0x36
    packet_start_index = bytearray(data).find(sync_bytes)
    return packet_start_index


def decode_payload(payload, observation_datetime, data_id):
    payload = bytearray.fromhex(payload)
    # Find the sync bytes, reframe the packet to start after sync
    sync_offset = find_sync_index(payload)
    if sync_offset == -1:
        raise ValueError('No sync bytes found')
    else:
        payload = payload[sync_offset:len(payload)]

    telemetry = []

    packet_index = unpack('<H', payload[3:3 + 2])[0]
    gnd_index_ack = unpack('<H', payload[5:5 + 2])[0]
    packet_type = unpack('B', payload[7:7 + 1])[0]
    payload_size = unpack('B', payload[8:8 + 1])[0]
    reboot_cnt = unpack('<H', payload[9:9 + 2])[0]
    if (packet_type == 1):
        uptime = unpack('<L', payload[11:11 + 4])[0]  # in ms
        unix_time = unpack('<L', payload[15:15 + 4])[0]  # in s
        temp_mcu = unpack('b', payload[19:19 + 1])[0]  # in C
        temp_fpga = unpack('b', payload[20:20 + 1])[0]  # in C
        magneto_x = unpack('<h', payload[21:21 + 2])[0]  # in ?
        magneto_y = unpack('<h', payload[23:23 + 2])[0]  # in ?
        magneto_z = unpack('<h', payload[25:25 + 2])[0]  # in ?
        gyro_x = unpack('<h', payload[27:27 + 2])[0]  # in ?
        gyro_y = unpack('<h', payload[29:29 + 2])[0]  # in ?
        gyro_z = unpack('<h', payload[31:31 + 2])[0]  # in ?
        i_cpu = unpack('<H', payload[33:33 + 2])[0]  # in ?
        temp_radio = unpack('b', payload[35:35 + 1])[0]  # in C
        payload_reserved_0 = unpack('<H', payload[36:36 + 2])[0]
        temp_bottom = unpack('B', payload[38:38 + 1])[0] * 0.2  # in ?C
        temp_upper = unpack('B', payload[39:39 + 1])[0] * 0.2  # in ?C
        payload_reserved_1 = unpack('B', payload[40:40 + 1])[0]
        eps_vbat = unpack('<H', payload[41:41 + 2])[0]  # in mV
        i_eps_sun = unpack('<H', payload[43:43 + 2])[0]  # in mA
        i_eps_out = unpack('<H', payload[45:45 + 2])[0]  # in mA
        v_eps_panel1 = unpack('<H', payload[47:47 + 2])[0]  # in mV
        v_eps_panel2 = unpack('<H', payload[49:49 + 2])[0]  # in mV
        v_eps_panel3 = unpack('<H', payload[51:51 + 2])[0]  # in mV
        i_eps_panel1 = unpack('<H', payload[53:53 + 2])[0]  # in mA
        i_eps_panel2 = unpack('<H', payload[55:55 + 2])[0]  # in mA
        i_eps_panel3 = unpack('<H', payload[57:57 + 2])[0]  # in mA
        temp_eps_bat = unpack('<H', payload[59:59 + 2])[0]  # in C
        payload_reserved_2 = unpack('B', payload[61:61 + 1])[0]
        sat_error_flag = unpack('<H', payload[62:62 + 2])[0]
        sat_operation_status = unpack('B', payload[64:64 + 1])[0]
        sat_crc = unpack('B', payload[65:65 + 1])[0]

        data = {
            'satellite_datetime': datetime.fromtimestamp(
                int(unix_time)).strftime('%Y-%m-%d %H:%M:%S'),
            'observation_datetime': observation_datetime,
            'data_id': data_id,
            'demod_data': {
                'packet_index': packet_index,
                'gnd_index_ack': gnd_index_ack,
                'packet_type': packet_type,
                'payload_size': payload_size,
                'reboot_cnt': reboot_cnt,
                'uptime': uptime,
                'temp mcu': temp_mcu,
                'temp_fpga': temp_fpga,
                'magneto_x': magneto_x,
                'magneto_y': magneto_y,
                'magneto_z': magneto_z,
                'gyro_x': gyro_x,
                'gyro_y': gyro_y,
                'gyro_z': gyro_z,
                'i_cpu': i_cpu,
                'temp_radio': temp_radio,
                'payload_reserved_0': payload_reserved_0,
                'temp_bottom': temp_bottom,
                'temp_upper': temp_upper,
                'payload_reserved_1': payload_reserved_1,
                'eps_vbat': eps_vbat,
                'i_eps_sun': i_eps_sun,
                'i_eps_out': i_eps_out,
                'v_eps_panel1': v_eps_panel1,
                'v_eps_panel2': v_eps_panel2,
                'v_eps_panel3': v_eps_panel3,
                'i_eps_panel1': i_eps_panel1,
                'i_eps_panel2': i_eps_panel2,
                'i_eps_panel3': i_eps_panel3,
                'temp_eps_bat': temp_eps_bat,
                'payload_reserved_2': payload_reserved_2,
                'sat_error_flag': sat_error_flag,
                'sat_operation_status': sat_operation_status,
                'sat_crc': sat_crc
            }
        }

        telemetry.append(data)
        return telemetry
