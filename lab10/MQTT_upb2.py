from uprotobuf import *


@registerMessage
class MqttmessageMessage(Message):
    _proto_fields=[
        dict(name='clientid', type=WireType.Varint, subType=VarintSubType.UInt32, fieldType=FieldType.Required, id=1),
        dict(name='temp', type=WireType.Varint, subType=VarintSubType.UInt32, fieldType=FieldType.Required, id=2),
        dict(name='time', type=WireType.Varint, subType=VarintSubType.UInt32, fieldType=FieldType.Required, id=3),
    ]
