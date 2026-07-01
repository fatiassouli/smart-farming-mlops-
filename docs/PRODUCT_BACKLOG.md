# 📋 Product Backlog - Smart Farming MLOps

---

## 🔵 SPRINT 1 - Ingestion & Transformation (30/06 → 03/07)

### US-01 : Ingestion avec dlt
| Élément | Description |
|---------|-------------|
| **En tant que** | Data Engineer |
| **Je veux** | Ingérer les données avec dlt |
| **Afin de** | Automatiser le chargement des données |
| **Story Points** | 5 |
| **Assignee** | **Ouiam** |
| **Labels** | data-engineering, sprint-1 |

**Critères d'acceptation :**
- [ ] Script dlt pour Crop_recommendation.csv
- [ ] Script dlt pour yield.csv
- [ ] Données chargées dans DuckDB
- [ ] Pipeline fonctionnel

---

### US-02 : Stockage DuckDB
| Élément | Description |
|---------|-------------|
| **En tant que** | Data Engineer |
| **Je veux** | Stocker les données dans DuckDB |
| **Afin de** | Avoir un accès rapide et local |
| **Story Points** | 3 |
| **Assignee** | **Ouiam** |
| **Labels** | data-engineering, sprint-1 |

**Critères d'acceptation :**
- [ ] Base DuckDB créée
- [ ] Schéma défini
- [ ] Données accessibles via connection
- [ ] Requêtes SQL fonctionnelles

---

### US-03 : Transformation dbt
| Élément | Description |
|---------|-------------|
| **En tant que** | Data Analyst |
| **Je veux** | Transformer les données avec dbt |
| **Afin de** | Préparer les données pour le ML |
| **Story Points** | 5 |
| **Assignee** | **Layla** |
| **Labels** | analytics, sprint-1 |

**Critères d'acceptation :**
- [ ] Models staging créés
- [ ] Models mart créés
- [ ] dbt run fonctionnel
- [ ] Documentation dbt générée

---

### US-04 : Tests de qualité automatisés
| Élément | Description |
|---------|-------------|
| **En tant que** | Data Quality Engineer |
| **Je veux** | Automatiser les tests de qualité |
| **Afin de** | Garantir l'intégrité des données |
| **Story Points** | 3 |
| **Assignee** | **Sanae** |
| **Labels** | data-quality, sprint-1 |

**Critères d'acceptation :**
- [ ] Tests de complétude
- [ ] Tests de validité
- [ ] Tests de cohérence
- [ ] Rapport qualité généré

---

## 🟢 SPRINT 2 - MLOps & Qualité (03/07 → 07/07)

### US-05 : Intégration des modèles ML
| Élément | Description |
|---------|-------------|
| **En tant que** | ML Engineer |
| **Je veux** | Intégrer les modèles existants |
| **Afin de** | Les utiliser dans le nouveau pipeline |
| **Story Points** | 5 |
| **Assignee** | **Khadija** |
| **Labels** | ml, sprint-2 |

**Critères d'acceptation :**
- [ ] Modèles chargés depuis models/
- [ ] Prétraitement adapté
- [ ] Prédictions fonctionnelles
- [ ] Tests des modèles

---

### US-06 : MLflow Experiment Tracking
| Élément | Description |
|---------|-------------|
| **En tant que** | MLOps Engineer |
| **Je veux** | Tracker les expérimentations avec MLflow |
| **Afin de** | Comparer les performances des modèles |
| **Story Points** | 5 |
| **Assignee** | **Kaoutar** |
| **Labels** | mlops, sprint-2 |

**Critères d'acceptation :**
- [ ] Serveur MLflow configuré
- [ ] Log des paramètres
- [ ] Log des métriques
- [ ] Interface accessible

---

### US-07 : Model Registry MLflow
| Élément | Description |
|---------|-------------|
| **En tant que** | MLOps Engineer |
| **Je veux** | Versionner les modèles |
| **Afin de** | Gérer les différentes versions |
| **Story Points** | 3 |
| **Assignee** | **Kaoutar** |
| **Labels** | mlops, sprint-2 |

**Critères d'acceptation :**
- [ ] Modèles enregistrés
- [ ] Versions gérées
- [ ] Promotion possible
- [ ] Chargement des modèles

---

### US-08 : Data Lineage
| Élément | Description |
|---------|-------------|
| **En tant que** | Data Quality Engineer |
| **Je veux** | Tracer le lineage des données |
| **Afin de** | Comprendre le flux des données |
| **Story Points** | 3 |
| **Assignee** | **Sanae** |
| **Labels** | data-quality, sprint-2 |

**Critères d'acceptation :**
- [ ] Traçabilité source → cible
- [ ] Documentation transformations
- [ ] Visualisation du lineage
- [ ] Data Contract défini

