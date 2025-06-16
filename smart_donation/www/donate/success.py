import frappe
from frappe.utils.print_format import download_pdf
from frappe.utils.pdf import get_pdf
from smart_donation.config import check_payment_status

def get_context(context):
    # Clear cache before processing
    frappe.clear_cache()
    
    reference_id = frappe.request.args.get('ref')
    is_valid = False
    if reference_id:
        try:
            if  frappe.db.exists('Donate', {'reference_id': reference_id}):
                is_valid = True
            
            donation = frappe.get_doc('Donation', {'reference_id': reference_id})
            
            
            # Add logging to debug payment status
            frappe.logger().debug(f"Checking payment status for donation: {donation.name}")
            frappe.logger().debug(f"Wave session ID: {donation.wave_session_id}")
            
            payment_status = check_payment_status(donation.wave_session_id)
            frappe.logger().debug(f"Payment status response: {payment_status}")

            if payment_status.get("success") and payment_status.get("payment_status").lower() == "succeeded":
                frappe.logger().debug(f"Setting payment status to Paid for donation: {donation.name}")
                
                # Update donation status
                donation.db_set('payment_status', 'Paid')
                frappe.db.commit()
                
                frappe.logger().debug("Payment status updated successfully")
               
                
            else:
                frappe.log_error(f"Payment not successful. Status: {payment_status.get('payment_status')}")
                frappe.logger().debug(f"Payment not successful. Status: {payment_status.get('payment_status')}")
        except Exception as e:
            frappe.log_error(f"Error processing donation: {str(e)}", "donation Processing Error")
            donation = None
    else:
        donation = None

    context.is_valid = is_valid
    context.reference_id = reference_id

    return context
