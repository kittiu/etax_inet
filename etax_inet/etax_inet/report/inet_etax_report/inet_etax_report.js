// Copyright (c) 2023, Kitti U. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["INET ETax Report"] = {
	filters: [
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: [
				"",
				"Draft",
				"Success",
				"Error",
				"Processing",
				"Replaced",
			],
			default: "Success",
		},
		{
			fieldname: "report_type",
			label: __("Report Type"),
			fieldtype: "Select",
			options: [
				"Document List",
				"Document List By Type",
				"Document List By Buyer",
				"Document List By Status"
			],
			default: "Document List",
		},
		{
			fieldname:"from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "etax_service",
			label: __("Company Tax ID/Branch"),
			fieldtype: "Link",
			options: "INET ETax Service",
		},
		{
			fieldname: "document_type",
			label: __("Document Type"),
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return [
					{"value": "380", "label": "380", "description": "ใบแจ้งหนี้"},
					{"value": "388", "label": "388", "description": "ใบกํากับภาษี"},
					{"value": "T02", "label": "T02", "description": "ใบแจ้งหนี้/ใบกํากับภาษี"},
					{"value": "T03", "label": "T03", "description": "ใบเสร็จรับเงิน/ใบกํากับภาษี"},
					{"value": "T04", "label": "T04", "description": "ใบส่งของ/ใบกํากับภาษี"},
					{"value": "T05", "label": "T05", "description": "ใบกํากับภาษี อย่างย่อ"},
					{"value": "T01", "label": "T01", "description": "ใบรับ (ใบเสร็จรับเงิน)"},
					{"value": "80", "label": "80", "description": "ใบเพิมหนี้"},
					{"value": "81", "label": "81", "description": "ใบลดหนี้"},
				]
			}
		},
		{
			fieldname: "name",
			label: __("Document ID"),
			fieldtype: "Data",
		},
		{
			fieldname: "number",
			label: __("Document Number"),
			fieldtype: "Data",
		},
	],
	"initial_depth": 1,
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "status" && data && data.status == "Draft") {
			value = "<span style='color:gray'>" + value + "</span>";
		}
		else if (column.fieldname == "status" && data && data.status == "Success") {
			value = "<span style='color:green'>" + value + "</span>";
		}
		else if (column.fieldname == "status" && data && data.status == "Error") {
			value = "<span style='color:red'>" + value + "</span>";
		}
		else if (column.fieldname == "status" && data && data.status == "Processing") {
			value = "<span style='color:yellow'>" + value + "</span>";
		}
		else if (column.fieldname == "status" && data && data.status == "Replaced") {
			value = "<span style='color:orange'>" + value + "</span>";
		}

		return value;
	}
};
