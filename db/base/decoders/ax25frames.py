# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Ax25frames(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self._raw_ax25_header = self._io.read_bytes(15)
        io = KaitaiStream(BytesIO(self._raw_ax25_header))
        self.ax25_header = self._root.Hdr(io, self, self._root)
        _on = (self.ax25_header.ctrl & 19)
        if _on == 0:
            self.frametype = self._root.IFrame(self._io, self, self._root)
        elif _on == 3:
            self.frametype = self._root.UiFrame(self._io, self, self._root)
        elif _on == 19:
            self.frametype = self._root.UiFrame(self._io, self, self._root)
        elif _on == 16:
            self.frametype = self._root.IFrame(self._io, self, self._root)
        elif _on == 18:
            self.frametype = self._root.IFrame(self._io, self, self._root)
        elif _on == 2:
            self.frametype = self._root.IFrame(self._io, self, self._root)

    class Hdr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_dest_address = self._io.read_bytes(6)
            self._raw_dest_address = KaitaiStream.process_rotate_left(self._raw__raw_dest_address, 8 - (1), 1)
            io = KaitaiStream(BytesIO(self._raw_dest_address))
            self.dest_address = self._root.DestAddress(io, self, self._root)
            self.u_dest_ssid = self._io.read_u1()
            self._raw__raw_src_address = self._io.read_bytes(6)
            self._raw_src_address = KaitaiStream.process_rotate_left(self._raw__raw_src_address, 8 - (1), 1)
            io = KaitaiStream(BytesIO(self._raw_src_address))
            self.src_address = self._root.SrcAddress(io, self, self._root)
            self.u_src_ssid = self._io.read_u1()
            self.ctrl = self._io.read_u1()

        @property
        def src_ssid(self):
            if hasattr(self, '_m_src_ssid'):
                return self._m_src_ssid if hasattr(self, '_m_src_ssid') else None

            self._m_src_ssid = ((self.u_src_ssid & 15) >> 1)
            return self._m_src_ssid if hasattr(self, '_m_src_ssid') else None

        @property
        def dest_ssid(self):
            if hasattr(self, '_m_dest_ssid'):
                return self._m_dest_ssid if hasattr(self, '_m_dest_ssid') else None

            self._m_dest_ssid = ((self.u_dest_ssid & 15) >> 1)
            return self._m_dest_ssid if hasattr(self, '_m_dest_ssid') else None


    class DestAddress(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_address_str = (self._io.read_bytes(6)).decode(u"ASCII")


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = self._io.read_bytes_full()


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = self._io.read_bytes_full()


    class SrcAddress(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.src_address_str = (self._io.read_bytes(6)).decode(u"ASCII")



