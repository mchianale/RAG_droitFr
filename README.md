
# Projet : Création d'un RAG (Retrieve and Generate) autour du droit français
Ce projet vise à développer une solution de recherche et d'extraction d'informations basée sur les textes du droit français. Il s'agit d'un système intelligent de récupération de données juridiques, avec l'objectif de faciliter la recherche d'informations pertinentes en utilisant des techniques avancées de traitement du langage naturel (NLP) et de clustering. Le projet se divise en plusieurs étapes clés, visant à optimiser l'accès et la manipulation des données juridiques.

### Étapes du projet :
1. **Récupération des données** : Collecte des textes juridiques et des documents relatifs au droit français (**~166722 documents**) sur `LegiFrance` et `Wikipedia`.
2. **Stockage des données** : Mise en place d'une base de données efficace pour stocker et gérer les documents récupérés.
3. **Système de recherche par similarité** : Mise en place d'un moteur de recherche basé sur la similarité sémantique, permettant de trouver des documents pertinents. Cette recherche est optimisée par un processus de clustering pour réduire l'espace de recherche.
4. **Création d'une API (FastAPI)** : Développement d'une API permettant d'interroger et d'insérer des documents dans le système, facilitant ainsi l'accès et la gestion des données juridiques.

---
### Exemple de requête 
`Quelles sont les conditions légales pour se marier en France ?` :
```json
 [
   {
        "text": "\nPour être opposable aux tiers en France, l'acte de mariage d'un Français célébré par une autorité étrangère\ndoit être transcrit sur les registres de l'état civil français. En l'absence de transcription, le mariage d'un\nFrançais, valablement célébré par une autorité étrangère, produit ses effets civils en France à l'égard des\népoux et des enfants.\nLes futurs époux sont informés des règles prévues au premier alinéa à l'occasion de la délivrance du certificat\nde capacité à mariage.\nLa demande de transcription est faite auprès de l'autorité consulaire ou diplomatique compétente au regard\ndu lieu de célébration du mariage.",
        "cosine_similarity": 0.8375268358093255
    },
    {
        "text": "En France, le droit des régimes matrimoniaux est une branche du droit regroupant les règles qui s'appliquent aux époux liés par le mariage pendant leur vie commune et au moment de la dissolution de leur union. La gestion des biens, les obligations pécuniaires des époux envers les tiers, leurs obligations familiales, la composition de leurs patrimoines (biens communs, propres ou indivis) pendant et après le mariage sont décrits dans leur régime matrimonial.\nIl existe deux grandes catégories de régimes matrimoniaux : \n\nles régimes communautaires, dans lesquels la plupart des biens appartiennent en commun aux époux ;\nles régimes séparatistes, dans lesquels l'un des époux, ou les deux, est ou a vocation à être, à la tête d'un patrimoine personnel et où chacun répond seul de ses dettes.\nLe droit français laisse la liberté aux époux de choisir leur régime matrimonial en rédigeant un contrat de mariage au moment du mariage ou, éventuellement, pendant la vie commune. Cette liberté de choix est prévue par l'article 1387 du Code civil et permet aux intéressés d'organiser comme ils le désirent leurs relations patrimoniales, sous réserves de respecter un minimum de règles communes que l'on nomme le statut impératif de base. À défaut de contrat de mariage, la loi française prévoit que les époux seront soumis à l'un d'eux que l'on appelle le régime légal et qui est, depuis 1966, la communauté réduite aux acquêts.",
        "cosine_similarity": 0.8304367584434162
    }]
```
---

