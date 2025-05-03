# Guidelines for Portable POSIX `sh` Scripting

> **Design it as a modular and flexible system focused on reusability and extendability. Encapsulate logic in well-defined, independent functions for clarity and maintainability. Follow clear and consistent naming conventions:**

- Use `snake_case` for all public/user-facing variables and functions.
- Prefix private/internal variables and functions with `__double_underscore` for clarity and encapsulation.
- Employ `__key__` for internal mechanisms that require special handling, following a dunder-style convention.

**1. Core Principles (Remain the Same, but Execution Differs):**

- **Modularity:** Break logic into functions.
- **Reusability:** Write generic functions; consider library files.
- **Readability:** Prioritize clear names, formatting, and comments.
- **Maintainability:** Structure code logically.
- **Robustness:** Implement error handling and validation diligently.
- **Explicitness:** Be clear; avoid obscure tricks. POSIX `sh` often _requires_ more explicit steps.
- **Portability:** Adhere strictly to POSIX `sh` standards.

**2. Script Structure & Boilerplate:**

- **Shebang:** Always use `#!/bin/sh`.
- **Strict Mode (`set` options):** Use POSIX-compliant strict options:

  ```sh
  set -eu
  # set -e: Exit immediately if a simple command exits with a non-zero status.
  # set -u: Treat unset variables and parameters (other than $@ or $*) as an error when performing parameter expansion.
  # NOTE: 'set -o pipefail' is NOT POSIX compliant and should NOT be used for portable scripts. Pipeline errors must be checked manually if needed beyond the exit status of the last command.
  ```

- **Header Comments:** Essential for explaining purpose, usage, etc.
- **Main Function:** Still recommended. Encapsulate main logic in `main() { ... }` and call via `main "$@"`. This structure is POSIX compliant.

  ```sh
  main() {
    # Main script logic here
    # Parse options, call other functions, etc.
    echo "Script execution started."
    input_file="$1" # Assign positional parameters early
    _process_file "$input_file"
    echo "Script execution finished."
  }

  # Call main function, passing all script arguments
  main "$@"
  ```

**3. Naming Conventions (Style Choice - Unchanged):**

- **Public Functions & Variables:** `snake_case`.

  ```sh
  process_data() { ... }
  input_file="data.txt"
  ```

- **Internal/Helper Functions & Variables:** `_leading_underscore_snake_case`. Signals intent for internal use.

  ```sh
  _validate_input() { ... }
  # Note: Variable scope differs significantly - see below.
  _temp_file="/tmp/myscript.$$" # Simple temp file naming
  ```

- **Constants & Exported Environment Variables:** `UPPER_SNAKE_CASE`. Use `readonly` (POSIX compliant).

  ```sh
  readonly MAX_RETRIES=3
  readonly DEFAULT_OUTPUT_DIR="/tmp/output"
  export LOG_LEVEL="INFO"
  ```

- **Consistency:** Crucial for readability.

**4. Functions (Key Differences from Bash):**

