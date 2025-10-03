from django.shortcuts import render

from accounts.models import UserProfile
from .models import Downloadable
from django.db.models import Q
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication,
)
from rest_framework.response import Response
from .serializers import DownloadableSerializer

# TESTING
import os
import zipfile
from django.shortcuts import render
from django.core.files.base import ContentFile
from .forms import UploadFolderForm
from .models import Downloadable, User
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .serializers import DownloadableSerializer
from .models import Downloadable

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .serializers import DownloadableSerializer
from .models import Downloadable


class DownloadsAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Fetch objects filtered by user
        queryset = Downloadable.objects.filter(Q(users=request.user))

        # Custom sorting by name after fetching the queryset
        sorted_queryset = sorted(queryset, key=lambda obj: obj.link_name.lower())

        serializer = DownloadableSerializer(sorted_queryset, many=True)
        return Response(serializer.data, status=200)




def HomeDownloads(request):
    return render(
        request,
        "downloads/index.html",
        {
            # "downloads":Downloadable.objects.filter(Q(users__isnull=True) | Q(users=request.user))
            "downloads": Downloadable.objects.filter(Q(users=request.user))
        },
    )


def upload_file(request):
    # if request.method == 'POST':
    #     return HttpResponse("Form submitted successfully!")
    # else:
    return render(request, "downloads/upload_folder.html", {"form": UploadFolderForm()})


import os
import zipfile
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.conf import settings
from .forms import UploadFolderForm
from .models import Downloadable
from django.contrib.auth.models import User

# def upload_folder(request):
#     if request.method == 'POST':
#         form = UploadFolderForm(request.POST, request.FILES)
#         if form.is_valid():
#             folder = request.FILES['folder']
#             # Extraire le nom du dossier de l'archive zip
#             folder_name = os.path.splitext(os.path.basename(folder.name))[0]

#             with zipfile.ZipFile(folder) as z:
#                 for filename in z.namelist():
#                     if filename.endswith('.pdf'):
#                         # Assurez-vous que le nom de fichier est sécurisé
#                         safe_filename = os.path.basename(filename)
#                         username = os.path.splitext(safe_filename)[0]
#                         try:
#                             user = User.objects.get(username=username)
#                             pdf_file = z.open(filename)

#                             # Créez un chemin sécurisé pour le fichier temporaire
#                             temp_file_path = os.path.join(settings.MEDIA_ROOT, 'downloadable', safe_filename)
#                             os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

#                             # Écrire le fichier temporairement
#                             with open(temp_file_path, 'wb') as temp_file:
#                                 temp_file.write(pdf_file.read())

#                             # Utilisez `ContentFile` pour créer un objet Django File
#                             with open(temp_file_path, 'rb') as f:
#                                 content = ContentFile(f.read(), name=safe_filename)

#                                 # Formater le nom du lien
#                                 link_name = f"BULLETIN DE PAIE {folder_name}"

#                                 downloadable = Downloadable.objects.create(
#                                     attachement=content,
#                                     link_name=link_name,
#                                 )
#                                 downloadable.users.add(user)

#                             # Nettoyez le fichier temporaire
#                             os.remove(temp_file_path)

#                         except User.DoesNotExist:
#                             print(f"User with username {username} does not exist.")

#             return render(request, 'downloads/upload_success.html')
#     else:
#         form = UploadFolderForm()

#     return render(request, 'downloads/upload_folder.html', {'form': form})

import os
import zipfile
from django.core.files.base import ContentFile
from django.conf import settings
from django.shortcuts import render
from .forms import UploadFolderForm
from .models import Downloadable
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


# def upload_folder(request):
#     if request.method == 'POST':
#         form = UploadFolderForm(request.POST, request.FILES)
#         if form.is_valid():
#             folder = request.FILES['folder']
#             # Extraire le nom du dossier de l'archive zip
#             folder_name = os.path.splitext(os.path.basename(folder.name))[0]
#             print(str(folder_name))