# Sommaire
1. [Run](#run)
2. [Récupération des données](#récupération-des-données)
    - [Extraction des articles en vigueur des codes](#extraction-des-articles-en-vigueur-des-codes)
    - [Extraction d'informations liées au droit Français](#extraction-dinformations-liées-au-droit-français)
    - [Récupérer un échantillon de données](#récupérer-un-échantillon-de-données)
4. [Système de recherche par similarité](#système-de-recherche-par-similarité)
    - [Représentation des documents avec des embeddings](#1-représentation-des-documents-avec-des-embeddings)
    - [Comparaison des documents avec la distance cosinus](#2-comparaison-des-documents-avec-la-distance-cosinus)
    - [Réduction de l'espace de recherche avec KMeans](#3-réduction-de-lespace-de-recherche-avec-K-Means-Clustering) 
    - [Évaluation des clusters](#4-évaluation-des-clusters)
    - [Intérêt du système de clustering](#5-intérêt)
5. [API](#api)
6. [Amélioration / À faire](#amélioration-à-faire)
    - [Améliorer le clustering (KMeans)](#1-améliorer-le-clustering-KMeans)
    - [Interface ou outil de visualisation](#2-interface-ou-outil-de-visualisation)
    - [Utilisation de LLAMA 3.2 1B en local pour créer un chatbot](#3-utilisation-de-llama-32-1b-en-local-pour-créer-un-chatbot)
    - [Évaluation du système de retrieval du RAG avec un jeu de tests](#4-évaluation-du-système-de-retrieval-du-rag-avec-un-jeu-de-tests)
    - [Nouveau système de base de données orienté vectorielle](#5-nouveau-système-de-base-de-données-orienté-vectorielle)
      
---

## Run
**python version I used : 3.10.11**
```bash
pip install -r requirements.txt
```
- Run MongoDB:
```bash
docker-compose up -d
```
- Run the Fast-API:
```bash
uvicorn app.main:app --reload
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

### Récupérer un échantillon de données

Crée un fichier Python qui récupère `N` données choisies aléatoirement (à fixer dans [create_sample.py](https://github.com/mchianale/RAG_droitFr/blob/main/get_data/create_sample.py)).

```bash
python get_data/create_sample.py
```

---

## Système de recherche par similarité

Le système de recherche par similarité de ce projet repose sur plusieurs étapes clés : l'utilisation d'embeddings pour représenter les documents, la mesure de la similarité entre ces embeddings à l'aide de la distance cosinus, et l'optimisation de l'espace de recherche par clustering des documents à l'aide de KMeans.

### 1. Représentation des documents avec des embeddings

Les documents sont représentés sous forme d'**embeddings** vectoriels générés à partir du modèle `paraphrase-multilingual-MiniLM-L12-v2` de **Sentence-Transformers**. Ce modèle permet de transformer chaque document en un vecteur dense qui capture le sens sémantique du texte. Cette approche permet de comparer les documents entre eux en fonction de leur signification, et non simplement de mots-clés ou de correspondances exactes.

### 2. Comparaison des documents avec la distance cosinus

Une fois les documents convertis en embeddings, la comparaison des documents se fait en utilisant la **distance cosinus**. Cette méthode mesure la similarité entre deux vecteurs en fonction de l'angle entre eux. Plus l'angle est petit, plus les vecteurs sont similaires. La formule utilisée est la suivante :

**Cosine Similarity = (A · B) / (|A| * |B|)**

Où **A** et **B** sont les embeddings de deux documents et **|A|** et **|B|** sont leurs normes respectives.

### 3. Réduction de l'espace de recherche avec K-Means Clustering  

Pour optimiser l'efficacité de la recherche, les documents sont regroupés en clusters à l'aide de l'algorithme **KMeans**. Cet algorithme divise les documents en groupes basés sur leurs similarités, mesurées par la distance cosinus entre les vecteurs.

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

**Comparaison des complexités**

Pour une même recherche de similarité d'une requête avec l'ensemble des données (**n** documents), voici la comparaison des deux méthodes :

##### 1. **Brute force (comparaison avec tous les documents)**

Dans la méthode brute force, chaque document de la base de données est comparé à la requête. Cela implique que la complexité augmente linéairement avec le nombre de documents **n**.

- **Complexité** : **O(n)**

Cela signifie que pour chaque requête, nous devons effectuer **n** comparaisons de similarité (une pour chaque document).

##### 2. **Clustering (réduction de l'espace de recherche)**

En utilisant le **clustering**, on divise l'ensemble des documents en **m** clusters. Au lieu de comparer la requête avec tous les documents, on compare d'abord la requête avec les **centroids** des clusters à l'aide de la **similarité cosinus**. Ensuite, on choisit le cluster le plus pertinent, et on ne compare la requête qu'avec les documents à l'intérieur de ce cluster, réduisant ainsi l'espace de recherche.

- **Étape 1** : Comparaison de la requête avec les centroids des **m** clusters (complexité **O(m)**).
- **Étape 2** : Comparaison de la requête avec les documents du cluster sélectionné, où **p** est le nombre de documents dans ce cluster. On suppose que, de manière idéale, les données sont réparties équitablement entre les clusters, donc p ~= n // m.

Ainsi, la complexité totale de la méthode **clustering** devient :

- **Complexité** : O(m) + O(p) 

On peut espérer réduire la complexité de la recherche à une valeur beaucoup plus faible que **O(n)**, en particulier lorsque **m** (le nombre de clusters) est petit.

#### Conclusion

En résumé, en passant d'une approche brute force à une approche avec clustering, on réduit considérablement le nombre de comparaisons nécessaires, ce qui permet d'améliorer les performances du système de recherche. Cela est particulièrement utile lorsque l'on travaille avec un grand nombre de documents, où la méthode brute force deviendrait inefficace.

---

## API
L'API de ce projet est construite avec **FastAPI** et permet d'interagir avec le service de recherche de documents. Les différentes routes suivantes sont définies pour effectuer des tâches spécifiques, telles que la recherche de documents, la gestion des clusters, l'ajout de nouveaux documents, etc.

**Voir les méthodes : [app](https://github.com/mchianale/RAG_droitFr/tree/main/app)**

---

## Amélioration / À faire
Voici une liste des améliorations et des tâches futures à mettre en place pour améliorer le projet :

### 1. **Améliorer le clustering (KMeans)**
   - Le système actuel de création des clusters basé sur KMeans est assez lent, surtout avec un grand nombre de documents. Il est nécessaire de l'optimiser pour gagner en performance, en utilisant des méthodes comme l'approximation de la recherche voisine (par exemple, avec HNSW) ou d'autres algorithmes plus efficaces.

### 2. **Interface ou outil de visualisation**
   - Développer une interface graphique ou un outil de visualisation pour permettre aux utilisateurs d'accéder facilement aux données. Cela pourrait inclure une interface pour explorer les clusters, visualiser les résultats de la recherche par similarité et interagir de manière plus intuitive avec les documents.

### 3. **Utilisation de LLAMA 3.2 1B en local pour créer un chatbot (JuryBot)**
   - Intégrer LLAMA 3.2 1B pour créer un chatbot, baptisé **JuryBot**, dédié à répondre aux questions sur le droit français. Ce chatbot serait basé sur les documents collectés et les embeddings générés, offrant une interface conversationnelle pour interagir avec les données juridiques.

### 4. **Évaluation du système de retrieval du RAG avec un jeu de tests**
   - Implémenter un jeu de tests pour évaluer le système de récupération d'informations (retrieval) dans le contexte du **RAG (Retrieval-Augmented Generation)**. Cela permettra de mesurer la performance du système en termes de précision, de rappel, et de F1-score, et d'ajuster les paramètres du modèle en fonction des résultats obtenus.

### 5. **Nouveau système de base de données orienté vectorielle**
   - Passer à un système de base de données plus adapté aux embeddings et aux recherches vectorielles, comme **FAISS**. Ce type de base de données permettra des recherches plus rapides et plus scalables.
   - Il serait également intéressant d'explorer des systèmes de **GraphRAG**, qui utilise des métadonnées et des graphes pour améliorer les requêtes et la récupération d'informations.
   - Ajout des metadonnées dans la BD. (nom d'article, code etc..)

Ces améliorations permettront d'augmenter la performance du système, d'enrichir l'interaction utilisateur et de rendre le projet plus robuste et scalable à mesure que les données et les fonctionnalités se développent.

