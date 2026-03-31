#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
    Check QGIS API compatibility of the plugin code against a target QGIS
    version range by cross-referencing actual usage with the official PyQGIS
    HTML documentation.

    Downloads and caches the PyQGIS docs for every version in the target
    range, then checks each class/method usage against all of them.

    How to use:

        python tools/qgis_compatibility_checker.py
        python tools/qgis_compatibility_checker.py --min-version 3.16
        python tools/qgis_compatibility_checker.py --min-version 3.16 --max-version 3.32
        python tools/qgis_compatibility_checker.py --list-rules

    Authors: S. Sampere
    Python: 3.7+
    Created: 2026-03-30
    License: GPL 3
"""

# #############################################################################
# ########## Libraries #############
# ##################################

import ast
import argparse
import re
import sys
from configparser import ConfigParser
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile

# #############################################################################
# ########## Globals ###############
# ##################################

DIR_PLUGIN_ROOT = Path(__file__).parent.parent
PLG_METADATA_FILE = DIR_PLUGIN_ROOT.resolve() / "metadata.txt"
DOC_CACHE_DIR = Path(__file__).parent / ".pyqgis-doc-cache"

DOCS_URL_PATTERN = (
    "https://github.com/qgis/pyqgis-api-docs-builder"
    "/releases/download/{version}/pyqgis-docs-{version}.zip"
)

# Modules we check (maps qgis.X to the doc subfolder name)
QGIS_MODULES = {
    "qgis.core": "core",
    "qgis.gui": "gui",
}

# Directories / patterns to skip when scanning plugin sources
SKIP_DIRS = {"build", ".venv", ".venv-qt6", "tests", "docs", "__pycache__", "_auth"}
SKIP_FILES = {"resources_rc.py", "pyqt5_to_pyqt6.py"}

RULES = {
    "QC001": {
        "summary": "Class not found in QGIS version docs",
        "severity": "error",
    },
    "QC002": {
        "summary": "Method not found in QGIS version docs",
        "severity": "error",
    },
    "QC003": {
        "summary": "Method added in a later version than the minimum supported",
        "severity": "warning",
    },
    "QC004": {
        "summary": "Method deprecated in a version within the supported range",
        "severity": "info",
    },
}


# #############################################################################
# ########## Version helpers #######
# ##################################


def read_metadata_versions(metadata_path):
    """Read qgisMinimumVersion and qgisMaximumVersion from metadata.txt."""
    cfg = ConfigParser()
    cfg.read(str(metadata_path), encoding="utf-8")
    min_v = cfg.get("general", "qgisMinimumVersion", fallback="3.16")
    max_v = cfg.get("general", "qgisMaximumVersion", fallback="3.44")
    # Strip patch-level (e.g. "3.44.99" -> "3.44")
    min_v = ".".join(min_v.split(".")[:2])
    max_v = ".".join(max_v.split(".")[:2])
    return min_v, max_v


def parse_version(v):
    """Parse 'X.Y' into a tuple (X, Y) for comparison."""
    parts = v.split(".")
    return (int(parts[0]), int(parts[1]))


def enumerate_versions(min_version, max_version):
    """List all QGIS versions between min and max (inclusive, step 2).

    QGIS 3.x releases use even minor versions: 3.16, 3.18, 3.20, ...
    """
    min_major, min_minor = parse_version(min_version)
    max_major, max_minor = parse_version(max_version)

    versions = []
    major = min_major
    minor = min_minor
    # Ensure we start on an even minor
    if minor % 2 != 0:
        minor += 1

    while (major, minor) <= (max_major, max_minor):
        versions.append(f"{major}.{minor}")
        minor += 2
        if minor > 98 and major == min_major:
            major += 1
            minor = 0

    return versions


# #############################################################################
# ########## AST Scanner ###########
# ##################################


class QgisApiUsage:
    """Represents a usage of a QGIS API symbol found in plugin code."""

    def __init__(self, filepath, line, col, module, class_name, method_name=None):
        self.filepath = filepath
        self.line = line
        self.col = col
        self.module = module  # e.g. "core", "gui"
        self.class_name = class_name
        self.method_name = method_name  # None for class-only imports

    def __repr__(self):
        if self.method_name:
            return f"{self.class_name}.{self.method_name} @ {self.filepath}:{self.line}"
        return f"{self.class_name} @ {self.filepath}:{self.line}"


def scan_file(filepath, plugin_root):
    """Scan a Python file for QGIS API usage. Returns list of QgisApiUsage."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError) as exc:
        print(f"  WARNING: Could not parse {filepath}: {exc}", file=sys.stderr)
        return []

    rel_path = str(filepath.relative_to(plugin_root))
    usages = []

    # Step 1: collect imports from qgis.core / qgis.gui
    # Maps local name -> (module_subfolder, original_class_name)
    imported_classes = {}

    # Build set of line numbers inside except/try-except blocks (fallback imports)
    except_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            for lineno in range(node.lineno, node.end_lineno + 1):
                except_lines.add(lineno)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in QGIS_MODULES:
            # Skip imports inside except blocks (compatibility fallbacks)
            if node.lineno in except_lines:
                continue
            module_sub = QGIS_MODULES[node.module]
            for alias in node.names:
                local_name = alias.asname if alias.asname else alias.name
                imported_classes[local_name] = (module_sub, alias.name)
                usages.append(
                    QgisApiUsage(
                        rel_path, node.lineno, node.col_offset,
                        module_sub, alias.name
                    )
                )

    if not imported_classes:
        return usages

    # Step 2: collect method calls
    # Track simple variable assignments for basic type inference
    # e.g. project = QgsProject.instance() -> project is QgsProject
    var_types = {}  # variable_name -> (module_sub, class_name)

    for node in ast.walk(tree):
        # Detect: ClassName.method() where ClassName is an imported QGIS class
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            func = node.func
            method_name = func.attr

            # Case 1: direct static call — ClassName.method()
            if isinstance(func.value, ast.Name) and func.value.id in imported_classes:
                module_sub, class_name = imported_classes[func.value.id]
                usages.append(
                    QgisApiUsage(
                        rel_path, node.lineno, node.col_offset,
                        module_sub, class_name, method_name
                    )
                )

            # Case 2: inferred variable call — var.method()
            elif isinstance(func.value, ast.Name) and func.value.id in var_types:
                module_sub, class_name = var_types[func.value.id]
                usages.append(
                    QgisApiUsage(
                        rel_path, node.lineno, node.col_offset,
                        module_sub, class_name, method_name
                    )
                )

        # Track assignments for type inference:
        # var = ClassName(...) or var = ClassName.method(...)
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                value = node.value
                # var = ClassName(...)
                if (isinstance(value, ast.Call)
                        and isinstance(value.func, ast.Name)
                        and value.func.id in imported_classes):
                    var_types[target.id] = imported_classes[value.func.id]
                # var = ClassName.method(...)
                elif (isinstance(value, ast.Call)
                      and isinstance(value.func, ast.Attribute)
                      and isinstance(value.func.value, ast.Name)
                      and value.func.value.id in imported_classes):
                    var_types[target.id] = imported_classes[value.func.value.id]

    return usages