- **No `local` Keyword:** POSIX `sh` does **not** have a `local` keyword. Variables defined inside functions are **global** by default. This requires extreme care.

  - **Workaround 1: Subshell `()`:** Define the function body within parentheses `()` instead of braces `{}`. This runs the function in a subshell, effectively localizing _variable assignments_ made within it (they don't affect the parent shell). However, functions defined this way cannot modify the parent shell's variables (except globals already exported), and each call incurs the cost of starting a subshell.

    ```sh
    _helper_in_subshell() ( # Note the parentheses
      # Variables assigned here are local to the subshell
      _sub_var="$1"
      echo "Subshell var: $_sub_var"
      # Cannot easily modify variables in the calling scope
    )
    ```

  - **Workaround 2: Careful Naming & `unset`:** Use unique names (e.g., prefixed with the function name `_funcname_var`) and explicitly `unset` them at the end of the function. This is error-prone.
  - **Recommendation:** Use the subshell `()` method for functions that don't need to modify the caller's state directly. Pass data via arguments and `stdout`. For functions needing to modify state, use very careful global variable management with clear naming (`_internal_state_var`).

- **Parameters:** Accessed via `$1`, `$2`, ... (POSIX compliant). Assign to variables (remembering scope issues).
- **Return Values:** Use `return <number>` (0-255) for status codes. Print data to `stdout`. Messages to `stderr` (`>&2`). (POSIX compliant).
- **Function Definition:** Use `func_name() { ... }` syntax (POSIX compliant). Avoid the `function` keyword.

**5. Readability & Style (Adaptations for POSIX):**

- **Indentation, Comments, Quoting:** Same principles apply. _Always_ quote variables (`"$variable"`) and command substitutions (`"$(command)"`).
- **Use `[ ... ]` or `test`:** The `[[ ... ]]` construct is **not** POSIX. Use the standard `[ ... ]` command (which is often a built-in alias for `test`).

  - Be meticulous with quoting _inside_ `[ ... ]`.
  - Use `-a` (AND) and `-o` (OR) with caution, as their behavior depends on precedence and is sometimes confusing. Prefer separate `[ ]` tests connected by shell logical operators `&&` and `||`.

    ```sh
    # POSIX compliant tests
    if [ "$count" -gt 5 ] && [ "$name" = "required" ]; then
      echo "Condition met."
    fi

    if [ -z "$input" ]; then
      echo "Error: Input is empty." >&2
      return 1 # Or exit 1 if not in a function
    fi
    ```

- **Use `$(...)`:** POSIX compliant and preferred over backticks `` `...` `` for command substitution.
- **Use `shellcheck`:** Lint scripts with `shellcheck -s sh your_script.sh` to catch non-POSIX constructs and common errors.

**6. Modularity & Reusability:**

- **Library Files:** Use the POSIX `.` command (dot) to include library files: `. ./my_lib.sh`. Ensure library files are safe to include multiple times if necessary (guard against re-definitions or use functions).
- **Avoid Globals:** Even more critical without `local`. Rely on function arguments, `stdout`, and return codes. Use subshells `()` for functions where possible.

**7. Error Handling:**

- **`set -eu`:** Use as a baseline.
- **Explicit Checks:** Check exit status `$?` where needed, especially after pipelines since `-o pipefail` is unavailable.

  ```sh
  command1 | command2
  status=$?
  if [ "$status" -ne 0 ]; then
    echo "Error: Pipeline failed with status $status" >&2
    # Handle error
  fi
  ```

- **Validate Input & Informative Messages:** Essential. Print errors to `stderr`.
- **Cleanup:** Use `trap` with POSIX signals (`EXIT`, `INT`, `TERM`, `HUP`, etc.).

  ```sh
  # POSIX trap example
  cleanup() {
    echo "Cleaning up temporary file: ${_temp_file}" >&2
    rm -f -- "$_temp_file"
  }
  trap cleanup EXIT INT TERM HUP

  _temp_file="/tmp/myscript.$$" # Process ID for basic uniqueness
  touch "$_temp_file" # Create it if needed by logic
  # ... rest of script ...
  ```

**8. POSIX `sh` Limitations to Remember:**

- **No `local`:** Manage scope carefully (subshells `()` or naming conventions).
- **No Arrays:** Use delimited strings and tools like `cut`, `awk`, or `sed`, or manage items via positional parameters (`set -- $list; item1=$1; item2=$2 ...`).
- **No `[[ ... ]]`:** Use `[ ... ]` or `test` with careful quoting.
- **Limited String Manipulation:** Rely on `${var#pattern}`, `${var##pattern}`, `${var%pattern}`, `${var%%pattern}` and external tools (`sed`, `awk`, `cut`, `expr`, `tr`) for complex tasks.
- **Arithmetic:** Use `$((...))` (POSIX) or the external `expr` command. Avoid Bash `((...))`.

  ```sh
  count=$(($count + 1)) # POSIX arithmetic expansion
  length=$(expr "$string" : '.*') # POSIX expr for string length
  ```

- **No Process Substitution (`<(...)`, `>(...)`):** Use temporary files.
- **No Brace Expansion (`{a,b,c}`):** Generate sequences explicitly or with tools like `seq` (if available, though not strictly POSIX required).

---

Writing portable POSIX `sh` scripts requires more effort and careful testing than writing Bash scripts, but results in code that runs reliably on a wider range of systems. Focus on the fundamentals, leverage standard Unix utilities, and test thoroughly, especially regarding variable scope and conditional expressions.
