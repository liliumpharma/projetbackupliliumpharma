from django.urls import path
from .views import *

urlpatterns = [
    path("upload-folder/", upload_folder, name="upload_folder"),
    path("upload-file/", upload_file, name="upload_file"),
    path("import-pdfs/", import_pdf_folder, name="import_pdf_folder"),
    path("chatbot/", chatbot, name="chatbot"),  # ✅
]
