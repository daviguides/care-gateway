from marshmallow import Schema, fields


class ClaimSchema(Schema):
    id = fields.Int(required=True)
    reference_id = fields.Str(required=True)
    patient_name = fields.Str(required=True)
    patient_dob = fields.Date()
    claim_amount = fields.Float(required=True)
    imported_from = fields.Str()
    created_at = fields.DateTime()