def discover_files(plugin_root):
    """Find all .py files to scan in the plugin."""
    files = []
    for py_file in plugin_root.rglob("*.py"):
        rel_parts = py_file.relative_to(plugin_root).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        if py_file.name in SKIP_FILES:
            continue
        if py_file.name.startswith("ui_") and py_file.name.endswith(".py"):
            continue
        files.append(py_file)
    return sorted(files)


# #############################################################################
# ########## Doc Fetcher ###########
# ##################################


def ensure_doc_zip(version):
    """Download the pyqgis docs ZIP for the given version if not cached."""
    DOC_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    zip_name = f"pyqgis-docs-{version}.zip"
    zip_path = DOC_CACHE_DIR / zip_name

    if zip_path.exists():
        return zip_path

    url = DOCS_URL_PATTERN.format(version=version)
    print(f"  Downloading PyQGIS {version} docs ...")
    try:
        urlretrieve(url, str(zip_path))
        size_mb = zip_path.stat().st_size // 1024 // 1024
        print(f"    -> {zip_path.name} ({size_mb} MB)")
    except Exception as exc:
        print(f"    ERROR: Failed to download: {exc}", file=sys.stderr)
        if zip_path.exists():
            zip_path.unlink()
        return None

    return zip_path


def find_html_in_zip(zf, version, module_sub, class_name):
    """Find the HTML path for a class inside the ZIP.

    Older doc ZIPs use '{version}/module/Class.html',
    newer ones use 'build/{version}/module/Class.html'.
    """
    candidates = [
        f"build/{version}/{module_sub}/{class_name}.html",
        f"{version}/{module_sub}/{class_name}.html",
    ]
    for path in candidates:
        if path in zf.namelist():
            return path
    return None