#             with zipfile.ZipFile(folder) as z:
#                 for filename in z.namelist():
#                     # Assurez-vous que le nom de fichier est sécurisé
#                     safe_filename = os.path.basename(filename)
#                     if safe_filename.startswith('._'):
#                         safe_filename = safe_filename[2:]

#                     print("file name -- > "+str(safe_filename))  # Extrait '008'

#                     # Extraire les 3 premiers chiffres du nom du fichier
#                     file_prefix = safe_filename.split('-')[0]
#                     print("prefix -- > "+str(file_prefix))  # Extrait '008'

# try:
#     # Obtenez l'utilisateur
#     try:
#         user = get_object_or_404(User, userprofile__pc_paie_id=file_prefix)
#         print("User -- > "+str(user))
#     except UserProfile.DoesNotExist:
#         print(f"UserProfile with pc_paie_id {file_prefix} does not exist.")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     pdf_file = z.open(filename)
#     # Créez un chemin sécurisé pour le fichier temporaire
#     temp_file_path = os.path.join(settings.MEDIA_ROOT, 'downloadable', safe_filename)
#     os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
#     # Écrire le fichier temporairement
#     with open(temp_file_path, 'wb') as temp_file:
#         temp_file.write(pdf_file.read())
#     # Utilisez `ContentFile` pour créer un objet Django File
#     with open(temp_file_path, 'rb') as f:
#         content = ContentFile(f.read(), name=safe_filename)

#         # Formater le nom du lien
#         link_name = f"BULLETIN DE PAIE {folder_name}"

#         downloadable = Downloadable.objects.create(
#             attachement=content,
#             link_name=link_name,
#         )
#         downloadable.users.add(user)
#     # Nettoyez le fichier temporaire
#     os.remove(temp_file_path)

# except User.DoesNotExist:
#     print(f"User does not exist.")
# except UserProfile.DoesNotExist:
#     print(f"UserProfile does not exist.")
# except Exception as e:
#     print(f"An error occurred: {e}")

#         return render(request, 'downloads/upload_success.html')
# else:
#     form = UploadFolderForm()

# return render(request, 'downloads/upload_folder.html', {'form': form})

import os
import zipfile
from django.core.files.base import ContentFile
from django.conf import settings
from django.shortcuts import render
from .forms import UploadFolderForm
from .models import Downloadable
from django.contrib.auth.models import User


import os
import zipfile
from django.core.files.base import ContentFile
from django.conf import settings
from django.shortcuts import render
from .forms import UploadFolderForm
from .models import Downloadable
from django.contrib.auth.models import User


def upload_folder(request):
    if request.method == "POST":
        form = UploadFolderForm(request.POST, request.FILES)
        if form.is_valid():
            folder = request.FILES["folder"]
            # Extraire le nom du dossier de l'archive zip
            folder_name = os.path.splitext(os.path.basename(folder.name))[0]
            print(f"Folder name extracted: {folder_name}")

            processed_prefixes = set()  # Ensemble pour suivre les préfixes traités

            with zipfile.ZipFile(folder) as z:
                for filename in z.namelist():
                    # Ignorer les fichiers système
                    if filename.startswith("__MACOSX") or filename.startswith("._"):
                        print(f"Ignoring system file: {filename}")
                        continue

                    # Nettoyer le nom du fichier
                    safe_filename = os.path.basename(filename)
                    if safe_filename.startswith("._"):
                        safe_filename = safe_filename[2:]

                    print(f"Processing file: {filename}")
                    print(f"Cleaned file name: {safe_filename}")

                    # Extraire les 3 premiers chiffres du nom du fichier
                    file_prefix = safe_filename.split("-")[0]
                    print(f"Extracted prefix: {file_prefix}")

                    # Vérifier si le préfixe a déjà été traité
                    if file_prefix in processed_prefixes:
                        print(f"Prefix {file_prefix} already processed, skipping file.")
                        continue

                    try:
                        user = User.objects.get(userprofile__pc_paie_id=file_prefix)
                        print(f"Found user: {user.username}")

                        pdf_file = z.open(filename)
                        temp_file_path = os.path.join(
                            settings.MEDIA_ROOT, "downloadable", safe_filename
                        )
                        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

                        with open(temp_file_path, "wb") as temp_file:
                            temp_file.write(pdf_file.read())

                        with open(temp_file_path, "rb") as f:
                            content = ContentFile(f.read(), name=safe_filename)

                            link_name = f"BULLETIN DE PAIE {folder_name}"

                            downloadable = Downloadable.objects.create(
                                attachement=content,
                                link_name=link_name,
                            )
                            downloadable.users.add(user)

                        # Marquer le préfixe comme traité
                        processed_prefixes.add(file_prefix)
                        os.remove(temp_file_path)

                    except User.DoesNotExist:
                        print(
                            f"User with profile pc_paie_id {file_prefix} does not exist."
                        )
                    except Exception as e:
                        print(f"An error occurred: {e}")

            return render(request, "downloads/upload_success.html")
    else:
        form = UploadFolderForm()

    return render(request, "downloads/upload_folder.html", {"form": form})


