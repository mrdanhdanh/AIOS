"""Create a fresh governed task folder from the standard _TEMPLATE.

This proves the standard AIOS job layout (plans/ scripts/ logs/) works
end-to-end on a brand-new task, not just on the pre-existing TASK-222.
"""
import os
import shutil

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TEMPLATE = os.path.join(REPO, "aios", "progress", "tasks", "_TEMPLATE")
TARGET = os.path.join(REPO, "aios", "progress", "tasks", "TASK-VERIFY-001")


def main() -> None:
    # Copy the standard lifecycle template into a new task folder.
    if os.path.isdir(TARGET):
        shutil.rmtree(TARGET)
    shutil.copytree(TEMPLATE, TARGET)
    # Ensure the job folder has the mandated functional subfolders.
    for sub in ("plans", "scripts", "logs"):
        os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), sub), exist_ok=True)
    print(f"created task folder: {TARGET}")


if __name__ == "__main__":
    main()