---

## 🟡 SPRINT 3 - API & Déploiement (07/07 → 10/07)

### US-09 : API FastAPI
| Élément | Description |
|---------|-------------|
| **En tant que** | Backend Developer |
| **Je veux** | Créer une API REST avec FastAPI |
| **Afin de** | Exposer les prédictions |
| **Story Points** | 8 |
| **Assignee** | **Rajae** |
| **Labels** | backend, sprint-3 |

**Critères d'acceptation :**
- [ ] Endpoint /predict/crop
- [ ] Endpoint /predict/yield
- [ ] Endpoint /predict/full
- [ ] Endpoint /health
- [ ] Documentation Swagger

---

### US-10 : Dockerisation
| Élément | Description |
|---------|-------------|
| **En tant que** | DevOps |
| **Je veux** | Containeriser l'application avec Docker |
| **Afin de** | Garantir la reproductibilité |
| **Story Points** | 3 |
| **Assignee** | **Rajae** |
| **Labels** | devops, sprint-3 |

**Critères d'acceptation :**
- [ ] Dockerfile pour l'API
- [ ] docker-compose.yml
- [ ] Conteneurs fonctionnels
- [ ] Variables d'environnement

---

### US-11 : Orchestration Dagster
| Élément | Description |
|---------|-------------|
| **En tant que** | Data Engineer |
| **Je veux** | Orchestrer tout le pipeline avec Dagster |
| **Afin de** | Automatiser l'ensemble |
| **Story Points** | 5 |
| **Assignee** | **Douaa** |
| **Labels** | orchestration, sprint-3 |

**Critères d'acceptation :**
- [ ] Pipeline d'ingestion
- [ ] Pipeline de transformation
- [ ] Pipeline d'entraînement
- [ ] Orchestration complète

---

## 🔴 SPRINT 4 - CI/CD & Finalisation (10/07 → 12/07)

### US-12 : CI/CD GitHub Actions
| Élément | Description |
|---------|-------------|
| **En tant que** | DevOps |
| **Je veux** | Mettre en place CI/CD avec GitHub Actions |
| **Afin de** | Automatiser les déploiements |
| **Story Points** | 5 |
| **Assignee** | **Douaa** |
| **Labels** | devops, sprint-4 |

**Critères d'acceptation :**
- [ ] Tests automatiques
- [ ] Build Docker
- [ ] Vérification du code
- [ ] Déploiement automatisé

---

### US-13 : Monitoring des modèles
| Élément | Description |
|---------|-------------|
| **En tant que** | MLOps Engineer |
| **Je veux** | Monitorer les modèles en production |
| **Afin de** | Détecter la dérive |
| **Story Points** | 5 |
| **Assignee** | **Kaoutar** |
| **Labels** | mlops, sprint-4 |

**Critères d'acceptation :**
- [ ] Métriques de performance
- [ ] Dashboards
- [ ] Alerts configurés
- [ ] Data drift détecté

---

### US-14 : Interface utilisateur Bootstrap
| Élément | Description |
|---------|-------------|
| **En tant que** | Utilisateur |
| **Je veux** | Une interface simple |
| **Afin de** | Utiliser facilement l'API |
| **Story Points** | 8 |
| **Assignee** | **Toute l'équipe** |
| **Labels** | frontend, sprint-4 |

**Critères d'acceptation :**
- [ ] Interface Bootstrap
- [ ] Formulaires
- [ ] Affichage des résultats
- [ ] Responsive

---

## 📊 RÉSUMÉ DES STORY POINTS

| Sprint | Total SP |
|--------|----------|
| Sprint 1 | 16 SP |
| Sprint 2 | 16 SP |
| Sprint 3 | 16 SP |
| Sprint 4 | 18 SP |
| **Total** | **66 SP** |

---

## 👥 RÉPARTITION DES TÂCHES PAR PERSONNE

| Personne | Rôle | Issues | Sprint |
|----------|------|--------|--------|
| **Ouiam** | Data Engineer | US-01, US-02 | Sprint 1 |
| **Layla** | Data Analyst | US-03 | Sprint 1 |
| **Sanae** | Data Quality | US-04, US-08 | Sprint 1 & 2 |
| **Khadija** | ML Engineer | US-05 | Sprint 2 |
| **Kaoutar** | MLOps | US-06, US-07, US-13 | Sprint 2 & 4 |
| **Rajae** | Backend/DevOps | US-09, US-10 | Sprint 3 |
| **Douaa** | Orchestration/CI/CD | US-11, US-12 | Sprint 3 & 4 |
| **Toute l'équipe** | Frontend | US-14 | Sprint 4 |
