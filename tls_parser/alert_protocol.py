from __future__ import absolute_import
from __future__ import print_function

import struct
from enum import Enum
from tls_parser.exceptions import NotEnoughData, UnknownTypeByte
import tls_parser.record_protocol
from typing import Tuple


class TlsAlertSeverityByte(Enum):
    WARNING = 0x01
    FATAL = 0x02


class TlsAlertMessage(tls_parser.record_protocol.TlsSubprotocolMessage):

    def __init__(self, alert_severity, alert_description):
        # type: (TlsAlertSeverityByte, int) -> None
        self.alert_severity = alert_severity
        # Right now the description is just stored as an int instead of a TlsAlertDescriptionByte
        self.alert_description = alert_description

    def from_bytes(cls, raw_bytes):
        # type: (bytes) -> Tuple[TlsAlertMessage, int]
        if len(raw_bytes) < 2:
            raise NotEnoughData()

        alert_severity = TlsAlertSeverityByte(struct.unpack('B', raw_bytes[0])[0])
        alert_description = TlsAlertSeverityByte(struct.unpack('B', raw_bytes[1])[0])
        return TlsAlertMessage(alert_severity, alert_description), 2


class TlsAlertRecord(tls_parser.record_protocol.TlsRecord):
    def __init__(self, record_header, alert_message):
        # type: (tls_parser.record_protocol.TlsRecordHeader, TlsAlertMessage) -> None
        super(TlsAlertRecord, self).__init__(record_header, alert_message)

    @classmethod
    def from_bytes(cls, raw_bytes):
        # type: (bytes) -> Tuple[TlsAlertRecord, int]
        header, len_consumed = tls_parser.record_protocol.TlsRecordHeader.from_bytes(raw_bytes)
        remaining_bytes = raw_bytes[len_consumed::]

        if header.type != tls_parser.record_protocol.TlsRecordTypeByte.ALERT:
            raise UnknownTypeByte()

        message, len_consumed_for_message = TlsAlertMessage.from_bytes(remaining_bytes)
        return TlsAlertRecord(header, message), len_consumed + len_consumed_for_message

    def to_bytes(self):
        raise NotImplementedError()