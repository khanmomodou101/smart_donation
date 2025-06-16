import frappe
from smart_donation.config import check_payment_status

def get_context(context):
    frappe.clear_cache()
    reference_id = frappe.request.args.get('ref')
    donation = None
    status = None
    is_valid = False

    if reference_id:
        try:
            donation = frappe.get_doc('Donation', {'reference_id': reference_id})
            is_valid = True
            # Logging for debugging
            frappe.logger().debug(f"Checking payment status for donation: {donation.name}")
            frappe.logger().debug(f"Wave session ID: {donation.wave_session_id}")

            payment_status = check_payment_status(donation.wave_session_id)
            frappe.logger().debug(f"Payment status response: {payment_status}")

            if payment_status.get("success") and payment_status.get("payment_status", "").lower() == "succeeded":
                frappe.logger().debug(f"Setting payment status to Paid for donation: {donation.name}")
                donation.db_set('payment_status', 'Paid')
                frappe.db.commit()
                status = 'Paid'
            else:
                frappe.log_error(f"Payment not successful. Status: {payment_status.get('payment_status')}")
                frappe.logger().debug(f"Payment not successful. Status: {payment_status.get('payment_status')}")
                status = payment_status.get("payment_status")
        except Exception as e:
            frappe.log_error(f"Error processing donation: {str(e)}", "Donation Processing Error")
            donation = None
            is_valid = False
    else:
        donation = None
        is_valid = False

    context.reference_id = reference_id
    context.donation = donation
    context.status = status or frappe.db.get_value("Donation", {"reference_id": reference_id}, "payment_status")
    context.is_valid = is_valid
    return context