# #############################################################################
# ########## Doc Parser ############
# ##################################


class MethodInfo:
    """Information about a method extracted from the HTML docs."""

    def __init__(self, name, added_in=None, deprecated_since=None):
        self.name = name
        self.added_in = added_in  # version string or None
        self.deprecated_since = deprecated_since  # version string or None

    def __repr__(self):
        parts = [self.name]
        if self.added_in:
            parts.append(f"added={self.added_in}")
        if self.deprecated_since:
            parts.append(f"deprecated={self.deprecated_since}")
        return f"MethodInfo({', '.join(parts)})"


class PyQGISDocParser(HTMLParser):
    """Parse a PyQGIS HTML doc page to extract method names and version info.

    Handles both old and new Sphinx doc formats:
      - "New in version X.XX." (older docs)
      - "Added in version X.XX." (newer docs)
      - "Deprecated since version X.XX:" (all versions, though sometimes broken)

    Also extracts parent class names from the "Bases:" section for inheritance
    resolution.
    """

    def __init__(self, full_class_id):
        super().__init__()
        # e.g. "qgis.core.QgsProject"
        self.class_id_prefix = full_class_id + "."
        self.methods = {}  # method_name -> MethodInfo
        self.parent_classes = []  # e.g. ["QgsMapLayer", "QgsExpressionContextGenerator"]

        # Parser state
        self._current_method = None
        self._in_versionadded = False
        self._in_deprecated = False
        self._capture_text = ""
        self._in_bases = False
        self._bases_text = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Detect <dt id="qgis.core.QgsProject.methodName">
        if tag == "dt":
            dt_id = attrs_dict.get("id", "")
            if dt_id.startswith(self.class_id_prefix):
                method_name = dt_id[len(self.class_id_prefix):]
                if method_name and "." not in method_name:
                    self._current_method = method_name
                    if method_name not in self.methods:
                        self.methods[method_name] = MethodInfo(method_name)

        # Detect <span class="versionmodified ...">
        css_class = attrs_dict.get("class", "")
        if tag == "span" and "versionmodified" in css_class:
            if "added" in css_class or "new" in css_class:
                self._in_versionadded = True
                self._capture_text = ""
            elif "deprecated" in css_class:
                self._in_deprecated = True
                self._capture_text = ""

    def handle_endtag(self, tag):
        if tag == "span" and self._in_versionadded:
            self._in_versionadded = False
            version = self._extract_version(self._capture_text)
            if version and self._current_method and self._current_method in self.methods:
                self.methods[self._current_method].added_in = version

        elif tag == "span" and self._in_deprecated:
            self._in_deprecated = False
            version = self._extract_version(self._capture_text)
            if version and self._current_method and self._current_method in self.methods:
                self.methods[self._current_method].deprecated_since = version

    def handle_data(self, data):
        if self._in_versionadded or self._in_deprecated:
            self._capture_text += data

    @staticmethod
    def _extract_version(text):
        """Extract version number from 'Added in version 3.16.' or similar."""
        match = re.search(r"(\d+\.\d+)", text)
        return match.group(1) if match else None


