import os, sys
# Make the canonical skill source importable from the dev/ test suite.
SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skill"))
if SKILL_DIR not in sys.path:
    sys.path.insert(0, SKILL_DIR)