import os
import zipfile
from django.core.files.base import ContentFile
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from .models import Downloadable
from django.contrib.auth.models import User
from .forms import UploadFolderForm  # Assurez-vous d'avoir ce formulaire défini


# def import_pdf_folder(request):
#     if request.method == "POST":
#         form = UploadFolderForm(request.POST, request.FILES)
#         if form.is_valid():
#             folder = request.FILES["folder"]
#             # Extraire le nom du dossier de l'archive zip
#             folder_name = os.path.splitext(os.path.basename(folder.name))[0]
#             print(f"Dossier extrait : {folder_name}")

#             processed_users = set()  # Ensemble pour suivre les utilisateurs traités

#             with zipfile.ZipFile(folder) as z:
#                 for filename in z.namelist():
#                     # Ignorer les fichiers système
#                     if filename.startswith("__MACOSX") or filename.startswith("._"):
#                         print(f"Ignoring system file: {filename}")
#                         continue

#                     # Nettoyer le nom du fichier
#                     safe_filename = os.path.basename(filename)
#                     print(f"Processing file: {filename}")
#                     print(f"Cleaned file name: {safe_filename}")

#                     # Extraire le nom d'utilisateur et le mois
#                     try:
#                         username, month = safe_filename[:-4].split(
#                             "_"
#                         )  # Enlève '.pdf' et divise
#                         print(f"Extracted username: {username}, month: {month}")

#                         # Vérifier si l'utilisateur a déjà été traité
#                         if username in processed_users:
#                             print(
#                                 f"Utilisateur {username} déjà traité, fichier ignoré."
#                             )
#                             continue

#                         user = User.objects.get(
#                             username=username
#                         )  # Récupérer l'utilisateur
#                         print(f"Utilisateur trouvé : {user.username}")

#                         # Lire le fichier PDF à partir de l'archive
#                         pdf_file = z.open(filename)
#                         temp_file_path = os.path.join(
#                             settings.MEDIA_ROOT, "downloadable", safe_filename
#                         )
#                         os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

#                         with open(temp_file_path, "wb") as temp_file:
#                             temp_file.write(pdf_file.read())

#                         with open(temp_file_path, "rb") as f:
#                             content = ContentFile(f.read(), name=safe_filename)

#                             # Utiliser le nom d'origine pour le champ attachement
#                             downloadable = Downloadable.objects.create(
#                                 attachement=content,
#                                 link_name=safe_filename,  # Nom d'origine du fichier
#                             )
#                             downloadable.users.add(user)

#                         # Marquer l'utilisateur comme traité
#                         processed_users.add(username)
#                         os.remove(temp_file_path)  # Supprimer le fichier temporaire

#                     except User.DoesNotExist:
#                         print(f"L'utilisateur {username} n'existe pas.")
#                     except Exception as e:
#                         print(f"Une erreur s'est produite : {e}")

#             return render(request, "downloads/upload_success.html")
#     else:
#         form = UploadFolderForm()


#     return render(request, "downloads/upload_gp.html", {"form": form})

