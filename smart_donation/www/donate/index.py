import frappe
from frappe.utils import random_string
from smart_donation.config import initialize_payment
import random

def get_context(context):
    frappe.clear_cache()
    reference_id = frappe.request.args.get('ref')
    is_valid = False
    donation = None

    if reference_id:
        try:
            # Use the correct doctype name consistently
            if frappe.db.exists('Donation', {'reference_id': reference_id}):
                is_valid = True
                donation = frappe.get_doc('Donation', {'reference_id': reference_id})
                # ... (rest of your payment status logic)
            else:
                is_valid = False
        except Exception as e:
            frappe.log_error(f"Error processing donation: {str(e)}", "Donation Processing Error")
            is_valid = False
    else:
        is_valid = False

    context.is_valid = is_valid
    context.reference_id = reference_id
    return context

@frappe.whitelist(allow_guest=True)
def donate():
    try:
        data = frappe.form_dict
        
        donate = frappe.new_doc("Donation")
        reference_id = random_string(40)
        amount = data.get("amount")
        

       
       
        donate.phone = data.get("phone")
        donate.full_name = data.get("full_name")
        donate.amount = amount
        donate.reference_id = reference_id
        
        payment = initialize_payment_for_donation(amount, reference_id)
        if payment.get("success"):
            donate.wave_payment_link = payment.get("wave_launch_url")
            donate.wave_session_id = payment.get("session_id")
            
            # Update Raw Code status to Used
            donate.insert(ignore_permissions=True)
            
            frappe.db.commit()
            return {
                "status": "success",
                "message": "Donation successful",
                "donation_id": donate.name,
                "wave_payment_link": donate.wave_payment_link,
                "reference_id": donate.reference_id
            }
        else:
            return {
                "status": "error",
                "message": "Error in donating"
            }
        
            
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in donating")
        return {
            "status": "error",
            "message": "Error in donating"
        }


    
@frappe.whitelist(allow_guest=True)
def initialize_payment_for_donation(amount, reference_id):
    try:
        success_url = f"https://donation.jokoor.com/donate/success?ref={reference_id}"
        error_url = f"https://donation.jokoor.com/donate/error?ref={reference_id}"
        response = initialize_payment(amount, reference_id, success_url, error_url)
        return response

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in initializing payment for donation")