def _extract_parent_classes(html_content):
    """Extract parent class names from the 'Bases:' section of the HTML.

    Looks for patterns like:
      Bases: <a ...>QgsMapLayer</a>, <a ...>QgsExpressionContextGenerator</a>
    """
    # Find the "Bases:" section and extract linked class names
    bases_match = re.search(r"Bases:\s*(.*?)</p>", html_content, re.DOTALL)
    if not bases_match:
        return []
    bases_html = bases_match.group(1)
    # Extract class names from <span class="pre">ClassName</span> or plain text
    class_names = re.findall(r"<span class=\"pre\">(Qgs\w+)</span>", bases_html)
    return class_names


def parse_class_doc(zip_path, version, module_sub, class_name):
    """Parse a class's HTML doc from the ZIP.

    Returns (methods_dict, parent_class_names) or (None, []) if the class
    page does not exist in this version.
    """
    try:
        with ZipFile(str(zip_path)) as zf:
            html_path = find_html_in_zip(zf, version, module_sub, class_name)
            if html_path is None:
                return None, []
            content = zf.read(html_path).decode("utf-8")
    except (KeyError, Exception):
        return None, []

    full_class_id = f"qgis.{module_sub}.{class_name}"
    parser = PyQGISDocParser(full_class_id)
    parser.feed(content)
    parent_classes = _extract_parent_classes(content)
    return parser.methods, parent_classes


# #############################################################################
# ########## Checker / Reporter ####
# ##################################


class Finding:
    """A compatibility finding."""

    def __init__(self, filepath, line, col, rule_id, severity, message):
        self.filepath = filepath
        self.line = line
        self.col = col
        self.rule_id = rule_id
        self.severity = severity
        self.message = message

    def __str__(self):
        return (
            f"{self.filepath}:{self.line}:{self.col}: "
            f"{self.rule_id} [{self.severity}] {self.message}"
        )


def check_compatibility(usages, versions, version_zips):
    """Cross-reference plugin API usages against ALL PyQGIS doc versions.

    Returns a list of Finding.
    """
    findings = []

    # Cache: (version, module, class) -> (methods_dict or None, parent_names)
    doc_cache = {}

    def get_class_doc(version, module_sub, class_name):
        key = (version, module_sub, class_name)
        if key not in doc_cache:
            zip_path = version_zips[version]
            doc_cache[key] = parse_class_doc(
                zip_path, version, module_sub, class_name
            )
        return doc_cache[key]

    def find_method_in_hierarchy(version, module_sub, class_name, method_name,
                                 visited=None):
        """Look up a method on a class, falling back to parent classes.

        Returns MethodInfo or None.
        """
        if visited is None:
            visited = set()
        if class_name in visited:
            return None
        visited.add(class_name)

        methods, parents = get_class_doc(version, module_sub, class_name)
        if methods is not None and method_name in methods:
            return methods[method_name]

        # Try parent classes (same module)
        for parent in parents:
            result = find_method_in_hierarchy(
                version, module_sub, parent, method_name, visited
            )
            if result is not None:
                return result
        return None

    # Deduplicate: for each (class, method) pair, only report once
    reported = set()

    for usage in usages:
        # For class-only imports: check existence in each version
        if usage.method_name is None:
            missing_versions = []
            for ver in versions:
                if ver not in version_zips:
                    continue
                methods, _ = get_class_doc(ver, usage.module, usage.class_name)
                if methods is None:
                    missing_versions.append(ver)

            if missing_versions:
                report_key = (usage.filepath, usage.class_name, None, "QC001")
                if report_key not in reported:
                    reported.add(report_key)
                    findings.append(Finding(
                        usage.filepath, usage.line, usage.col,
                        "QC001", "error",
                        f"Class '{usage.class_name}' (qgis.{usage.module}) "
                        f"not found in QGIS: {', '.join(missing_versions)}"
                    ))

        # For method calls: check existence and annotations in each version
        else:
            missing_versions = []
            added_in_info = None
            deprecated_versions = []

            for ver in versions:
                if ver not in version_zips:
                    continue
                methods, _ = get_class_doc(ver, usage.module, usage.class_name)
                if methods is None:
                    # Class doesn't exist — already covered by class-level check
                    missing_versions.append(ver)
                    continue

                # Look up method with inheritance fallback
                method_info = find_method_in_hierarchy(
                    ver, usage.module, usage.class_name, usage.method_name
                )

                if method_info is None:
                    missing_versions.append(ver)
                else:
                    if method_info.added_in and added_in_info is None:
                        added_in_info = method_info.added_in
                    if method_info.deprecated_since:
                        deprecated_versions.append(
                            (ver, method_info.deprecated_since)
                        )

            # Report missing method
            if missing_versions:
                report_key = (
                    usage.filepath, usage.class_name, usage.method_name, "QC002"
                )
                if report_key not in reported:
                    reported.add(report_key)
                    msg = (
                        f"'{usage.class_name}.{usage.method_name}()' "
                        f"not found in QGIS: {', '.join(missing_versions)}"
                    )
                    if added_in_info:
                        msg += f" (added in {added_in_info})"
                    findings.append(Finding(
                        usage.filepath, usage.line, usage.col,
                        "QC002", "error", msg
                    ))

            # Report deprecation
            if deprecated_versions:
                report_key = (
                    usage.filepath, usage.class_name, usage.method_name, "QC004"
                )
                if report_key not in reported:
                    reported.add(report_key)
                    _, depr_ver = deprecated_versions[0]
                    findings.append(Finding(
                        usage.filepath, usage.line, usage.col,
                        "QC004", "info",
                        f"'{usage.class_name}.{usage.method_name}()' "
                        f"deprecated since QGIS {depr_ver}"
                    ))

    return findings


