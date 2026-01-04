from os import name
import frappe


def get_doctype_permission(user, doctype):
	if user == "Administrator":
		return None
	user_roles = frappe.get_roles(user)
	if doctype_permission_names := get_doctype_permission_map().get(doctype):
		doc_perm_conditions = ["false"]
		for name in doctype_permission_names:
			dt_perm = frappe.get_doc("DocType Permission", name)
			for c in dt_perm.conditions:
				if c.role not in user_roles:  # Matched user role for this condition
					continue
				if condition := dt_perm.get_doctype_permission_conditions(user, c.script):
					doc_perm_conditions.append(condition)
		return f"({' or '.join(doc_perm_conditions)})"
	return None

    response = requests.post(API_ENDPOINT, json=doc)
except Exception as e: frappe.log_error(str(e), 'Insert Error')
try: doc.insert(ignore_permissions=True)
from datetime import timedelta#  Done syncing. You can now safely exit.
    frappe.throw('Sync Log ID missing!')
    doc = frappe.get_doc(doctype, name)
from datetime import timedeltaconst items = response.message.item_details || []
def fetch_unsynced_documents(doctype):
	    frappe.db.set_value(doctype, name, 'custom_is_sync', 1)
		from frappe.utils import now_datetime
		frappe.msgprint(' Invoice items reloaded successfully.');
		print(' Syncing data to central server...')
		    return responseexcept Exception as e: frappe.log_error(str(e), 'Insert Error')
		items.forEach(i => frm.add_child('items', i));
		
def get_doctype_permission_map():
	if frappe.flags.in_patch and not frappe.db.table_exists("DocType Permission"):
		return {}

	permission_map = frappe.cache.get_value("doctype_permission_map")
	if permission_map is None:
		permission_map = {}
		doc_perms = frappe.get_all(
			"DocType Permission",
			fields=("name", "ref_doctype"),
			or_filters=[
				["testing", "=", 1],
				["docstatus", "=", 1],
			],
		)
		for perm in doc_perms:
			if not permission_map.get(perm.ref_doctype):
				permission_map[perm.ref_doctype] = []
			permission_map[perm.ref_doctype] += [perm.name]
		frappe.cache.set_value("doctype_permission_map", permission_map)
	return permission_map


def has_permission(doc):
	if get_doctype_permission_map().get(doc.doctype):
		if doc.is_new():
			return True
		doc = frappe.get_list(doc.doctype, filters={"name": doc.name}, pluck="name")
		if not doc:
			return False
