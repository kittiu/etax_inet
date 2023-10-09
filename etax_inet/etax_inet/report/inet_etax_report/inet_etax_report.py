# Copyright (c) 2023, Kitti U. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import Case, CustomFunction


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data, None, None, None


def get_columns():
	return [
		# {
		# 	"label": _("Tax Address"),
		# 	"fieldname": "company_tax_address",
		# 	"fieldtype": "Link",
		# 	"options": "Address",
		# 	"width": 0,
		# },
		# {
		# 	"label": _("Report Date"),
		# 	"fieldname": "report_date",
		# 	"fieldtype": "Date",
		# 	"width": 0,
		# },
		# {
		# 	"label": _("Number"),
		# 	"fieldname": "name",
		# 	"fieldtype": "Data",
		# 	"width": 150,
		# },
		# {
		# 	"label": _("Customer"),
		# 	"fieldname": "party_name",
		# 	"fieldtype": "Data",
		# 	"width": 200,
		# },
		# {
		# 	"label": _("Tax ID"),
		# 	"fieldname": "tax_id",
		# 	"fieldtype": "Data",
		# 	"width": 120,
		# },
		# {
		# 	"label": _("Tax Base"),
		# 	"fieldname": "tax_base",
		# 	"fieldtype": "Currency",
		# 	"options": "Company:company:default_currency",
		# 	"width": 0,
		# },
		# {
		# 	"label": _("Tax Amount"),
		# 	"fieldname": "tax_amount",
		# 	"fieldtype": "Currency",
		# 	"options": "Company:company:default_currency",
		# 	"width": 0,
		# },
		# {
		# 	"label": _("Ref Voucher Type"),
		# 	"fieldname": "voucher_type",
		# 	"fieldtype": "Data",
		# 	"width": 0,
		# },
		# {
		# 	"label": _("Ref Voucher No"),
		# 	"fieldname": "voucher_no",
		# 	"fieldtype": "Dynamic Link",
		# 	"options": "voucher_type",
		# 	"width": 200,
		# },

		{
			"label": _("Document Type"),
			"fieldname": "H02-DOCUMENT_NAME",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Issue Date"),
			"fieldname": "H04-DOCUMENT_ISSUE_DTM",
			"fieldtype": "Date",
			"width": 0,
		},
		{
			"label": _("Document Number"),
			"fieldname": "H03-DOCUMENT_ID",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Buyer Tax ID"),
			"fieldname": "B04-BUYER_TAX_ID",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Buyer Branch ID"),
			"fieldname": "B05-BUYER_Branch_ID",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Buyer Name"),
			"fieldname": "B02-BUYER_NAME",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Base Amount"),
			"fieldname": "F46-TAX_BASIS_TOTAL_AMOUNT",
			"fieldtype": "Currency",
			"options": "Company:company:default_currency",
			"width": 0,
		},
		{
			"label": _("Tax Amount"),
			"fieldname": "F48-TAX_TOTAL_AMOUNT",
			"fieldtype": "Currency",
			"options": "Company:company:default_currency",
			"width": 0,
		},
		{
			"label": _("Total Amount"),
			"fieldname": "F50-GRAND_TOTAL_AMOUNT",
			"fieldtype": "Currency",
			"options": "Company:company:default_currency",
			"width": 0,
		}
	]


def get_data(filters):

	etax_doc = frappe.qb.DocType("INET ETax Document")
	round = CustomFunction("round", ["value", "digit"])
	month = CustomFunction("month", ["date"])
	year = CustomFunction("year", ["date"])
	concat = CustomFunction("concat", ["1", "2"])

	query = (
		frappe.qb.from_(etax_doc)
		# .left_join(cust)
		# .on(cust.name == tinv.party)
		.select(
			etax_doc.h02_document_name.as_("H02-DOCUMENT_NAME"),
			etax_doc.h04_document_issue_dtm.as_("H04-DOCUMENT_ISSUE_DTM"),
			etax_doc.h03_document_id.as_("H03-DOCUMENT_ID"),
			etax_doc.b04_buyer_tax_id.as_("B04-BUYER_TAX_ID"),
			etax_doc.b05_buyer_branch_id.as_("B05-BUYER_BRANCH_ID"),
			etax_doc.b02_buyer_name.as_("B02-BUYER_NAME"),
			etax_doc.f46_tax_basis_total_amount.as_("F46-TAX_BASIS_TOTAL_AMOUNT"),
			etax_doc.f48_tax_total_amount.as_("F48-TAX_TOTAL_AMOUNT"),
			etax_doc.f50_grand_total_amount.as_("F50-GRAND_TOTAL_AMOUNT")

			
			
			


			# tinv.company_tax_address.as_("company_tax_address"),
			# tinv.report_date.as_("report_date"),
			# Case()
			# .when(tinv.docstatus == 1, tinv.name)
			# .else_(concat(tinv.name, " (CANCEL)"))
			# .as_("name"),
			# tinv.party_name.as_("party_name"),
			# cust.tax_id.as_("tax_id"),
			# Case().when(tinv.docstatus == 1, round(tinv.tax_base, 2)).else_(0).as_("tax_base"),
			# Case()
			# .when(tinv.docstatus == 1, round(tinv.tax_amount, 2))
			# .else_(0)
			# .as_("tax_amount"),
			# tinv.voucher_type.as_("voucher_type"),
			# tinv.voucher_no.as_("voucher_no"),
		)
		# .where(
		# 	(tinv.docstatus.isin([1, 2]))
		# 	& (month(tinv.report_date) == filters.get("month"))
		# 	& (year(tinv.report_date) == filters.get("year"))
		# )
		.orderby(etax_doc.h04_document_issue_dtm)
	)

	# if filters.get("company_tax_address"):
	# 	query = query.where(tinv.company_tax_address == filters.get("company_tax_address"))

	result = query.run(as_dict=True)

	return result
