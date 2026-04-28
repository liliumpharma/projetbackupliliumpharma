import sys
import os
import requests

# This tells the script to run independently of Apache
if __name__ == "__main__":
    # 1. Wake up Django from the command line
    sys.path.append('/var/www/server')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
    import django
    django.setup()

    # 2. Import models AFTER Django is awake
    from orders.models import Order
    from django.template.loader import render_to_string
    from weasyprint import HTML

    # 3. Grab the data sent from views.py
    order_id = sys.argv[1]
    raw_phone = sys.argv[2]

    if not raw_phone or raw_phone == "None":
        sys.exit(0)

    # 4. Clean the phone number
    clean_phone = str(raw_phone).replace(" ", "").replace("-", "").replace("+", "")
    if clean_phone.startswith("0"):
        clean_phone = "213" + clean_phone[1:]

    pdf_path = f"/var/www/server/temp_pdfs/temp_order_{order_id}.pdf"

    try:
        # Generate the PDF
        order = Order.objects.get(id=order_id)
        rendered = render_to_string("orders/pdf.html", {"order": order})
        html_doc = HTML(string=rendered, base_url="http://app.liliumpharma.com")
        html_doc.write_pdf(pdf_path)

        # Send it to Node.js
        payload = {
            "number": clean_phone,
            "filePath": pdf_path,
            "message": f"Nouvelle commande n° {order_id} - soumise par {order.user.username} - à transférer à {order.super_gros}",
        }
        requests.post("http://127.0.0.1:3000/send-pdf", json=payload, timeout=30)
        
    except Exception as e:
        # REPLACE 'pass' WITH THESE TWO LINES:
        with open("/var/www/server/whatsapp_debug.log", "a") as f:
            f.write(f"Error on order {order_id}: {str(e)}\n")
    finally:
        # Always clean up the PDF
        if os.path.exists(pdf_path):
            os.remove(pdf_path)