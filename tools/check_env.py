"""Small environment checker for troubleshooting TF and backends.

Usage:
    python tools/check_env.py

Prints whether TensorFlow is installed, its version, and whether torch is available.
"""
import importlib.util
import importlib

print('Environment check')
print('=================')

# TensorFlow
tf_spec = importlib.util.find_spec('tensorflow')
if tf_spec is None:
    print('TensorFlow: NOT INSTALLED')
else:
    try:
        tf = importlib.import_module('tensorflow')
        print('TensorFlow: INSTALLED, version =', getattr(tf, '__version__', 'unknown'))
    except Exception as e:
        print('TensorFlow: import failed ->', e)

# PyTorch
torch_spec = importlib.util.find_spec('torch')
if torch_spec is None:
    print('PyTorch: NOT INSTALLED')
else:
    try:
        torch = importlib.import_module('torch')
        print('PyTorch: INSTALLED, version =', getattr(torch, '__version__', 'unknown'))
    except Exception as e:
        print('PyTorch: import failed ->', e)

# sentence-transformers backend check
s_spec = importlib.util.find_spec('sentence_transformers')
if s_spec is None:
    print('sentence-transformers: NOT INSTALLED')
else:
    try:
        st = importlib.import_module('sentence_transformers')
        print('sentence-transformers: INSTALLED, version =', getattr(st, '__version__', 'unknown'))
    except Exception as e:
        print('sentence-transformers: import failed ->', e)

print('\nDone')
