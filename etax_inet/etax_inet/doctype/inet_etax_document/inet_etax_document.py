# Copyright (c) 2023, Kitti U. and contributors
# For license information, please see license.txt
import json
import requests
import frappe
import base64
from frappe import _
from frappe.model.document import Document


class INETETaxDocument(Document):

	def before_submit(self):
		self.preset_data()  # setup similar data
		# self.set_footer_by_tax_code()
		self.submit_etax()
	
	def preset_data(self):
		# Branch
		self.h22_seller_branch_id = self.c02_seller_branch_id
		# Line count
		self.f01_line_total_count = len(self.line_item_information)
		# Set currency code for footer and lines as in header
		# --
		# def update_cur_fields(doctype, docs, currency):
		# 	for doc in docs:
		# 		meta = frappe.get_meta(doctype)
		# 		fields = filter(
		# 			lambda l: l.fieldname.__contains__("currency_code"),
		# 			meta.fields
		# 		)
		# 		d = {}
		# 		for field in fields:
		# 			d[field.fieldname] = currency
		# 		doc.update(d)
		# update_cur_fields(self.doctype, [self], self.currency)
		# update_cur_fields(self.doctype + " Line", self.line_item_information, self.currency)
		# --

	# def summarize_footer(self):


	def submit_etax(self):
		# Get inet etax setting
		setting = frappe.get_single("INET ETax Settings")
		url = setting.url_etax_sign_document_uat
	
		# Get etax service object
		services = frappe.get_list(
			"INET ETax Service",
			filters={
				"seller_tax_id": self.c01_seller_tax_id,
				"seller_branch_id": self.c02_seller_branch_id,
				"seller_service_user": frappe.session.user
			},
			pluck="name"
		)
		if not services or len(services) > 1:
			frappe.throw(_("The service user %s is not valid for seller %s (%s)") % (
				frappe.session.user,
				self.c01_seller_tax_id,
				self.c02_seller_branch_id
			))
		service = frappe.get_doc("INET ETax Service", services[0])

		# Prepare header
		header = {
			"Content-Type": "application/json",
			"Authorization": service.authorization_code
		}

		# Prepare body
		head_meta = frappe.get_meta(self.doctype)
		line_meta = frappe.get_meta(self.doctype + " Line")
		head_fields = list(filter(
			lambda l: l.fieldtype not in ("Tab Break", "Section Break", "Column Break", "Code")
			and l.fieldname not in (
				"document_type",
				"line_item_information",
				"server_response",
				"transaction_code",
				"error_message",
				"amended_from"),
			head_meta.fields
		))
		line_fields = list(filter(
			lambda l: l.fieldtype not in ("Tab Break", "Section Break", "Column Break"),
			line_meta.fields
		))
		doc_content = {"LINE_ITEM_INFORMATION": []}
		for field in head_fields:
			doc_content[field.label] = get_field_value(self, field)
		for line in self.line_item_information:
			item = {}
			for field in line_fields:
				item[field.label] = get_field_value(line, field)
			doc_content["LINE_ITEM_INFORMATION"].append(item)

		# Get PDF
		html = frappe.get_print(self.doctype, self.name, "Standard", None)
		pdf_content = base64.b64encode(frappe.utils.pdf.get_pdf(html)).decode("utf-8")

		# Prepare json data
		body = {
			"SellerTaxId": service.seller_tax_id,
			"SellerBranchId": service.seller_branch_id,
			"APIKey": service.api_key,
			"UserCode": service.user_code,
			"AccessKey": service.access_key,
			"ServiceCode": service.service_code,
			"PDFContent": pdf_content,
			"TextContent": doc_content,
		}

		# Submit etax and keep the response
		response = requests.post(url=url, headers=header, data=json.dumps(body)).json()
		states = {
			"OK": "Success",
			"ER": "Error",
			"PC": "Processing",
		}
		self.status = states[response.get("status")]
		self.error_code = response.get("errorCode")
		self.error_message = response.get("errorMessage")
		self.transaction_code = response.get("transactionCode")
		self.xml_url = response.get("xmlURL")
		self.pdf_url = response.get("pdfURL")


def get_field_value(doc, field):
	if field.fieldtype == "Int":
		return doc.get(field.fieldname) and str(doc.get(field.fieldname)) or ""
	elif field.fieldtype == "Float":
		return doc.get(field.fieldname) and "{:.2f}".format(doc.get(field.fieldname)) or ""				 
	elif field.fieldtype == "Datetime":
		return doc.get(field.fieldname) and doc.get(field.fieldname).replace(" ", "T") or ""
	else:
		return doc.get(field.fieldname) or ""