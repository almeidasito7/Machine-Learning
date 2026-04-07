import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.pipeline import run_full_pipeline

result = run_full_pipeline()

print("\nPipeline Result:\n")
print(result)