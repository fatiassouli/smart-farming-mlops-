# 🌾 Smart Farming MLOps - Vision du Projet

---

## 🎯 Problématique

L'agriculture moderne fait face à des défis majeurs :
- Changement climatique et sécheresses
- Raréfaction des ressources en eau
- Dégradation des sols
- Pression démographique croissante

Notre équipe a développé un **prototype Smart Farming** qui démontre qu'il est possible de :
- Recommander des cultures avec une **précision de 99,32%**
- Prédire les rendements avec un **R² de 0,98**

**Mais ce prototype n'est pas industrialisable** :
- ❌ Pas de pipeline automatisé
- ❌ Pas de versionnement des modèles
- ❌ Pas d'API accessible
- ❌ Pas de monitoring
- ❌ Pas de CI/CD

---

## 💡 Objectif du projet

Transformer le prototype en une **solution industrielle complète** en appliquant :

| Concept | Outils |
|---------|--------|
| **DataOps** | dlt, DuckDB, dbt, Dagster |
| **MLOps** | MLflow, Model Registry, Monitoring |
| **DevOps** | FastAPI, Docker, CI/CD |

---

## 👥 Utilisateurs cibles

| Utilisateur | Besoin | Fréquence |
|-------------|--------|-----------|
| **Agriculteurs** | Recommandation de cultures | Quotidienne |
| **Coopératives** | Planification production | Saisonnière |
| **Ministère** | Politiques agricoles | Annuelle |
| **Chercheurs** | Analyse de données | Variable |

---

## 🏗️ Architecture cible
┌─────────────────────────────────────────────────────────────────────┐
│ SMART FARMING MLOps │
├─────────────────────────────────────────────────────────────────────┤
│ │
│ 📊 Kaggle / FAO │
│ │ │
│ ▼ │
│ 🔄 dlt (Ingestion automatisée) │
│ │ │
│ ▼ │
│ 🗄️ DuckDB (Stockage local) │
│ │ │
│ ▼ │
│ 🔧 dbt (Transformation) │
│ │ │
│ ▼ │
│ 🤖 Modèles ML (Scikit-learn) │
│ │ │
│ ▼ │
│ 📈 MLflow (Tracking & Registry) │
│ │ │
│ ▼ │
│ 🌐 FastAPI (API REST) │
│ │ │
│ ▼ │
│ 🐳 Docker (Conteneurisation) │
│ │ │
│ ▼ │
│ 🚀 GitHub Actions (CI/CD) │
│ │
└─────────────────────────────────────────────────────────────────────┘

---

## 📊 Bénéfices attendus

| Bénéfice | Impact |
|----------|--------|
| **Automatisation** | Pipeline 100% automatisé |
| **Traçabilité** | Data Lineage complet |
| **Versionnement** | Modèles versionnés |
| **Accessibilité** | API pour tous les utilisateurs |
| **Monitoring** | Détection de dérive en continu |
| **Reproductibilité** | CI/CD garanti |

---

## 🗓️ Planning

| Sprint | Dates | Focus |
|--------|-------|-------|
| **Sprint 1** | 30/06 → 03/07 | Ingestion & Transformation |
| **Sprint 2** | 03/07 → 07/07 | MLOps & Qualité |
| **Sprint 3** | 07/07 → 10/07 | API & Déploiement |
| **Sprint 4** | 10/07 → 12/07 | CI/CD & Finalisation |

---

## 👥 Équipe

| Rôle | Personne |
|------|----------|
| Product Owner | Personne 1 |
| Scrum Master | Personne 1 |
| Data Engineer | Personne 2 |
| Data Analyst | Personne 3 |
| Data Quality | Personne 4 |
| ML Engineer | Personne 5 |
| MLOps | Personne 6 |
| Backend/DevOps | Personne 7 |
| Orchestration/CI/CD | Personne 8 |

---

## 📚 Documentation

- [Product Backlog](PRODUCT_BACKLOG.md)
- [Sprint Planning](SPRINT_PLANNING.md)
- [Architecture](ARCHITECTURE.md)

---

*Document créé le 30/06/2026*
