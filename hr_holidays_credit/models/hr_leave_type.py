# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.tools.float_utils import float_round


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    allow_credit = fields.Boolean(
        help=(
            "If set to true, employees would be able to make requests for this"
            " leave type even if allocated amount is insufficient."
        ),
    )
    creditable_employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        help="If set, limits credit allowance to specified employees",
    )
    creditable_employee_category_ids = fields.Many2many(
        comodel_name="hr.employee.category",
        help=(
            "If set, limits credit allowance to employees with at least one of"
            " specified tags"
        ),
    )
    creditable_department_ids = fields.Many2many(
        comodel_name="hr.department",
        help=("If set, limits credit allowance to employees of specified departments"),
    )

    def name_get(self):
        context_employee_id = self.env.context.get("employee_id")
        res = []
        for record in self:
            record_name = record.name
            extra = None
            if record.allocation_type != "no" and context_employee_id:
                amount = (
                    float_round(record.virtual_remaining_leaves, precision_digits=2)
                    or 0.0
                )
                if amount >= 0:
                    if record.request_unit == "day":
                        extra = _("%(amount)g day%(suffix)s available%(credit)s") % {
                            "amount": amount,
                            "suffix": "" if abs(amount) <= 1 else "s",
                            "credit": " + credit" if record.allow_credit else "",
                        }
                    elif record.request_unit == "hour":
                        extra = _("%(amount)g hour%(suffix)s available%(credit)s") % {
                            "amount": amount,
                            "suffix": "" if abs(amount) <= 1 else "s",
                            "credit": " + credit" if record.allow_credit else "",
                        }
                else:
                    amount = abs(amount)
                    if record.request_unit == "day":
                        extra = _("%(amount)g day%(suffix)s used in credit") % {
                            "amount": amount,
                            "suffix": "" if abs(amount) <= 1 else "s",
                        }
                    elif record.request_unit == "hour":
                        extra = _("%(amount)g hour%(suffix)s used in credit") % {
                            "amount": amount,
                            "suffix": "" if abs(amount) <= 1 else "s",
                        }
            if extra:
                record_name = _("%(name)s (%(extra)s)") % {
                    "name": record_name,
                    "extra": extra,
                }
            res.append((record.id, record_name))
        return res
