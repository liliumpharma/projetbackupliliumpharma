import os
import threading
import requests
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML

class thread(threading.Thread):
    def __init__(self, order_id, raw_phone):
        threading.Thread.__init__(self)
        self.order_id = order_id
        self.daemon = True
        
        if raw_phone:
            clean_phone = str(raw_phone).replace(" ", "").replace("-", "").replace("+", "")
            if clean_phone.startswith("0"):
                clean_phone = "213" + clean_phone[1:]
            self.admin_phone = clean_phone
        else:
            self.admin_phone = None

    def run(self):
        print(f"🚀 [WHATSAPP] THREAD STARTED FOR ORDER {self.order_id} 🚀")
        
        if not self.admin_phone:
            print(f"❌ [WHATSAPP] Aborting: No valid phone number.")
            return

        from .models import Order
        pdf_path = f"/var/www/server/temp_pdfs/temp_order_{self.order_id}.pdf"
        
        try:
            print(f"⏳ [WHATSAPP] Generating PDF for Order {self.order_id}...")
            order = Order.objects.get(id=self.order_id)
            rendered = render_to_string("orders/pdf.html", {"order": order})
            html_doc = HTML(string=rendered, base_url="http://app.liliumpharma.com")
            html_doc.write_pdf(pdf_path)
            
            print(f"✅ [WHATSAPP] PDF successfully saved to {pdf_path}")

            payload = {
                "number": self.admin_phone,
                "filePath": pdf_path,
                "message": f"Nouvelle commande n° {self.order_id} - soumise par {order.user.username} - à transférer à {order.super_gros}",
            }
            
            print(f"📡 [WHATSAPP] Sending request to Node.js at 127.0.0.1:3000...")
            response = requests.post("http://127.0.0.1:3000/send-pdf", json=payload, timeout=30)
            
            print(f"🎯 [WHATSAPP] Node.js replied with Status: {response.status_code} | Body: {response.text}")
            
        except requests.exceptions.RequestException as req_err:
            print(f"🔥 [WHATSAPP] FAILED TO CONNECT TO NODE.JS: {req_err}")
        except Exception as e:
            print(f"🔥 [WHATSAPP] PYTHON CRASHED: {e}")
        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                print(f"🧹 [WHATSAPP] Cleaned up temporary PDF file.")