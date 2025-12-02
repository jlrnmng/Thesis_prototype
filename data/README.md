# Data Directory

This directory is intended for machine learning models, datasets, and data files used by the Hirely application.

## Purpose

Store data files that are:
- 🤖 Machine learning models
- 📊 Training datasets
- 📈 Analytics data
- 🗃️ Reference data (e.g., skill taxonomies, job categories)

## Current Contents

```
data/
└── (currently empty - ready for future data files)
```

## Potential Use Cases

### 1. Machine Learning Models

**K-Means Clustering Model:**
```
data/
├── kmeans_job_clustering.pkl      # Trained k-means model
├── job_clusters_metadata.json     # Cluster descriptions
└── scaler.pkl                     # Feature scaler
```

**Skills Classification:**
```
data/
├── skill_classifier.pkl           # Skills extraction model
├── skills_vocabulary.json         # Known skills database
└── tech_stack_mappings.json      # Technology relationships
```

### 2. Reference Data

**Job Categories:**
```
data/
├── job_categories.json            # Standard job categories
├── industry_taxonomy.json         # Industry classifications
└── seniority_levels.json         # Job levels (Junior, Mid, Senior)
```

**Skills Data:**
```
data/
├── programming_languages.json     # List of programming languages
├── frameworks.json                # Web frameworks, libraries
├── tools.json                     # Development tools
└── certifications.json            # Professional certifications
```

### 3. Training Datasets

**Resume Datasets:**
```
data/
├── training_resumes/
│   ├── software_engineer_resumes.csv
│   ├── data_scientist_resumes.csv
│   └── designer_resumes.csv
└── job_descriptions/
    ├── tech_jobs.csv
    └── non_tech_jobs.csv
```

### 4. Analytics Data

**Usage Statistics:**
```
data/
├── analytics/
│   ├── match_accuracy.csv        # Matching performance metrics
│   ├── user_engagement.csv       # User activity logs
│   └── conversion_rates.csv      # Application conversion data
```

## File Formats

### Recommended Formats

- **Models:** `.pkl` (pickle), `.joblib`, `.h5` (Keras), `.pt` (PyTorch)
- **Structured Data:** `.json`, `.csv`, `.parquet`
- **Configuration:** `.yaml`, `.json`
- **Binary Data:** `.npy` (NumPy arrays)

### Example: Saving/Loading Models

```python
import pickle
import joblib

# Save model
with open('data/kmeans_model.pkl', 'wb') as f:
    pickle.dump(model, f)

# Load model
with open('data/kmeans_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Or using joblib (recommended for large models)
joblib.dump(model, 'data/kmeans_model.joblib')
model = joblib.load('data/kmeans_model.joblib')
```

## Security & Privacy

### ⚠️ Important Considerations:

**DO NOT store:**
- ❌ User personal data (PII)
- ❌ Passwords or API keys
- ❌ Unencrypted sensitive information
- ❌ Large files without compression

**DO store:**
- ✅ Trained ML models
- ✅ Anonymized datasets
- ✅ Reference/lookup data
- ✅ Configuration files
- ✅ Cached computations

## Git Configuration

### .gitignore Settings

```gitignore
# Large data files
data/*.csv
data/*.pkl
data/*.joblib
data/*.h5

# Keep directory structure
!data/.gitkeep

# Keep small reference files
!data/*_reference.json
!data/*_config.yaml
```

### Version Control for ML Models

For large model files, consider:
- **Git LFS** (Large File Storage)
- **DVC** (Data Version Control)
- **Cloud storage** (S3, GCS, Azure Blob)

## Data Management

### Adding New Data Files

1. **Determine file type and purpose**
2. **Choose appropriate format**
3. **Document in this README**
4. **Update .gitignore if needed**
5. **Add loading utilities in scripts/**

### Data Versioning

```
data/
├── models/
│   ├── v1/
│   │   └── classifier_v1.pkl
│   ├── v2/
│   │   └── classifier_v2.pkl
│   └── production/
│       └── classifier.pkl  # Symlink to current version
```

### Data Validation

```python
import os
import hashlib

def validate_data_file(filepath, expected_hash=None):
    """Verify data file integrity"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")
    
    if expected_hash:
        with open(filepath, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        if file_hash != expected_hash:
            raise ValueError("Data file hash mismatch!")
    
    return True
```

## Integration with Thesis

### K-Means Clustering

The sibling folder `k-means_model_training/` contains:
```
k-means_model_training/
├── k-means_model_train.ipynb     # Training notebook
└── recruitment_job_desc.csv      # Training dataset
```

**Integration plan:**
1. Train model in notebook
2. Export model to `data/kmeans_model.pkl`
3. Load in `matching_service.py` for clustering
4. Use cluster_id in matching algorithm

### Future ML Integration

```python
# Example: Loading k-means model
from matching_service import MatchingService

class EnhancedMatchingService(MatchingService):
    def __init__(self):
        super().__init__()
        self.kmeans_model = self._load_kmeans_model()
    
    def _load_kmeans_model(self):
        import joblib
        return joblib.load('data/kmeans_job_clustering.joblib')
    
    def cluster_job(self, job_description):
        # Use k-means to assign cluster
        features = self.extract_features(job_description)
        cluster_id = self.kmeans_model.predict([features])[0]
        return cluster_id
```

## Related Directories

- `../k-means_model_training/` - Model training notebooks
- `../chroma_storage/` - Vector embeddings storage
- `../instance/` - Database files
- `../scripts/` - Data processing scripts

## Maintenance

### Regular Tasks
- **Weekly:** Check file sizes, compress if needed
- **Monthly:** Archive old model versions
- **Quarterly:** Clean up unused datasets

### Backup Strategy
```bash
# Backup data directory
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/

# Backup to cloud (example)
aws s3 sync data/ s3://hirely-data-backup/data/
```

## Documentation

When adding new data files, document:
- **Purpose:** What is this data for?
- **Source:** Where did it come from?
- **Format:** File format and schema
- **Size:** Approximate file size
- **Usage:** How to load and use it
- **Update Frequency:** How often it changes

---

**Last Updated:** December 2, 2025
**Status:** Ready for future data files
