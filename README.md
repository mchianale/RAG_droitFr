
# Projet : Création d'un RAG (Retrieve and Generate) autour du droit français
Ce projet vise à développer une solution de recherche et d'extraction d'informations basée sur les textes du droit français. Il s'agit d'un système intelligent de récupération de données juridiques, avec l'objectif de faciliter la recherche d'informations pertinentes en utilisant des techniques avancées de traitement du langage naturel (NLP) et de clustering. Le projet se divise en plusieurs étapes clés, visant à optimiser l'accès et la manipulation des données juridiques.

### Étapes du projet :
1. **Récupération des données** : Collecte des textes juridiques et des documents relatifs au droit français (**~166722 documents**).
2. **Stockage des données** : Mise en place d'une base de données efficace pour stocker et gérer les documents récupérés.
3. **Système de recherche par similarité** : Mise en place d'un moteur de recherche basé sur la similarité sémantique, permettant de trouver des documents pertinents. Cette recherche est optimisée par un processus de clustering pour réduire l'espace de recherche.
4. **Création d'une API (FastAPI)** : Développement d'une API permettant d'interroger et d'insérer des documents dans le système, facilitant ainsi l'accès et la gestion des données juridiques.

---

# Sommaire
1. [Run](#run)
    - [Installation des dépendances](#installation-des-dépendances)
    - [Lancer le système avec Docker](#lancer-le-système-avec-docker)
    - [Initialiser la base de données](#initialiser-la-base-de-données)
2. [Récupération des données](#récupération-des-données)
    - [Extraction des articles en vigueur des codes](#extraction-des-articles-en-vigueur-des-codes)
    - [Extraction d'informations liées au droit Français](#extraction-dinformations-liées-au-droit-français)
3. [Récupérer un échantillon de données](#récupérer-un-échantillon-de-données)
4. [Système de recherche par similarité](#système-de-recherche-par-similarité)
    - [Représentation des documents avec des embeddings](#représentation-des-documents-avec-des-embeddings)
    - [Comparaison des documents avec la distance cosinus](#comparaison-des-documents-avec-la-distance-cosinus)
    - [Réduction de l'espace de recherche avec KNN](#réduction-de-lespace-de-recherche-avec-knn)
    - [Évaluation des clusters](#évaluation-des-clusters)
    - [Intérêt du système de clustering](#intérêt-du-système-de-clustering)
5. [API](#api)
    - [GET /query](#get-query)
    - [POST /clusterize](#post-clusterize)
    - [POST /insert_new_document](#post-insert_new_document)
    - [POST /insert_new_documents](#post-insert_new_documents)
    - [GET /evaluate_clusters](#get-evaluate_clusters)
    - [POST /reset](#post-reset)
    - [GET /info](#get-info)
6. [Amélioration / À faire](#amélioration-à-faire)
    - [Améliorer le clustering (KNN)](#améliorer-le-clustering-knn)
    - [Interface ou outil de visualisation](#interface-ou-outil-de-visualisation)
    - [Utilisation de LLAMA 3.2 1B en local pour créer un chatbot](#utilisation-de-llama-32-1b-en-local-pour-créer-un-chatbot)
    - [Évaluation du système de retrieval du RAG avec un jeu de tests](#évaluation-du-système-de-retrieval-du-rag-avec-un-jeu-de-tests)
    - [Nouveau système de base de données orienté vectorielle (FAISS) et GraphRAG](#nouveau-système-de-base-de-données-orienté-vectorielle-faiss-et-graphrag)
      
---

## Run
**python version I used : 3.10.11**
```bash
pip install -r requirements.txt
```

```bash
docker-compose up -d
```

**Initialiser la base de données avec les données récupérées:**
```bash
python populate_db.py
``` 
**Warning** : Assurez-vous que MongoDB soit bien lancé et instancié avant d'exécuter ce script.

---

## Récupération des données
Pour extraire les données, exécutez le script suivant :

```bash
python get_data/createDroitData.py
```
Cela permet de sauvegarder les données au format `json`.
### Extraction des articles en vigueur des codes
- Extraction des articles à partir des fichiers PDF sur [LegiFrance](https://www.legifrance.gouv.fr/liste/code?etatTexte=VIGUEUR&etatTexte=VIGUEUR_DIFF&page=1#code)
- voir [init_code.py](https://github.com/mchianale/RAG_droitFr/blob/main/get_data/init_code.py)
### Extraction d'informations liées au droit Francais
- Extraction des données à l'aide de la bibliothèque `wikipedia-api`.
- Extraction des articles liés au droit français depuis [Wikipedia](https://fr.wikipedia.org/wiki/Cat%C3%A9gorie:Portail:Droit_fran%C3%A7ais/Articles_li%C3%A9s)
- voir [init_corpus.py](https://github.com/mchianale/RAG_droitFr/blob/main/get_data/init_corpus.py)

## Récupérer un échantillon de données

Crée un fichier Python qui récupère `N` données choisies aléatoirement (à fixer dans [create_sample.py](https://github.com/mchianale/RAG_droitFr/blob/main/get_data/create_sample.py)).

```bash
python get_data/create_sample.py
```

---

## Système de recherche par similarité

Le système de recherche par similarité de ce projet repose sur plusieurs étapes clés : l'utilisation d'embeddings pour représenter les documents, la mesure de la similarité entre ces embeddings à l'aide de la distance cosinus, et l'optimisation de l'espace de recherche par clustering des documents à l'aide de K-Nearest Neighbors (KNN).

### 1. Représentation des documents avec des embeddings

Les documents sont représentés sous forme d'**embeddings** vectoriels générés à partir du modèle `paraphrase-multilingual-MiniLM-L12-v2` de **Sentence-Transformers**. Ce modèle permet de transformer chaque document en un vecteur dense qui capture le sens sémantique du texte. Cette approche permet de comparer les documents entre eux en fonction de leur signification, et non simplement de mots-clés ou de correspondances exactes.

### 2. Comparaison des documents avec la distance cosinus

Une fois les documents convertis en embeddings, la comparaison des documents se fait en utilisant la **distance cosinus**. Cette méthode mesure la similarité entre deux vecteurs en fonction de l'angle entre eux. Plus l'angle est petit, plus les vecteurs sont similaires. La formule utilisée est la suivante :

\[
\text{Cosine Similarity} = \frac{A \cdot B}{\|A\| \|B\|}
\]

Où \( A \) et \( B \) sont les embeddings de deux documents et \( \|A\| \) et \( \|B\| \) sont leurs normes respectives.

### 3. Réduction de l'espace de recherche avec KNN (K-Nearest Neighbors)

Pour optimiser l'efficacité de la recherche, les documents sont regroupés en **clusters** à l'aide de l'algorithme **K-Nearest Neighbors (KNN)**. Cet algorithme permet de réduire l'espace de recherche en identifiant les documents similaires les uns aux autres et en les regroupant dans des clusters. La distance cosinus est utilisée comme critère pour définir les voisins les plus proches.

### 4. Évaluation des clusters

Une fois les clusters formés, la performance du système de recherche est évaluée en fonction de la similarité entre les documents au sein des mêmes clusters (positifs) et entre les documents provenant de clusters différents (négatifs). Les mesures suivantes sont utilisées pour évaluer la qualité des clusters :

- **Vrai Positif (TP)** : Les paires de documents similaires qui se trouvent dans le même cluster.
- **Faux Positif (FP)** : Les paires de documents similaires qui sont classées dans des clusters différents.
- **Vrai Négatif (TN)** : Les paires de documents non similaires qui sont dans des clusters différents.
- **Faux Négatif (FN)** : Les paires de documents non similaires qui sont classées dans le même cluster.

L'évaluation est basée sur plusieurs indicateurs statistiques :

- **Précision (Precision)** : La proportion de vrais positifs parmi tous les résultats pertinents trouvés.
- **Rappel (Recall)** : La proportion de vrais positifs parmi tous les documents qui auraient dû être retrouvés.
- **Score F1 (F1-score)** : Une moyenne harmonique de la précision et du rappel, qui combine ces deux mesures en un seul score.

Les performances sont mesurées pour chaque paire de clusters en calculant la similarité cosinus entre les documents et en mettant à jour les compteurs de TP, FP, TN et FN. Ensuite, ces valeurs sont utilisées pour calculer la précision, le rappel et le F1-score.

### 5. Intérêt

L'intérêt du système de recherche par similarité avec **clustering** réside dans l'optimisation de la recherche, en particulier lorsqu'on doit comparer une requête avec un grand nombre de documents. La comparaison brute avec tous les documents dans la base de données peut être coûteuse en termes de temps de calcul, tandis que le **clustering** permet de réduire cet espace de recherche et d'améliorer l'efficacité. 

#### Comparaison des complexités

Pour une même recherche de similarité d'une requête avec l'ensemble des données (\(n\) documents), voici la comparaison des deux méthodes :

##### 1. **Brute force (comparaison avec tous les documents)**

Dans la méthode brute force, chaque document de la base de données est comparé à la requête. Cela implique que la complexité augmente linéairement avec le nombre de documents \(n\).

- **Complexité** : \( O(n) \)

Cela signifie que pour chaque requête, nous devons effectuer \(n\) comparaisons de similarité (une pour chaque document).

##### 2. **Clustering (réduction de l'espace de recherche)**

En utilisant le **clustering**, on divise l'ensemble des documents en \(m\) clusters. Au lieu de comparer la requête avec tous les documents, on compare d'abord la requête avec les **centroids** des clusters à l'aide de la **similarité cosinus**. Ensuite, on choisit le cluster le plus pertinent, et on ne compare la requête qu'avec les documents à l'intérieur de ce cluster, réduisant ainsi l'espace de recherche.

- **Étape 1** : Comparaison de la requête avec les centroids des \(m\) clusters (complexité \(O(m)\)).
- **Étape 2** : Comparaison de la requête avec les documents du cluster sélectionné, où \(p\) est le nombre de documents dans ce cluster. On suppose que, de manière idéale, les données sont réparties équitablement entre les clusters, donc \( p \approx n // m \).

Ainsi, la complexité totale de la méthode **clustering** devient :

- **Complexité** : \( O(m) + O(p) \)

Avec \( p \leq n \) et idéalement \( p = \frac{n}{m} \), on peut espérer réduire la complexité de la recherche à une valeur beaucoup plus faible que \( O(n) \), en particulier lorsque \( m \) (le nombre de clusters) est petit.

#### Conclusion

En résumé, en passant d'une approche brute force à une approche avec clustering, on réduit considérablement le nombre de comparaisons nécessaires, ce qui permet d'améliorer les performances du système de recherche. Cela est particulièrement utile lorsque l'on travaille avec un grand nombre de documents, où la méthode brute force deviendrait inefficace.

---

## API
L'API de ce projet est construite avec **FastAPI** et permet d'interagir avec le service de recherche de documents. Les différentes routes suivantes sont définies pour effectuer des tâches spécifiques, telles que la recherche de documents, la gestion des clusters, l'ajout de nouveaux documents, etc.

### 1. GET /query
Permet de rechercher des documents similaires à une requête donnée.

**Paramètres :**
- query (str) : Le texte de la requête à rechercher dans les documents.
- limit (int, optionnel, par défaut 10) : Le nombre de documents à retourner.

**Réponse :** Une liste de documents avec leur texte et leur similarité en cosinus par rapport à la requête.

### 2. POST /clusterize

Permet de créer des clusters de documents en utilisant l'algorithme de clustering.

**Paramètres :**
- `n_clusters` (int) : Le nombre de clusters à créer.
- `max_iter` (int, optionnel, par défaut 300) : Le nombre maximum d'itérations pour le clustering.
- `tolerance` (float, optionnel, par défaut 1e-4) : La tolérance pour la convergence des centroids.
- `patience` (int, optionnel, par défaut 10) : Le nombre d'itérations sans changement significatif avant l'arrêt.

**Réponse :**  
Un message de confirmation indiquant le nombre d'itérations effectuées et le temps écoulé pour le clustering.

### 3. POST /insert_new_document

Permet d'ajouter un nouveau document à la base de données.

**Paramètres :**
- `doc` (Dict) : Le document à insérer. Le dictionnaire doit contenir au moins un champ `text` qui contient le texte du document.

**Réponse :**  
Un message de confirmation indiquant que le document a été ajouté avec succès.

### 4. POST /insert_new_documents

Permet d'ajouter plusieurs documents à la base de données en utilisant le traitement en parallèle pour accélérer l'insertion.

**Paramètres :**
- `docs` (List[Dict]) : Une liste de documents à insérer. Chaque document doit être un dictionnaire contenant au moins un champ `text` avec le texte du document.
- `chunk_size` (int, optionnel, par défaut 8) : Le nombre de documents traités par thread pour l'insertion parallèle.

**Réponse :**  
Un message de confirmation indiquant que les documents ont été ajoutés avec succès.

### 5. GET /evaluate_clusters

Permet d'évaluer la qualité des clusters créés en fonction de la similarité des documents au sein de chaque cluster.

**Paramètres :**
- `threshold` (float, optionnel, par défaut 0.9) : Le seuil de similarité en cosinus pour déterminer si deux documents dans le même cluster sont considérés comme correctement regroupés. Si la similarité est supérieure ou égale à ce seuil, les documents sont considérés comme appartenant au même cluster.

**Réponse :**  
Une évaluation des clusters, incluant la précision, le rappel, le score F1, la similarité moyenne et le nombre total de documents. Ces métriques permettent d'évaluer la cohérence des documents au sein des clusters.

### 6. POST /reset

Permet de réinitialiser la base de données en supprimant tous les documents et les centroids des clusters. Cela permet de repartir de zéro et de recréer de nouveaux clusters si nécessaire.

**Réponse :**  
Un message indiquant que la réinitialisation a été effectuée avec succès.

### 7. GET /info

Permet d'obtenir des informations sur l'état actuel des données et des clusters dans la base de données. Cette route retourne le nombre total de documents et la répartition des documents dans les clusters.

**Réponse :**  
Un objet JSON contenant le nombre total de documents dans la base de données ainsi que des informations détaillées sur le nombre de documents dans chaque cluster, le cas échéant.

## Amélioration / À faire
Voici une liste des améliorations et des tâches futures à mettre en place pour améliorer le projet :

### 1. **Améliorer le clustering (KNN)**
   - Le système actuel de clustering basé sur KNN est assez lent, surtout avec un grand nombre de documents. Il est nécessaire de l'optimiser pour gagner en performance, en utilisant des méthodes comme l'approximation de la recherche voisine (par exemple, avec HNSW) ou d'autres algorithmes plus efficaces.

### 2. **Interface ou outil de visualisation**
   - Développer une interface graphique ou un outil de visualisation pour permettre aux utilisateurs d'accéder facilement aux données. Cela pourrait inclure une interface pour explorer les clusters, visualiser les résultats de la recherche par similarité et interagir de manière plus intuitive avec les documents.

### 3. **Utilisation de LLAMA 3.2 1B en local pour créer un chatbot (JuryBot)**
   - Intégrer LLAMA 3.2 1B pour créer un chatbot, baptisé **JuryBot**, dédié à répondre aux questions sur le droit français. Ce chatbot serait basé sur les documents collectés et les embeddings générés, offrant une interface conversationnelle pour interagir avec les données juridiques.

### 4. **Évaluation du système de retrieval du RAG avec un jeu de tests**
   - Implémenter un jeu de tests pour évaluer le système de récupération d'informations (retrieval) dans le contexte du **RAG (Retrieval-Augmented Generation)**. Cela permettra de mesurer la performance du système en termes de précision, de rappel, et de F1-score, et d'ajuster les paramètres du modèle en fonction des résultats obtenus.

### 5. **Nouveau système de base de données orienté vectorielle (FAISS) et GraphRAG**
   - Passer à un système de base de données plus adapté aux embeddings et aux recherches vectorielles, comme **FAISS**. Ce type de base de données permettra des recherches plus rapides et plus scalables. Il serait également intéressant d'explorer des systèmes de **GraphRAG**, qui utilise des métadonnées et des graphes pour améliorer les requêtes et la récupération d'informations.

Ces améliorations permettront d'augmenter la performance du système, d'enrichir l'interaction utilisateur et de rendre le projet plus robuste et scalable à mesure que les données et les fonctionnalités se développent.

python get_data\createDroitData.py
docker-compose up -d
python populate_db.py
uvicorn app.main:app --reload

backend_service:
    container_name: backend_service
    build:
      context: .
      dockerfile: Dockerfile.app
    ports:
      - "8000:8000"   
    depends_on:
      - mongodb
    networks:
      - public   
