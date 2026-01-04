import frappe

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def get_permission_settings():
    """Cached global permission settings"""
    cache_key = "doctype_permission_settings"
    settings = frappe.cache.get_value(cache_key)

    if settings is None:
        settings = {
            "enabled": False,
            "allowed_roles": [],
        }

        if frappe.db.exists("DocType", "DocType Permission Settings"):
            doc = frappe.get_single("DocType Permission Settings")
            settings["enabled"] = bool(doc.enable_doctype_permissions)
            settings["allowed_roles"] = [d.role for d in doc.allowed_roles]

        frappe.cache.set_value(cache_key, settings)

    return settings


def is_user_exempt(user):
    """Check if user should bypass all custom permissions"""
    # if user == "Administrator":
    #     return True

    settings = get_permission_settings()
    if not settings["enabled"]:
        return True

    user_roles = frappe.get_roles(user)
    return any(role in user_roles for role in settings["allowed_roles"])


# ---------------------------------------------------------
# Query Conditions (List / Report / Link)
# ---------------------------------------------------------

def permission_query_conditions(user, doctype):
    if is_user_exempt(user):
        return None

    permission_map = get_doctype_permission_map()
    perm_names = permission_map.get(doctype)

    if not perm_names:
        return None

    user_roles = frappe.get_roles(user)
    conditions = ["0=1"]  # safe false

    for name in perm_names:
        perm = frappe.get_doc("DocType Permission", name)

        for c in perm.conditions:
            if c.role not in user_roles:
                continue

            condition = perm.get_doctype_permission_conditions(user, c.script)
            if condition:
                conditions.append(condition)

    return f"({' OR '.join(conditions)})"


# ---------------------------------------------------------
# Document-level Permission
# ---------------------------------------------------------

def has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user

    if is_user_exempt(user):
        return True

    permission_map = get_doctype_permission_map()
    if doc.doctype not in permission_map:
        return True

    if doc.is_new():
        return True

    exists = frappe.db.exists(doc.doctype, doc.name)
    return bool(exists)


# ---------------------------------------------------------
# Permission Map (Cached)
# ---------------------------------------------------------

def get_doctype_permission_map():
    if frappe.flags.in_patch and not frappe.db.table_exists("DocType Permission"):
        return {}

    cache_key = "doctype_permission_map"
    permission_map = frappe.cache.get_value(cache_key)

    if permission_map is None:
        permission_map = {}

        perms = frappe.get_all(
            "DocType Permission",
			or_filters=[ ["testing", "=", 1], ["docstatus", "=", 1] ],
            fields=["name", "ref_doctype"],
        )

        for p in perms:
            permission_map.setdefault(p.ref_doctype, []).append(p.name)

        frappe.cache.set_value(cache_key, permission_map)

    return permission_map



# def get_doctype_permission(user, doctype):
# 	if user == "Administrator":
# 		return None
# 	user_roles = frappe.get_roles(user)
# 	if doctype_permission_names := get_doctype_permission_map().get(doctype):
# 		doc_perm_conditions = ["false"]
# 		for name in doctype_permission_names:
# 			dt_perm = frappe.get_doc("DocType Permission", name)
# 			for c in dt_perm.conditions:
# 				if c.role not in user_roles:  # Matched user role for this condition
# 					continue
# 				if condition := dt_perm.get_doctype_permission_conditions(user, c.script):
# 					doc_perm_conditions.append(condition)
# 		return f"({' or '.join(doc_perm_conditions)})"
# 	return None


# def get_doctype_permission_map():
# 	if frappe.flags.in_patch and not frappe.db.table_exists("DocType Permission"):
# 		return {}

# 	permission_map = frappe.cache.get_value("doctype_permission_map")
# 	if permission_map is None:
# 		permission_map = {}
# 		doc_perms = frappe.get_all(
# 			"DocType Permission",
# 			fields=("name", "ref_doctype"),
# 			or_filters=[
# 				["testing", "=", 1],
# 				["docstatus", "=", 1],
# 			],
# 		)
# 		for perm in doc_perms:
# 			if not permission_map.get(perm.ref_doctype):
# 				permission_map[perm.ref_doctype] = []
# 			permission_map[perm.ref_doctype] += [perm.name]
# 		frappe.cache.set_value("doctype_permission_map", permission_map)
# 	return permission_map


# def has_permission(doc):
# 	if get_doctype_permission_map().get(doc.doctype):
# 		if doc.is_new():
# 			return True
# 		doc = frappe.get_list(doc.doctype, filters={"name": doc.name}, pluck="name")
# 		if not doc:
# 			return False
