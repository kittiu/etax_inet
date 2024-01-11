# Copyright (c) 2023, Kitti U. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import Case


def execute(filters=None):
	columns = get_columns()
	(data, totals) = get_data(filters)
	report_summary = get_report_summary(totals)
	return columns, data, None, None, report_summary


def get_columns():
	return [
		{
			"label": _("Document ID"),
			"fieldname": "document_id",
			"fieldtype": "Link",
			"options": "INET ETax Document",
			"width": 120,
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 0,
		},
		{
			"label": _("Document Type"),
			"fieldname": "h02_document_name",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Issue Date"),
			"fieldname": "h04_document_issue_dtm",
			"fieldtype": "Date",
			"width": 0,
		},
		{
			"label": _("Document Number"),
			"fieldname": "h03_document_id",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Reference"),
			"fieldname": "h12_buyer_order_assign_id",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Buyer Tax ID"),
			"fieldname": "b04_buyer_tax_id",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Buyer Branch ID"),
			"fieldname": "b05_buyer_branch_id",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Buyer Name"),
			"fieldname": "b02_buyer_name",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Base Amount"),
			"fieldname": "f46_tax_basis_total_amount",
			"fieldtype": "Float",
			"width": 0,
		},
		{
			"label": _("Tax Amount"),
			"fieldname": "f48_tax_total_amount",
			"fieldtype": "Float",
			"width": 0,
		},
		{
			"label": _("Total Amount"),
			"fieldname": "f50_grand_total_amount",
			"fieldtype": "Float",
			"width": 0,
		}
	]


def get_data(filters):
	query = get_document_list_query(filters)
	result = query and query.run(as_dict=True) or []
	total_cols = [
		"f46_tax_basis_total_amount",
		"f48_tax_total_amount",
		"f50_grand_total_amount"
	]
	totals = []
	for c in total_cols:
		totals.append(
			sum([x[c] for x in result])
		)

	if not result:
		return (result, totals)

	group_by_column = {
		"Document List By Type": "h02_document_name",
		"Document List By Buyer": "b02_buyer_name",
		"Document List By Status": "status",
	}
	group_by = group_by_column.get(filters["report_type"])
	if group_by:
		groups = list(set([x[group_by] for x in result]))
		res = []
		for group in groups:
			parent = {"document_id": group, "indent": 0}
			childs = []
			for row in filter(lambda l: l[group_by] == group, result):
				row["indent"] = 1
				childs.append(row)
			for c in total_cols:
				parent[c] = sum([x[c] for x in childs])
			res += [parent] + childs
		result = res

	return (result, totals)


def get_document_list_query(filters):
	status = filters.get("status")	
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	etax_service = filters.get("etax_service")
	document_types = filters.get("document_type")
	name = filters.get("name")
	number = filters.get("number")
	cn_code = "81"

	if not (from_date and to_date):
		return False

	etax_doc = frappe.qb.DocType("INET ETax Document")
	query = (
		frappe.qb.from_(etax_doc)
		.select(
			etax_doc.name.as_("document_id"),
			etax_doc.status.as_("status"),
			etax_doc.h02_document_name.as_("h02_document_name"),
			etax_doc.h04_document_issue_dtm.as_("h04_document_issue_dtm"),
			etax_doc.h03_document_id.as_("h03_document_id"),
			etax_doc.h12_buyer_order_assign_id.as_("h12_buyer_order_assign_id"),
			etax_doc.b04_buyer_tax_id.as_("b04_buyer_tax_id"),
			etax_doc.b05_buyer_branch_id.as_("b05_buyer_branch_id"),
			etax_doc.b02_buyer_name.as_("b02_buyer_name"),
			Case()
			.when(etax_doc.h01_document_type_code == cn_code, -etax_doc.f46_tax_basis_total_amount)
			.else_(etax_doc.f46_tax_basis_total_amount)
			.as_("f46_tax_basis_total_amount"),
			Case()
			.when(etax_doc.h01_document_type_code == cn_code, -etax_doc.f48_tax_total_amount)
			.else_(etax_doc.f48_tax_total_amount)
			.as_("f48_tax_total_amount"),
			Case()
			.when(etax_doc.h01_document_type_code == cn_code, -etax_doc.f50_grand_total_amount)
			.else_(etax_doc.f50_grand_total_amount)
			.as_("f50_grand_total_amount"),
		)
		.where(etax_doc.h04_document_issue_dtm >= filters.get("from_date"))
		.where(etax_doc.h04_document_issue_dtm <= filters.get("to_date"))
		.orderby(etax_doc.h04_document_issue_dtm)
	)
	if status:
		query = query.where(etax_doc.status == status)
	if etax_service:
		(tax_id, branch_id) = etax_service.split("-")
		query = query.where(etax_doc.c01_seller_tax_id == tax_id)
		query = query.where(etax_doc.c02_seller_branch_id == branch_id)
	if document_types:
		query = query.where(etax_doc.h01_document_type_code.isin(document_types))
	if name:
		query = query.where(etax_doc.name == name)
	if number:
		query = query.where(etax_doc.h03_document_id.like(f"%{number}%"))

	return query


def get_report_summary(totals):
	return [
		{
			"value": totals[0],
			"label": _("Total Base Amount"),
			"datatype": "Currency",
			"currency": "THB",
		},
		{
			"value": totals[1],
			"label": _("Total Tax Amount"),
			"datatype": "Currency",
			"currency": "THB",
		},
		{
			"value": totals[2],
			"label": _("Total Amount"),
			"datatype": "Currency",
			"currency": "THB",
		},
	]
