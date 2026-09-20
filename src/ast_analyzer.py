import os
import sys
import ast
from typing import Dict, List, Set, Tuple

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class ASTDependencyAnalyzer:
    """
    Parses Python Abstract Syntax Trees (AST) across source files and tests
    to establish fine-grained symbol-level dependency graphs for test selection.
    """

    def __init__(self, repo_dir: str = "."):
        self.repo_dir = repo_dir
        self.source_symbols: Dict[str, Set[str]] = {}
        self.test_dependencies: Dict[str, Set[str]] = {}
        self._build_dependency_map()

    def _extract_symbols_from_file(self, fpath: str) -> Set[str]:
        """Extracts class, function, and variable names defined in a Python file."""
        symbols = set()
        if not os.path.exists(fpath):
            return symbols
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=fpath)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    symbols.add(node.name)
        except Exception:
            pass
        return symbols

    def _extract_referenced_symbols_from_test(self, test_path: str) -> Set[str]:
        """Extracts all imported and referenced symbols inside a test file."""
        references = set()
        if not os.path.exists(test_path):
            return references
        try:
            with open(test_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=test_path)
            for node in ast.walk(tree):
                # Check imports (from app.x import Foo)
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        references.add(alias.name)
                elif isinstance(node, ast.Name):
                    references.add(node.id)
                elif isinstance(node, ast.Attribute):
                    references.add(node.attr)
        except Exception:
            pass
        return references

    def _build_dependency_map(self):
        """Scans app/ and tests/ to construct the AST call dependency graph."""
        app_dir = os.path.join(self.repo_dir, "app")
        tests_dir = os.path.join(self.repo_dir, "tests")

        # Scan app source files
        if os.path.exists(app_dir):
            for root, _, files in os.walk(app_dir):
                for file in files:
                    if file.endswith(".py"):
                        fpath = os.path.join(root, file)
                        rel_path = os.path.relpath(fpath, self.repo_dir).replace("\\", "/")
                        self.source_symbols[rel_path] = self._extract_symbols_from_file(fpath)

        # Scan test files
        if os.path.exists(tests_dir):
            for file in os.listdir(tests_dir):
                if file.startswith("test_") and file.endswith(".py"):
                    tpath = os.path.join(tests_dir, file)
                    rel_test_path = os.path.relpath(tpath, self.repo_dir).replace("\\", "/")
                    self.test_dependencies[rel_test_path] = self._extract_referenced_symbols_from_test(tpath)

    def resolve_impacted_tests(self, changed_files: List[str]) -> Dict[str, any]:
        """
        Maps changed source files to candidate tests based on AST symbol references.
        """
        selected_tests: Set[str] = set()
        matched_symbols: Set[str] = set()
        affects_infrastructure = False

        for fpath in changed_files:
            norm = fpath.replace("\\", "/")
            if any(core in norm.lower() for core in ["requirements.txt", "setup.py", ".github", "database"]):
                affects_infrastructure = True

            symbols = self.source_symbols.get(norm, set())
            if not symbols:
                # Re-parse if newly modified
                full_path = os.path.join(self.repo_dir, norm)
                symbols = self._extract_symbols_from_file(full_path)
            
            matched_symbols.update(symbols)

            # Match symbols against test dependencies
            for test_file, test_refs in self.test_dependencies.items():
                if symbols.intersection(test_refs):
                    selected_tests.add(test_file)

        # Safety fallback
        all_tests = sorted(list(self.test_dependencies.keys()))
        if affects_infrastructure or not selected_tests:
            return {
                "selected_tests": all_tests,
                "is_full_suite": True,
                "impacted_symbols": sorted(list(matched_symbols)),
                "reason": "Infrastructure change or unresolved AST dependencies (safety fallback triggered)"
            }

        return {
            "selected_tests": sorted(list(selected_tests)),
            "is_full_suite": len(selected_tests) == len(all_tests),
            "impacted_symbols": sorted(list(matched_symbols)),
            "reason": f"AST dependency match for symbols: {', '.join(sorted(list(matched_symbols))[:5])}"
        }

if __name__ == "__main__":
    analyzer = ASTDependencyAnalyzer()
    print("AST Source Symbols Detected:", {k: len(v) for k, v in analyzer.source_symbols.items()})
    print("AST Test References:", {k: len(v) for k, v in analyzer.test_dependencies.items()})
    res = analyzer.resolve_impacted_tests(["app/authentication/auth_service.py"])
    print("\nImpacted Tests for auth_service.py:", res)
