from uprotobuf import *


@registerMessage
class SystemtimeMessage(Message):
    _proto_fields=[
        dict(name='hours', type=WireType.Varint, subType=VarintSubType.UInt32, fieldType=FieldType.Required, id=1),
        dict(name='minutes', type=WireType.Varint, subType=VarintSubType.UInt32, fieldType=FieldType.Required, id=2),
        dict(name='seconds', type=WireType.Varint, subType=VarintSubType.UInt32, fieldType=FieldType.Required, id=3),
    ]

@registerMessage
class MqttmessageMessage(Message):
    _proto_fields=[
        dict(name='temp', type=WireType.Varint, subType=VarintSubType.UInt32, fieldType=FieldType.Required, id=1),
        dict(name='time', type=WireType.Length, subType=LengthSubType.Message, fieldType=FieldType.Required, id=2, mType='.SystemTime'),
    ]
