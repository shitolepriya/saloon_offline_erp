# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
from frappe.desk.reportview import get_match_cond
import frappe
import frappe, os, json

@frappe.whitelist()
def get_currency_domination(currency):
	return frappe.db.sql("""select label,value from `tabCurrency Denomination` where parent=%s order by value """,currency, as_dict=1)

@frappe.whitelist()
def get_items(price_list, sales_or_purchase, item=None):
	# company = frappe.db.sql("""select company from `tabUser` where name='%s'"""%(frappe.session.user),as_list=1)
	condition = ""
	order_by = ""
	args = {"price_list": price_list}

	if sales_or_purchase == "Sales":
		# condition = "i.is_sales_item=1 and i.company = '%s'"%(company[0][0])
		condition = "i.is_sales_item=1"
	else:
		condition = "i.is_purchase_item=1"

	if item:
		# search serial no
		item_code = frappe.db.sql("""select name as serial_no, item_code
			from `tabSerial No` where name=%s""", (item), as_dict=1)
		if item_code:
			item_code[0]["name"] = item_code[0]["item_code"]
			return item_code

		# search barcode
		item_code = frappe.db.sql("""select name, item_code from `tabItem`
			where barcode=%s""",
			(item), as_dict=1)
		if item_code:
			item_code[0]["barcode"] = item
			return item_code

		condition += " and ((CONCAT(i.name, i.item_name) like %(name)s) or (i.variant_of like %(name)s) or (i.item_group like %(name)s))"
		order_by = """if(locate(%(_name)s, i.name), locate(%(_name)s, i.name), 99999),
			if(locate(%(_name)s, i.item_name), locate(%(_name)s, i.item_name), 99999),
			if(locate(%(_name)s, i.variant_of), locate(%(_name)s, i.variant_of), 99999),
			if(locate(%(_name)s, i.item_group), locate(%(_name)s, i.item_group), 99999),"""
		args["name"] = "%%%s%%" % frappe.db.escape(item)
		args["_name"] = item.replace("%", "")

	# locate function is used to sort by closest match from the beginning of the value
	return frappe.db.sql("""select i.name, i.item_name, i.image,
		item_det.price_list_rate, item_det.currency
		from `tabItem` i LEFT JOIN
			(select item_code, price_list_rate, currency from
				`tabItem Price`	where price_list=%(price_list)s) item_det
		ON
			(item_det.item_code=i.name or item_det.item_code=i.variant_of)
		where
			ifnull(i.has_variants, 0) = 0 and
			{condition}
		order by
			{order_by}
			i.name """.format(condition=condition, order_by=order_by), args, as_dict=1)

# @frappe.whitelist()
# def get_mobile_no(doctype, txt, searchfield, start, page_len, filters):
# 	get_cont = frappe.db.sql("""select mobile_no, customer from `tabContact` where customer is not null""",as_list=1)
# 	return get_cont

@frappe.whitelist()
def get_customer(mob_no):
	get_cust = frappe.db.sql("""select customer from `tabContact` where mobile_no='%s'"""%(mob_no),as_list=1)
	return get_cust

@frappe.whitelist()
def get_all_employee(doctype, txt, searchfield, start, page_len, filters):
	# company = frappe.db.sql("""select company from `tabUser` where name = '%s'"""%(frappe.session.user),as_list=1)
	#employees = frappe.db.sql("""select name from `tabEmployee` where company = '%s'"""%(company[0][0]),as_list=1)
	#return employees
	emp = frappe.db.sql("""select name, employee_name from `tabEmployee` where employee_name is not 
		null and ({key} like %(txt)s
		or employee_name like %(txt)s)
		{mcond}
		order by
		if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
		if(locate(%(_txt)s, employee_name), locate(%(_txt)s, employee_name), 99999),
		name, employee_name
		limit %(start)s, %(page_len)s""".format(**{
		'key': searchfield,
		'mcond': get_match_cond(doctype)
		}), {
		'txt': "%%%s%%" % txt,
		'_txt': txt.replace("%", ""),
		'start': start,
		'page_len': page_len
	})
	# emp = frappe.db.sql("""select name, employee_name from `tabEmployee` where company = %(com)s and employee_name is not 
	# 	null and ({key} like %(txt)s
	# 	or employee_name like %(txt)s)
	# 	{mcond}
	# 	order by
	# 	if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
	# 	if(locate(%(_txt)s, employee_name), locate(%(_txt)s, employee_name), 99999),
	# 	name, employee_name
	# 	limit %(start)s, %(page_len)s""".format(**{
	# 	'key': searchfield,
	# 	'mcond': get_match_cond(doctype)
	# 	}), {
	# 	'com': company[0][0],
	# 	'txt': "%%%s%%" % txt,
	# 	'_txt': txt.replace("%", ""),
	# 	'start': start,
	# 	'page_len': page_len
	# })
	return emp