SEVERITY_ORDER = {"error": 3, "warning": 2, "info": 1}


def filter_findings(findings, min_severity):
    """Filter findings by minimum severity level."""
    threshold = SEVERITY_ORDER.get(min_severity, 1)
    return [f for f in findings if SEVERITY_ORDER.get(f.severity, 0) >= threshold]


# #############################################################################
# ########## CLI ###################
# ##################################


SEVERITY_ICON = {"error": "!!!", "warning": "!", "info": "~"}


def format_text(findings, errors, warnings, infos):
    """Format findings as plain text (flake8-style)."""
    if not findings:
        return "No compatibility issues found."

    lines = ["=" * 70]
    for f in findings:
        lines.append(str(f))
    lines.append("=" * 70)
    lines.append(f"\nSummary: {errors} error(s), {warnings} warning(s), {infos} info(s)")
    return "\n".join(lines)


def format_markdown(findings, min_version, max_version, versions,
                    n_classes, n_methods, n_files,
                    errors, warnings, infos):
    """Format findings as a Markdown report."""
    lines = []
    lines.append("# QGIS Compatibility Report")
    lines.append("")
    lines.append(f"**QGIS range** : {min_version} - {max_version}  ")
    lines.append(f"**Versions checked** : {', '.join(versions)}  ")
    lines.append(f"**Files scanned** : {n_files}  ")
    lines.append(f"**QGIS classes found** : {n_classes}  ")
    lines.append(f"**Method calls found** : {n_methods}")
    lines.append("")

    if not findings:
        lines.append("## Result")
        lines.append("")
        lines.append("No compatibility issues found.")
        return "\n".join(lines)

    # Summary
    lines.append("## Summary")
    lines.append("")
    if errors:
        lines.append(f"- **{errors} error(s)** : class or method missing in one or more versions")
    if warnings:
        lines.append(f"- **{warnings} warning(s)** : added after minimum version")
    if infos:
        lines.append(f"- **{infos} info(s)** : deprecated in supported range")
    lines.append("")

    # Findings table
    lines.append("## Findings")
    lines.append("")
    lines.append("| Severity | Location | Rule | Details |")
    lines.append("|----------|----------|------|---------|")
    for f in findings:
        sev = SEVERITY_ICON.get(f.severity, "?")
        location = f"{f.filepath}:{f.line}"
        lines.append(f"| {sev} {f.severity} | `{location}` | {f.rule_id} | {f.message} |")
    lines.append("")

    # Rules reference
    lines.append("## Rules reference")
    lines.append("")
    lines.append("| Rule | Severity | Description |")
    lines.append("|------|----------|-------------|")
    for rule_id, info in sorted(RULES.items()):
        lines.append(f"| {rule_id} | {info['severity']} | {info['summary']} |")

    return "\n".join(lines)