def import_pdf_folder(request):
    if request.method == "POST":
        form = UploadFolderForm(request.POST, request.FILES)
        if form.is_valid():
            folder = request.FILES["folder"]
            folder_name = os.path.splitext(os.path.basename(folder.name))[0]
            print(f"Dossier extrait : {folder_name}")

            processed_users = set()  # Ensemble pour suivre les utilisateurs traités

            with zipfile.ZipFile(folder) as z:
                for filename in z.namelist():
                    if filename.startswith("__MACOSX") or filename.startswith("._"):
                        print(f"Ignoring system file: {filename}")
                        continue

                    safe_filename = os.path.basename(filename)
                    print(f"Processing file: {filename}")
                    print(f"Cleaned file name: {safe_filename}")

                    try:
                        username, month = safe_filename[:-4].split("_")
                        print(f"Extracted username: {username}, month: {month}")

                        if username in processed_users:
                            print(
                                f"Utilisateur {username} déjà traité, fichier ignoré."
                            )
                            continue

                        user = User.objects.get(username=username)
                        print(f"Utilisateur trouvé : {user.username}")

                        pdf_file = z.open(filename)
                        temp_file_path = os.path.join(
                            settings.MEDIA_ROOT, "downloadable", safe_filename
                        )
                        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

                        with open(temp_file_path, "wb") as temp_file:
                            temp_file.write(pdf_file.read())

                        with open(temp_file_path, "rb") as f:
                            content = ContentFile(f.read(), name=safe_filename)

                            # Créer le nom de lien formaté
                            # link_name = f"{username}_{month}.pdf"
                            link_name = f"Griffe de passage pharmacie_{username}_1"
                            

                            downloadable = Downloadable.objects.create(
                                attachement=content,
                                link_name=link_name,  # Nouveau nom formaté
                            )
                            downloadable.users.add(user)

                        processed_users.add(username)
                        os.remove(temp_file_path)

                    except User.DoesNotExist:
                        print(f"L'utilisateur {username} n'existe pas.")
                    except Exception as e:
                        print(f"Une erreur s'est produite : {e}")

            return render(request, "downloads/upload_success.html")
    else:
        form = UploadFolderForm()

    return render(request, "downloads/upload_gp.html", {"form": form})










import json
import requests
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt

OLLAMA_URL = "http://localhost:11434/api/generate"

@csrf_exempt
def chatbot(request):
    if request.method != "POST":
        return StreamingHttpResponse(
            json.dumps({"error": "Only POST method allowed"}),
            content_type="application/json",
            status=405
        )

    try:
        data = json.loads(request.body)
        question = data.get("question", "").strip()
        lang = data.get("lang", "fr").strip().lower()
        print("ASSKKINNNGGGG")
        print("ASSKKINNNGGGG")
        print("ASSKKINNNGGGG")
        print("ASSKKINNNGGGG")

        if not question:
            return StreamingHttpResponse(
                json.dumps({"error": "Missing question"}),
                content_type="application/json",
                status=400
            )

        lang_map = {
            "fr": "français",
            "ar": "arabe moderne",
            "en": "anglais"
        }
        target_lang = lang_map.get(lang, "français")

        prompt = (
            f"Tu es un assistant utile et poli. "
            f"Réponds uniquement en {target_lang}. "
            "Réponds de manière courte et claire.\n"
            f"Question: {question}"
        )

        def generate():
            try:
                with requests.post(
                    OLLAMA_URL,
                    json={"model": "llama2:7b", "prompt": prompt, "stream": True},
                    stream=True,
                    timeout=(2, 30)  # connect, read timeout
                ) as r:
                    r.raise_for_status()
                    for line in r.iter_lines(decode_unicode=True):
                        if line:
                            try:
                                chunk = json.loads(line)
                                if "response" in chunk:
                                    yield chunk["response"]
                            except json.JSONDecodeError:
                                continue
            except requests.RequestException as e:
                yield f"Erreur serveur Ollama: {str(e)}"

        return StreamingHttpResponse(generate(), content_type="text/plain")

    except json.JSONDecodeError:
        return StreamingHttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            content_type="application/json",
            status=400
        )
