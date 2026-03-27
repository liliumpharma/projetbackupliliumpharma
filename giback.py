# import os
# import subprocess
# from datetime import datetime
# # 📂 Dossier à sauvegarder
# SERVER_DIR = "/var/www/server"
# WORK_DIR = "/var/www/server"
# # 🔗 Repo GitHub (avec token)***REPLACED_TOKEN*** 
# GITHUB_REPO = "https://***REPLACED_TOKEN***@github.com/liliumpharma/projetbackupliliumpharma.git"

# # Aller dans le dossier
# os.chdir(WORK_DIR)

# def run(cmd):
#     """Exécuter une commande shell"""
#     result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
#     if result.stdout:
#         print(result.stdout.strip())
#     if result.stderr:
#         print(result.stderr.strip())
#     return result

# print("➡️ Vérification du dépôt Git...")
# if not os.path.exists(os.path.join(WORK_DIR, ".git")):
#     print("⚡ Pas de dépôt Git, initialisation...")
#     run("git init -b main")

# print("➡️ Configuration du remote GitHub...")
# run("git remote remove origin || true")  # supprime si déjà présent
# run(f"git remote add origin {GITHUB_REPO}")

# print("➡️ Ajout des fichiers...")
# run("git add .")

# commit_message = f"Backup {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
# print(f"➡️ Commit : {commit_message}")
# run(f'git commit -m "{commit_message}" || echo "⚠️ Rien à commit"')

# print("➡️ Envoi vers GitHub...")
# run("git push origin main --force")


# print("✅ Sauvegarde envoyée sur GitHub")

# print("hmdlhhhh")