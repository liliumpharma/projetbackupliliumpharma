import requests 
import weasyprint as wsp

resp = requests.get('http://localhost:8001/orders/'+str(87))
print("loaded")
img_filepath ='/app/static/share/orders/'+str(87)+'.png'
html_source=resp.text
print("after text")
html = wsp.HTML(string=html_source)
html.write_pdf(img_filepath)