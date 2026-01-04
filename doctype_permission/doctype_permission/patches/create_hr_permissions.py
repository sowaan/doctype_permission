import frappe

HR_DOCTYPES = [
    "Employee",
    "Salary Slip",
    "Payroll Entry",
    "Leave Application",
    "Attendance",
    "Timesheet",
    "Employee Checkin",
    "Appraisal",
    "Expense Claim",
]


def execute():
    if not frappe.db.table_exists("DocType Permission"):
        return

    for doctype in HR_DOCTYPES:
        try:
            # ✅ Skip if doctype does not exist (HRMS not installed)
            if not frappe.db.exists("DocType", doctype):
                frappe.logger().info(
                    f"[HR PERMISSION BOOTSTRAP] Skipping {doctype} (DocType not installed)"
                )
                continue

            if frappe.db.exists("DocType Permission", {"ref_doctype": doctype}):
                continue

            doc = frappe.get_doc({
                "doctype": "DocType Permission",
                "title": f"HR Permissions for {doctype}",
                "ref_doctype": doctype,
                "testing": 1,
                "conditions": [],
            })

            doc.insert(ignore_permissions=True)

            # if doc.meta.is_submittable:
            #     doc.submit()

        except Exception:
            frappe.log_error(
                title=f"HR Permission Bootstrap Failed for {doctype}",
                message=frappe.get_traceback()
            )

    frappe.cache.delete_value("doctype_permission_map")
