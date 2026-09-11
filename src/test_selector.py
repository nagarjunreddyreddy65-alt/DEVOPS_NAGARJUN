import os
from typing import List, Dict, Set

class ChangeAwareTestSelector:
    """
    Selects relevant candidate tests based on modified module paths and files.
    Applies safety fallbacks if critical modules (e.g. database or shared core) are altered.
    """

    MODULE_TEST_MAP: Dict[str, List[str]] = {
        "authentication": ["tests/test_auth.py"],
        "payment": ["tests/test_payment.py"],
        "reporting": ["tests/test_reporting.py"],
        "database": ["tests/test_database.py", "tests/test_auth.py", "tests/test_payment.py"]  # DB affects multiple modules
    }

    ALL_TESTS: List[str] = [
        "tests/test_auth.py",
        "tests/test_payment.py",
        "tests/test_reporting.py",
        "tests/test_database.py"
    ]

    def __init__(self, repo_dir: str = "."):
        self.repo_dir = repo_dir

    def select_tests_for_changes(
        self,
        changed_files: List[str],
        force_full_suite: bool = False
    ) -> Dict[str, any]:
        """
        Maps changed files to required test files.
        If force_full_suite is True, returns all tests.
        """
        if force_full_suite or not changed_files:
            return {
                "selected_tests": list(self.ALL_TESTS),
                "is_full_suite": True,
                "reason": "Full suite forced or no specific change files detected"
            }

        selected_set: Set[str] = set()
        matched_modules: Set[str] = set()
        affects_core_infrastructure = False

        for fpath in changed_files:
            normalized = fpath.replace("\\", "/").lower()
            
            # If critical config, workflow, root or requirement changed -> full suite
            if any(k in normalized for k in ["requirements.txt", "setup.py", ".github", "database"]):
                affects_core_infrastructure = True

            for module_name, test_paths in self.MODULE_TEST_MAP.items():
                if module_name in normalized:
                    matched_modules.add(module_name)
                    selected_set.update(test_paths)

        # Conservative safety check: if core infrastructure is touched, fallback to full suite
        if affects_core_infrastructure or not selected_set:
            return {
                "selected_tests": list(self.ALL_TESTS),
                "is_full_suite": True,
                "matched_modules": list(matched_modules),
                "reason": "Core infrastructure change or unmapped file detected (safety fallback)"
            }

        return {
            "selected_tests": sorted(list(selected_set)),
            "is_full_suite": len(selected_set) == len(self.ALL_TESTS),
            "matched_modules": sorted(list(matched_modules)),
            "reason": f"Change-aware mapping for modules: {', '.join(sorted(matched_modules))}"
        }

if __name__ == "__main__":
    selector = ChangeAwareTestSelector()
    res1 = selector.select_tests_for_changes(["app/authentication/auth_service.py"])
    print("Auth change selection:", res1)
    res2 = selector.select_tests_for_changes(["app/database/connection.py"])
    print("DB change selection:", res2)
