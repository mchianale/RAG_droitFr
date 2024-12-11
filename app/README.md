# APP
- [POST /clusterize](#2-post-clusterize)
- [POST /insert_new_document](#3-post-insert_new_document)
- [POST /insert_new_documents](#4-post-insert_new_documents)
- [GET /evaluate_clusters](#5-get-evaluate_clusters)
- [POST /reset](#6-post-reset)
- [GET /info](#7-get-info)
  
---

## 1. GET /query
Permet de rechercher des documents similaires à une requête donnée.

**Paramètres :**
- query (str) : Le texte de la requête à rechercher dans les documents.
- limit (int, optionnel, par défaut 10) : Le nombre de documents à retourner.

**Réponse :** Une liste de documents avec leur texte et leur similarité en cosinus par rapport à la requête.

---

## 2. POST /clusterize

Permet de créer des clusters de documents en utilisant l'algorithme de clustering.

**Paramètres :**
- `n_clusters` (int) : Le nombre de clusters à créer.
- `max_iter` (int, optionnel, par défaut 300) : Le nombre maximum d'itérations pour le clustering.
- `tolerance` (float, optionnel, par défaut 1e-4) : La tolérance pour la convergence des centroids.
- `patience` (int, optionnel, par défaut 10) : Le nombre d'itérations sans changement significatif avant l'arrêt.

**Réponse :**  
Un message de confirmation indiquant le nombre d'itérations effectuées et le temps écoulé pour le clustering.

---

## 3. POST /insert_new_document

Permet d'ajouter un nouveau document à la base de données.

**Paramètres :**
- `doc` (Dict) : Le document à insérer. Le dictionnaire doit contenir au moins un champ `text` qui contient le texte du document.

**Réponse :**  
Un message de confirmation indiquant que le document a été ajouté avec succès.

---

## 4. POST /insert_new_documents

Permet d'ajouter plusieurs documents à la base de données en utilisant le traitement en parallèle pour accélérer l'insertion.

**Paramètres :**
- `docs` (List[Dict]) : Une liste de documents à insérer. Chaque document doit être un dictionnaire contenant au moins un champ `text` avec le texte du document.
- `chunk_size` (int, optionnel, par défaut 8) : Le nombre de documents traités par thread pour l'insertion parallèle.

**Réponse :**  
Un message de confirmation indiquant que les documents ont été ajoutés avec succès.

---

## 5. GET /evaluate_clusters

Permet d'évaluer la qualité des clusters créés en fonction de la similarité des documents au sein de chaque cluster.

**Paramètres :**
- `threshold` (float, optionnel, par défaut 0.9) : Le seuil de similarité en cosinus pour déterminer si deux documents dans le même cluster sont considérés comme correctement regroupés. Si la similarité est supérieure ou égale à ce seuil, les documents sont considérés comme appartenant au même cluster.

**Réponse :**  
Une évaluation des clusters, incluant la précision, le rappel, le score F1, la similarité moyenne et le nombre total de documents. Ces métriques permettent d'évaluer la cohérence des documents au sein des clusters.

---

## 6. POST /reset

Permet de réinitialiser la base de données en supprimant tous les documents et les centroids des clusters. Cela permet de repartir de zéro et de recréer de nouveaux clusters si nécessaire.

**Réponse :**  
Un message indiquant que la réinitialisation a été effectuée avec succès.

---

## 7. GET /info

Permet d'obtenir des informations sur l'état actuel des données et des clusters dans la base de données. Cette route retourne le nombre total de documents et la répartition des documents dans les clusters.

**Réponse :**  
Un objet JSON contenant le nombre total de documents dans la base de données ainsi que des informations détaillées sur le nombre de documents dans chaque cluster, le cas échéant.