def list_rules():
    """Print all available rules."""
    print("Available compatibility rules:\n")
    for rule_id, info in sorted(RULES.items()):
        print(f"  {rule_id}  [{info['severity']:>7s}]  {info['summary']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Check QGIS Python API compatibility of the plugin code."
    )
    parser.add_argument(
        "--min-version",
        help="Minimum QGIS version to check against (default: from metadata.txt)",
    )
    parser.add_argument(
        "--max-version",
        help="Maximum QGIS version to check against (default: from metadata.txt)",
    )
    parser.add_argument(
        "--severity",
        choices=["info", "warning", "error"],
        default="warning",
        help="Minimum severity to report (default: warning)",
    )
    parser.add_argument(
        "--path",
        help="Plugin root directory (default: parent of tools/)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "markdown"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--output",
        help="Write report to file instead of stdout",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="List all available rules and exit",
    )
    args = parser.parse_args()

    if args.list_rules:
        list_rules()
        return 0

    # Resolve plugin root
    plugin_root = Path(args.path).resolve() if args.path else DIR_PLUGIN_ROOT.resolve()

    # Read versions
    metadata_file = plugin_root / "metadata.txt"
    default_min, default_max = read_metadata_versions(metadata_file)
    min_version = args.min_version or default_min
    max_version = args.max_version or default_max

    # Enumerate all QGIS versions in range
    versions = enumerate_versions(min_version, max_version)

    print("QGIS Compatibility Checker")
    print(f"  Plugin root : {plugin_root}")
    print(f"  QGIS range  : {min_version} - {max_version}")
    print(f"  Versions    : {', '.join(versions)}")
    print(f"  Severity    : >= {args.severity}")
    print()

    # Discover files
    files = discover_files(plugin_root)
    print(f"Scanning {len(files)} Python file(s)...")

    # Scan for API usages
    all_usages = []
    for f in files:
        usages = scan_file(f, plugin_root)
        all_usages.extend(usages)

    method_usages = [u for u in all_usages if u.method_name is not None]
    unique_classes = {(u.module, u.class_name) for u in all_usages}
    print(
        f"  Found {len(unique_classes)} QGIS class(es), "
        f"{len(method_usages)} method call(s)"
    )
    print()

    # Download docs for all versions
    print(f"Ensuring docs for {len(versions)} version(s)...")
    version_zips = {}
    for ver in versions:
        zip_path = ensure_doc_zip(ver)
        if zip_path:
            version_zips[ver] = zip_path
        else:
            print(f"  WARNING: Skipping QGIS {ver} (docs unavailable)")
    print()

    if not version_zips:
        print("ERROR: No docs available for any version.", file=sys.stderr)
        return 2

    # Check compatibility against all versions
    print("Checking compatibility...")
    findings = check_compatibility(all_usages, versions, version_zips)
    findings = filter_findings(findings, args.severity)

    # Sort by severity (errors first), then file, then line
    findings.sort(
        key=lambda f: (-SEVERITY_ORDER.get(f.severity, 0), f.filepath, f.line)
    )

    errors = sum(1 for f in findings if f.severity == "error")
    warnings = sum(1 for f in findings if f.severity == "warning")
    infos = sum(1 for f in findings if f.severity == "info")

    # Generate report
    if args.format == "markdown":
        report = format_markdown(
            findings, min_version, max_version, versions,
            len(unique_classes), len(method_usages), len(files),
            errors, warnings, infos,
        )
    else:
        report = format_text(findings, errors, warnings, infos)

    # Output
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"\nReport written to {args.output}")
    else:
        print()
        print(report)

    if errors > 0:
        return 2
    if warnings > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
