# Archive Directory

This directory contains old, deprecated, or backup files that are no longer actively used in the project but kept for reference.

## Archived Files

### Test Files
- `comprehensive_test.py` - Comprehensive system test (replaced by modular tests in `tests/`)
- `status_report.py` - Old status reporting script

### Backup Files
- `resume_backup_20251009_012931.txt` - Resume text backup from October 9, 2024

### Deprecated Apps
- `simple_app.py` - Simple Flask app prototype (replaced by full app structure)

## Purpose

These files are archived rather than deleted to:
- Maintain project history
- Reference old implementations
- Preserve backup data
- Document development evolution

## Usage

⚠️ **Warning**: These files are no longer maintained and may not work with the current codebase.

If you need to reference old code:
```bash
# View archived file
cat archive/simple_app.py

# Compare with current implementation
diff archive/simple_app.py main.py
```

## Migration Notes

- **October 2024**: Initial prototypes archived
- **December 2024**: Comprehensive tests split into modular test files
- All current functionality is in `main.py`, `app/`, and `scripts/`
