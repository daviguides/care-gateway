from marshmallow import Schema, fields


class ClaimEventSchema(Schema):
    id = fields.Str(required=True)
    claim_id = fields.Int(required=True)
    event_type = fields.Str(required=True)
    details = fields.Str(allow_none=True)
    created_at = fields.DateTime()
