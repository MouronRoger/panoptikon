# Pyright Migration Plan - Post Phase 4
# Overview
With Phase 4 (Database Foundation) complete, now is an opportune time to migrate from mypy to Pyright for type checking. This migration will provide improved performance, better compatibility with VS Code, and enhanced type checking capabilities that align with the project's strict quality requirements.
# Strategic Considerations
**1** **Timing**: Phase 4 completion marks a stable point in development with database architecture solidified
**2** **Project Size**: Codebase is mature enough to benefit from Pyright's faster checking but not yet too large for migration to be cumbersome
**3** **Developer Experience**: Pyright offers better IDE integration, especially with VS Code
**4** **Technical Debt**: Migration now prevents accumulating type-checking inconsistencies

⠀Migration Plan
### 1. Assessment & Setup (1 day)
* **Install Pyright** ### bash
pip install pyright


* **Create Initial Configuration** Create pyrightconfig.json in project root: ### json
{
* "include": ["src", "tests", "scripts"],
* "exclude": [
* "**/__pycache__",
* ".git",
* ".github",
* ".mypy_cache",
* ".pytest_cache",
* ".ruff_cache",
* ".venv",
* "actions-runner/externals"
* ],
* "typeCheckingMode": "basic",
* "pythonVersion": "3.9",
* "reportMissingImports": true,
* "reportMissingTypeStubs": false,
* "reportUnknownMemberType": false,
* "useLibraryCodeForTypes": true,
* "strict": [],
* "stubPath": "src/panoptikon/typings"
* }



⠀2. Baseline Evaluation (0.5 day)
* **Run Initial Scan** ### bash
pyright


* **Document Current Issues**
  * Create pyright-migration.md to track issues and patterns
  * Identify recurring error types
  * Assess severity and impact on development

⠀3. Configuration Tuning (0.5 day)
* **Align with Current Standards** Adjust pyrightconfig.json to match mypy strictness: ### json
{
* "include": ["src", "tests", "scripts"],
* "exclude": [
* "**/__pycache__",
* ".git",
* ".github",
* ".mypy_cache",
* ".pytest_cache",
* ".ruff_cache",
* ".venv",
* "actions-runner/externals"
* ],
* "typeCheckingMode": "strict",
* "pythonVersion": "3.9",
* "reportMissingImports": true,
* "reportMissingTypeStubs": false,
* "reportUnknownMemberType": false,
* "useLibraryCodeForTypes": true,
* "strictListInference": true,
* "strictDictionaryInference": true,
* "strictSetInference": true,
* "strictParameterNoneValue": true,
* "enableTypeIgnoreComments": true,
* "reportMissingParameterType": "error",
* "reportUnknownParameterType": "error",
* "reportUnknownArgumentType": "error",
* "reportUnknownLambdaType": "error",
* "reportUnknownVariableType": "error",
* "reportUnknownMemberType": "error",
* "reportMissingTypeArgument": "error",
* "reportInvalidTypeVarUse": "error",
* "reportCallInDefaultInitializer": "error",
* "reportUntypedFunctionDecorator": "error",
* "reportUntypedClassDecorator": "error",
* "reportUntypedBaseClass": "error",
* "reportUntypedNamedTuple": "error",
* "reportUnusedImport": "warning",
* "reportUnusedVariable": "warning",
* "reportUnusedClass": "warning",
* "reportUnusedFunction": "warning",
* "stubPath": "src/panoptikon/typings"
* }


* **PyObjC Handling** Add module-specific settings for PyObjC and other external libraries: ### json
{
* "ignore": [
* "objc",
* "Foundation", 
* "AppKit", 
* "Cocoa"
* ]
* }



⠀4. Incremental Adoption (2 days)
* **Update CI Pipeline**
  * Add Pyright to GitHub Actions workflow
  * Run both mypy and Pyright temporarily with Pyright in warning-only mode
  * Update .pre-commit-config.yaml to include Pyright
* **Fix Critical Issues**
  * Prioritize errors over warnings
  * Address systemic issues first (e.g., common annotation patterns)
  * Focus on core modules first, then supporting code

⠀5. Developer Setup (0.5 day)
* **Update Editor Configuration**
  * Add VS Code settings to workspace
  * Configure Pyright settings in .vscode/settings.json
  * Add recommended extensions to .vscode/extensions.json
* **Document Patterns**
  * Update coding standards with Pyright-specific guidance
  * Document common idioms and solutions

⠀6. Migration Completion (1.5 days)
* **Switch to Strict Mode**
  * Set typeCheckingMode to strict in pyrightconfig.json
  * Resolve remaining errors
  * Cleanup any technical debt introduced during migration
* **Remove mypy**
  * Remove mypy config files
  * Update CI pipeline to remove mypy
  * Remove mypy from dev dependencies
  * Clean up any mypy-specific type comments

⠀7. Documentation (0.5 day)
* **Update Project Documentation**
  * Document Pyright configuration choices
  * Update contributor docs with type checking guidance
  * Add Pyright usage to onboarding materials
* **Release Notes**
  * Document migration in CHANGELOG.md
  * Note any behavioral changes or issues

⠀Timeline
* **Total Estimated Time**: 6.5 developer days
* **Recommended Approach**:
  * Complete Steps 1-3 together (2 days)
  * Steps 4-5 can be done incrementally (2.5 days)
  * Steps 6-7 should be done together (2 days)

⠀Benefits
**1** **Performance**: Pyright is significantly faster than mypy, especially for large codebases
**2** **IDE Integration**: Better VS Code experience with inline error reporting
**3** **Modern Features**: Improved support for recent Python typing features
**4** **Cross-Platform**: Consistent experience across all development environments
**5** **Strict Mode**: More comprehensive type checking than current mypy config

⠀Risks & Mitigations
| Risk | Mitigation |
|:-:|:-:|
| Breaking CI pipeline | Temporary dual checking with fail-open on Pyright |
| Developer learning curve | Document common patterns and provide examples |
| PyObjC compatibility | Configure ignore patterns for external libraries |
| Inconsistent annotations | Identify and document project-specific idioms |
# Pre-Commit Configuration
Update .pre-commit-config.yaml to include:

### yaml
- repo: https://github.com/microsoft/pyright
  rev: 1.1.353
  hooks:
  - id: pyright
# GitHub Actions Integration
Add to existing workflow:

### yaml
pyright:
  name: Pyright Type Check
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
        pip install pyright
    - name: Run pyright
      run: pyright
# Conclusion
Migrating to Pyright after Phase 4 completion is a strategic decision that provides significant benefits with manageable effort. The migration will strengthen the project's type safety, improve developer experience, and maintain the strict quality requirements established in the project specification.