@frappe.whitelist()
def get_mobile_no(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select mobile_no, customer from `tabContact` where customer is not null
		and ({key} like %(txt)s
		or mobile_no like %(txt)s)
		{mcond}
		order by
		if(locate(%(_txt)s, mobile_no), locate(%(_txt)s, mobile_no), 99999),
		if(locate(%(_txt)s, customer), locate(%(_txt)s, customer), 99999),
		mobile_no, customer
		limit %(start)s, %(page_len)s""".format(**{
		'key': searchfield,
		'mcond': get_match_cond(doctype)
		}), {
		'txt': "%%%s%%" % txt,
		'_txt': txt.replace("%", ""),
		'start': start,
		'page_len': page_len
	})

@frappe.whitelist()
def service_products(price_list, sales_or_purchase, item=None):
	condition = ""
	order_by = ""
	args = {"price_list": price_list}

	# company = frappe.db.sql("""select company from `tabUser` where name = '%s'"""%(frappe.session.user),as_list=1)

	if sales_or_purchase == "Sales":
		if item == "All":
			# condition = "i.is_sales_item=1 and i.company = '%s'"%(company[0][0])
			condition = "i.is_sales_item=1"
		else:
			condition = "i.is_sales_item=1 and i.item_group = '%s'"%(item)
			# condition = "i.is_sales_item=1 and i.company = '%s' and i.item_group = '%s'"%(company[0][0],item)

	order_by = """if(locate(%(_name)s, i.item_group), locate(%(_name)s, i.item_group), 99999),"""
	args["name"] = "%%%s%%" % frappe.db.escape(item)
	args["_name"] = item.replace("%", "")

	data = frappe.db.sql("""select i.name, i.item_name, i.image,
		item_det.price_list_rate, item_det.currency
		from `tabItem` i LEFT JOIN
			(select item_code, price_list_rate, currency from
				`tabItem Price`	where price_list=%(price_list)s) item_det
		ON
			(item_det.item_code=i.name or item_det.item_code=i.variant_of)
		where
			ifnull(i.has_variants, 0) = 0 and
			{condition}
		order by
			{order_by}
		i.name """.format(condition=condition, order_by=order_by), args, as_dict=1)

	return data

@frappe.whitelist()
def search_categoty(price_list, sales_or_purchase, item=None, category=None, sub_category=None):
	# frappe.errprint("in category")
	condition = ""
	order_by = ""
	args = {"price_list": price_list}

	# company = frappe.db.sql("""select company from `tabUser` where name = '%s'"""%(frappe.session.user),as_list=1)

	if sales_or_purchase == "Sales":
		if item == "All":
			condition = "i.is_sales_item=1 and i.category = '%s'"%(category)
			if category:
				condition = "i.is_sales_item=1 and i.category = '%s'"%(category)
				if sub_category:
					condition = "i.is_sales_item=1 and i.category = '%s' and i.sub_category = '%s' "%(category,sub_category)
				else:
					condition = "i.is_sales_item=1 and i.category = '%s'"%(category)
			else:
				condition = "i.is_sales_item=1"
				if sub_category:
					condition = "i.is_sales_item=1 and i.sub_category = '%s' "%(sub_category)
				else:
					condition = "i.is_sales_item=1"
		else:
			condition = "i.is_sales_item=1 and i.item_group = '%s' and i.category = '%s'"%(item,category)
			if category:
				condition = "i.is_sales_item=1 and i.item_group = '%s' and i.category = '%s'"%(item,category)
				if sub_category:
					condition = "i.is_sales_item=1 and i.item_group = '%s' and i.category = '%s' and i.sub_category = '%s' "%(item,category,sub_category)
				else:
					condition = "i.is_sales_item=1 and i.item_group = '%s' and i.category = '%s'"%(item,category)
			else:
				condition = "i.is_sales_item=1 and i.item_group = '%s'"%(item)
				if sub_category:
					condition = "i.is_sales_item=1 and i.item_group = '%s' and i.sub_category = '%s' "%(item,sub_category)
				else:
					condition = "i.is_sales_item=1 and i.item_group = '%s' "%(item)

	order_by = """if(locate(%(_name)s, i.item_group), locate(%(_name)s, i.item_group), 99999),"""
	args["name"] = "%%%s%%" % frappe.db.escape(item)
	args["_name"] = item.replace("%", "")

	data = frappe.db.sql("""select i.name, i.item_name, i.image,
		item_det.price_list_rate, item_det.currency
		from `tabItem` i LEFT JOIN
			(select item_code, price_list_rate, currency from
				`tabItem Price`	where price_list=%(price_list)s) item_det
		ON
			(item_det.item_code=i.name or item_det.item_code=i.variant_of)
		where
			ifnull(i.has_variants, 0) = 0 and
			{condition}
		order by
			{order_by}
		i.name """.format(condition=condition, order_by=order_by), args, as_dict=1)

	return data


@frappe.whitelist()
def search_sub_categoty(price_list, sales_or_purchase, item=None, category=None, sub_category=None):
	# frappe.errprint("in sub category")
	condition = ""
	order_by = ""
	args = {"price_list": price_list}

	# company = frappe.db.sql("""select company from `tabUser` where name = '%s'"""%(frappe.session.user),as_list=1)

	if sales_or_purchase == "Sales":
		if item=="All":
			if category:
				condition = "i.is_sales_item=1 and i.category = '%s' and i.sub_category = '%s' "%(category,sub_category)
				if sub_category:
					condition = "i.is_sales_item=1 and i.category = '%s' and i.sub_category = '%s' "%(category,sub_category)
				else:
					condition = "i.is_sales_item=1 and i.category = '%s'"%(category)
			else:
				condition = "i.is_sales_item=1 and i.sub_category = '%s' "%(sub_category)
				if sub_category:
					condition = "i.is_sales_item=1 and i.sub_category = '%s' "%(sub_category)
				else:
					condition = "i.is_sales_item=1"
		else:
			if category:
				condition = "i.is_sales_item=1 and i.item_group = '%s'  and i.category = '%s' and i.sub_category = '%s' "%(item,category,sub_category)
				if sub_category:
					condition = "i.is_sales_item=1 and i.item_group = '%s' and i.category = '%s' and i.sub_category = '%s' "%(item,category,sub_category)
				else:
					condition = "i.is_sales_item=1 and i.item_group = '%s' and i.category = '%s'"%(item,category)
			else:
				condition = "i.is_sales_item=1 and i.item_group = '%s' and i.sub_category = '%s' "%(item,sub_category)
				if sub_category:
					condition = "i.is_sales_item=1 and i.item_group = '%s' and i.sub_category = '%s' "%(item,sub_category)
				else:
					condition = "i.is_sales_item=1 and i.item_group = '%s' "%(item)

	order_by = """if(locate(%(_name)s, i.item_group), locate(%(_name)s, i.item_group), 99999),"""
	args["name"] = "%%%s%%" % frappe.db.escape(item)
	args["_name"] = item.replace("%", "")

	data = frappe.db.sql("""select i.name, i.item_name, i.image,
		item_det.price_list_rate, item_det.currency
		from `tabItem` i LEFT JOIN
			(select item_code, price_list_rate, currency from
				`tabItem Price`	where price_list=%(price_list)s) item_det
		ON
			(item_det.item_code=i.name or item_det.item_code=i.variant_of)
		where
			ifnull(i.has_variants, 0) = 0 and
			{condition}
		order by
			{order_by}
		i.name """.format(condition=condition, order_by=order_by), args, as_dict=1)

	return data
