# ChromaDB Schema Analysis Tools

This directory contains tools for analyzing and visualizing the ChromaDB database schema and contents.

## Scripts

### 1. `analyze_chroma_db.py` - Full Analysis & Visualization
**Purpose**: Comprehensive analysis of ChromaDB schema with visual charts saved as PNG images.

**Features**:
- Database structure analysis
- Document distribution charts
- Metadata field analysis
- Content statistics
- Schema health checks
- Visual charts saved as high-resolution PNG files

**Usage**:
```bash
python scripts/analyze_chroma_db.py
```

**Generates**:
- `visualizations/chroma_overview.png` - Collection overview and summary statistics
- `visualizations/document_analysis.png` - Document length distributions and patterns
- `visualizations/metadata_analysis.png` - Metadata field analysis and completeness
- `visualizations/chroma_schema_report.json` - Detailed JSON report
- `visualizations/chroma_schema_report.txt` - Human-readable text report

### 2. `check_chroma_schema.py` - Quick Terminal Check
**Purpose**: Lightweight terminal-based schema overview without generating files.

**Features**:
- Quick database connectivity check
- Collection and document counts
- Metadata field summary
- Schema health validation
- No file dependencies (suitable for CI/CD)

**Usage**:
```bash
python scripts/check_chroma_schema.py
```

## Output Examples

### Terminal Output (Quick Check)
```
ChromaDB Quick Schema Check
========================================
Database Path: /path/to/chroma_storage
Timestamp: 2025-10-15 13:36:07

Collections Found: 2
----------------------------------------
1. Collection: resumes
   Documents: 8
   Metadata Fields: preprocessed, user_id
   Sample IDs: user_5, user_6, user_7
   Doc Lengths: min=729, max=1798, avg=893

2. Collection: jobs
   Documents: 0
   Metadata Fields: None

----------------------------------------
Total Documents: 8

Schema Health Check:
✅ Database contains collections and documents
✅ Expected collection 'resumes' found
✅ Expected collection 'jobs' found
```

### Generated Schema Report (Text)
```
ChromaDB Schema Analysis Report
==================================================

Analysis Timestamp: 2025-10-15T13:34:58.917300
Total Collections: 2
Total Documents: 8

1. Collection: resumes
   Document Count: 8
   Metadata Fields: user_id, preprocessed
   ID Patterns: {'user': 8}
   Document Length Stats:
     - Min: 729
     - Max: 1798
     - Mean: 893.1
     - Median: 757.5
   Sample IDs: user_5, user_6, user_7

2. Collection: jobs
   Document Count: 0
   Metadata Fields: None
   ID Patterns: []
```

## Visualizations

The analysis script generates several types of visualizations:

### 1. Collection Overview (`chroma_overview.png`)
- Document count by collection (bar chart)
- Document distribution (pie chart)
- Metadata fields heatmap
- Summary statistics table

### 2. Document Analysis (`document_analysis.png`)
- Document length distribution by collection (box plots)
- Overall document length histogram
- ID pattern distribution
- Collection size comparison

### 3. Metadata Analysis (`metadata_analysis.png`)
- Metadata field frequency across collections
- Unique values per metadata field
- Metadata completeness heatmap
- Numeric metadata statistics

## Dependencies

### For Full Analysis (`analyze_chroma_db.py`)
- `matplotlib` - Chart generation
- `seaborn` - Statistical visualizations
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `chromadb` - Database access

### For Quick Check (`check_chroma_schema.py`)
- `chromadb` - Database access only

## Installation

Install required packages:
```bash
pip install matplotlib seaborn pandas numpy
```

Note: ChromaDB should already be installed as part of the main application requirements.

## Troubleshooting

### Common Issues

1. **NumPy Version Conflicts**
   ```bash
   pip install "numpy<2.0"
   ```

2. **ChromaDB Connection Errors**
   - Ensure `chroma_storage` directory exists
   - Check database permissions
   - Verify ChromaDB installation

3. **Missing Visualizations**
   - Check if `scripts/visualizations/` directory was created
   - Ensure sufficient disk space
   - Verify matplotlib backend configuration

### Schema Health Warnings

- **⚠️ No collections found**: Database may be empty or corrupted
- **⚠️ Collections exist but no documents found**: Collections initialized but no data imported
- **⚠️ Expected collection 'X' not found**: Missing standard collections (resumes/jobs)

## Integration

### In Development
Add to your development scripts:
```bash
# Quick health check
python scripts/check_chroma_schema.py

# Full analysis for debugging
python scripts/analyze_chroma_db.py
```

### In CI/CD Pipeline
```yaml
- name: Check ChromaDB Schema
  run: python scripts/check_chroma_schema.py
```

### In Monitoring
Set up periodic runs to monitor database growth and health.

## Schema Evolution

These tools help track:
- Collection growth over time
- Metadata field additions/changes
- Document size trends
- Schema health and integrity

For database migrations, run before and after analysis to verify changes.