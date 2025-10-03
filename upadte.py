import psycopg2

# Paramètres de connexion à la base PostgreSQL
db_config = {
    'dbname': 'lilliumpharma',
    'user': 'postgres',
    'password': 'openpgpwd',
    'host': 'localhost',
    'port': 5432
}

try:
    # Connexion à PostgreSQL
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # Requête de mise à jour
    update_query = "UPDATE public.rapports_rapport SET can_update = FALSE WHERE can_update = TRUE;"
    cursor.execute(update_query)

    # Sauvegarde des modifications
    conn.commit()

    print(f"{cursor.rowcount} ligne(s) mise(s) à jour avec can_update = FALSE.")

except Exception as e:
    print("Erreur lors de la connexion ou de l'exécution :", e)

finally:
    # Fermeture
    if cursor:
        cursor.close()
    if conn:
        conn.close()



