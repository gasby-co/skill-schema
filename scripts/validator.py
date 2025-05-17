import json
import os
import glob
import argparse

# Third-party libraries - ensure they are installed
# pip install jsonschema PyLD
try:
    import jsonschema
except ImportError:
    print("Error: jsonschema library not found. Please install it using 'pip install jsonschema'")
    exit(1)

try:
    from pyld import jsonld
except ImportError:
    print("Error: PyLD library not found. Please install it using 'pip install PyLD'")
    exit(1)

def validate_json_syntax(file_path):
    """
    Validates the basic JSON syntax of a given file.

    Args:
        file_path (str): The path to the JSON or JSON-LD file.

    Returns:
        tuple: (bool, str) where bool is True if syntax is valid, False otherwise,
               and str is an error message if syntax is invalid, or an empty string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True, ""
    except json.JSONDecodeError as e:
        return False, f"Syntax error: {e.msg} (line {e.lineno}, column {e.colno})"
    except FileNotFoundError:
        return False, "Error: File not found."
    except Exception as e:
        return False, f"An unexpected error occurred during JSON syntax validation: {str(e)}"

def validate_jsonld_structure(file_path):
    """
    Validates the JSON-LD structure of a given file using pyld.

    Args:
        file_path (str): The path to the JSON-LD file.

    Returns:
        tuple: (bool, str) where bool is True if structure is valid, False otherwise,
               and str is an error message if invalid, or an empty string.
    """
    # First, ensure basic JSON syntax is valid
    is_syntax_valid, syntax_error_message = validate_json_syntax(file_path)
    if not is_syntax_valid:
        # Return the syntax error, as JSON-LD processing can't proceed
        return False, syntax_error_message

    try:
        # Load the document again for pyld processing
        with open(file_path, 'r', encoding='utf-8') as f:
            doc = json.load(f)
        
        # Attempt to expand the JSON-LD document
        # This will fetch contexts and process the structure
        # For local file contexts, a custom documentLoader might be needed if not resolvable by default.
        # Assuming contexts are URLs or resolvable relative paths for now.
        # TODO: Implement a robust documentLoader for local contexts if needed.
        # Custom document loader for local files
        def local_document_loader(url, options=None):
            # Convert potential URL to local path relative to 'contexts/' directory
            # This is a simplified loader. A more robust one would handle various URL schemes
            # and map them to a local cache or specific directory structure.
            if url.startswith("https://raw.githubusercontent.com/ModelContext/skill-schema/main/contexts/"):
                context_file_name = url.split('/')[-1]
                local_path = os.path.join(os.path.dirname(__file__), '..', 'contexts', context_file_name) # Assumes script is in scripts/
            elif os.path.exists(url): # If it's already a local path that exists
                 local_path = url
            elif os.path.exists(os.path.join(os.path.dirname(file_path), url)): # Relative to the file being processed
                local_path = os.path.join(os.path.dirname(file_path), url)
            else: # Fallback for contexts specified as just filenames, look in project's contexts/ dir
                local_path = os.path.join(os.path.dirname(__file__), '..', 'contexts', url)


            if os.path.exists(local_path):
                with open(local_path, 'r', encoding='utf-8') as f_context:
                    context_doc = json.load(f_context)
                return {
                    'contextUrl': None, # No remote context URL as it's local
                    'documentUrl': 'file://' + os.path.abspath(local_path),
                    'document': context_doc
                }
            raise jsonld.JsonLdError(f"Context URL {url} could not be resolved to a local file.", "jsonld.LoadContextError")

        jsonld.expand(doc, {'documentLoader': local_document_loader})
        return True, ""
    except jsonld.JsonLdError as e:
        return False, f"JSON-LD processing error: {str(e)}"
    except FileNotFoundError: # Should have been caught by validate_json_syntax
        return False, "Error: File not found (should not happen here)."
    except Exception as e:
        return False, f"An unexpected error occurred during JSON-LD validation: {str(e)}"

def map_example_to_schema(example_file_path, base_dir="."):
    """
    Determines the corresponding schema file for a given example file based on naming conventions.
    Example: "examples/foo_example.json" -> "schemas/foo.schema.json"
             "examples/bar_example.jsonld" -> "schemas/bar.schema.json"

    Args:
        example_file_path (str): The path to the example file.
        base_dir (str): The base directory of the project, used for resolving schema path.

    Returns:
        str or None: The path to the schema file if found and exists, otherwise None.
    """
    file_name = os.path.basename(example_file_path)
    schema_base_name = None

    if file_name.endswith("_example.json"):
        schema_base_name = file_name[:-len("_example.json")]
    elif file_name.endswith("_example.jsonld"):
        schema_base_name = file_name[:-len("_example.jsonld")]
    else:
        # Not following the expected naming convention for an example file
        return None

    if not schema_base_name:
        return None

    # Construct schema path relative to the base_dir/schemas/
    # Assumes 'examples' and 'schemas' are direct children of base_dir
    schema_file_name = schema_base_name + ".schema.json"
    schema_path = os.path.join(base_dir, 'schemas', schema_file_name)
    
    if os.path.exists(schema_path):
        return schema_path
    else:
        return None

def validate_with_schema(example_file_path, schema_file_path):
    """
    Validates an example JSON/JSON-LD file against a given JSON schema.

    Args:
        example_file_path (str): Path to the example data file.
        schema_file_path (str): Path to the JSON schema file.

    Returns:
        tuple: (bool, str) where bool is True if valid, False otherwise,
               and str is an error message if invalid or an error occurred.
    """
    # First, ensure the example file itself has valid JSON syntax
    is_syntax_valid, syntax_error_message = validate_json_syntax(example_file_path)
    if not is_syntax_valid:
        return False, syntax_error_message # Return the specific syntax error

    try:
        with open(example_file_path, 'r', encoding='utf-8') as f:
            example_data = json.load(f)
    except Exception as e: # Should be caught by validate_json_syntax, but as a fallback
        return False, f"Error reading example file {example_file_path}: {str(e)}"

    try:
        with open(schema_file_path, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
    except FileNotFoundError:
        return False, f"Schema file not found: {schema_file_path}"
    except json.JSONDecodeError as e:
        return False, f"Syntax error in schema file {schema_file_path}: {e.msg} (line {e.lineno}, col {e.colno})"
    except Exception as e:
        return False, f"Error reading schema file {schema_file_path}: {str(e)}"

    try:
        jsonschema.validate(instance=example_data, schema=schema_data)
        return True, ""
    except jsonschema.exceptions.ValidationError as e:
        error_path = "->".join(map(str, e.path))
        return False, f"Schema validation error: {e.message} (at path: '{error_path}')"
    except jsonschema.exceptions.SchemaError as e:
        # This indicates the schema itself is invalid
        return False, f"Invalid schema definition in {schema_file_path}: {e.message}"
    except Exception as e:
        return False, f"An unexpected error occurred during schema validation: {str(e)}"

def check_context_utilization(example_file_path, base_dir="."):
    """
    Verifies that an example file is using the JSON-LD context correctly.
    - Checks if the @context value matches the expected context URL.
    - Attempts to expand the JSON-LD document to ensure terms resolve.

    Args:
        example_file_path (str): Path to the example JSON/JSON-LD file.
        base_dir (str): The base directory of the project.

    Returns:
        tuple: (bool, str) where bool is True if context is utilized correctly,
               False otherwise, and str is an error/warning message or empty string.
    """
    # BASE_CONTEXT_URL = "https://raw.githubusercontent.com/ModelContext/skill-schema/main/contexts/"
    # Using local paths now, so base URL for comparison is not strictly needed in the same way,
    # but we'll construct expected local paths.
    # Assuming 'contexts' directory is at the root of the project, sibling to 'scripts'
    PROJECT_ROOT_FOR_CONTEXTS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


    # Ensure basic JSON syntax is valid first
    is_syntax_valid, syntax_error_message = validate_json_syntax(example_file_path)
    if not is_syntax_valid:
        return False, syntax_error_message

    try:
        with open(example_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return False, f"Error reading example file {example_file_path}: {str(e)}"

    actual_context = data.get('@context')
    if not actual_context:
        return False, "Missing '@context' key in the example file."

    # Determine expected context URL
    file_name = os.path.basename(example_file_path)
    expected_context_name = None
    if file_name == "code_classification_example.json":
        expected_context_name = "code_classification_context.jsonld"
    elif file_name == "repo_profile_example.json":
        expected_context_name = "repo_profile_context.jsonld"
    elif file_name == "skill_profile_example.json":
        expected_context_name = "skill_profile_context.jsonld"
    # Add more mappings if other example types exist

    if not expected_context_name:
        # Try to expand with whatever context is provided, even if not in our known list.
        # The validate_jsonld_structure function (which uses the loader) would be better for generic expansion.
        # This function is more about checking specific expected contexts.
        # For now, if it's not a known example type, we can't check its specific context path.
        # We will still try to expand it using the local loader.
        try:
            # Custom document loader for local files
            def local_document_loader_for_check(url, options=None):
                if url.startswith("https://raw.githubusercontent.com/ModelContext/skill-schema/main/contexts/"): # old URLs
                    _context_file_name = url.split('/')[-1]
                    _local_path = os.path.join(PROJECT_ROOT_FOR_CONTEXTS, 'contexts', _context_file_name)
                elif os.path.exists(url): 
                     _local_path = url
                elif os.path.exists(os.path.join(os.path.dirname(example_file_path), url)): 
                    _local_path = os.path.join(os.path.dirname(example_file_path), url)
                else: 
                    _local_path = os.path.join(PROJECT_ROOT_FOR_CONTEXTS, 'contexts', url)

                if os.path.exists(_local_path):
                    with open(_local_path, 'r', encoding='utf-8') as f_context:
                        context_doc = json.load(f_context)
                    return {'contextUrl': None, 'documentUrl': 'file://' + os.path.abspath(_local_path), 'document': context_doc}
                raise jsonld.JsonLdError(f"Context URL {url} could not be resolved to a local file.", "jsonld.LoadContextError")
            
            jsonld.expand(data, {'documentLoader': local_document_loader_for_check})
            return True, f"WARNING: No specific expected context mapping for {file_name}. Document expanded successfully with provided context '{actual_context}'."
        except Exception as e_expand:
            return False, f"WARNING: No specific expected context mapping for {file_name}. Expansion with provided context '{actual_context}' failed: {str(e_expand)}"


    # expected_context_url = BASE_CONTEXT_URL + expected_context_name
    # Construct expected local path. Assumes contexts are in 'contexts/' dir relative to project root.
    expected_local_context_path = os.path.normpath(os.path.join(PROJECT_ROOT_FOR_CONTEXTS, 'contexts', expected_context_name))
    
    # Normalize the actual_context if it's a relative path from the example file's location
    # or if it's already an absolute path.
    normalized_actual_context_path = None
    if isinstance(actual_context, str):
        if os.path.isabs(actual_context):
            normalized_actual_context_path = os.path.normpath(actual_context)
        else:
            # Try resolving relative to example file's directory first
            path_relative_to_example = os.path.normpath(os.path.join(os.path.dirname(example_file_path), actual_context))
            if os.path.exists(path_relative_to_example):
                 normalized_actual_context_path = path_relative_to_example
            else:
                # Try resolving relative to project's contexts directory if it's just a filename
                path_relative_to_project_contexts = os.path.normpath(os.path.join(PROJECT_ROOT_FOR_CONTEXTS, 'contexts', actual_context))
                if os.path.exists(path_relative_to_project_contexts):
                    normalized_actual_context_path = path_relative_to_project_contexts
                else: # if it's a URL like the old ones, try to map it
                    if actual_context.startswith("https://raw.githubusercontent.com/ModelContext/skill-schema/main/contexts/"):
                        _context_file_name = actual_context.split('/')[-1]
                        normalized_actual_context_path = os.path.normpath(os.path.join(PROJECT_ROOT_FOR_CONTEXTS, 'contexts', _context_file_name))


    if not normalized_actual_context_path or normalized_actual_context_path != expected_local_context_path:
        message = (f"Context path mismatch: Expected '{expected_local_context_path}', "
                   f"but found '{actual_context}' (resolved to '{normalized_actual_context_path}').")
        try:
            def local_document_loader_for_mismatch(url, options=None):
                # Simplified loader for this specific mismatch case
                _actual_path_to_try = normalized_actual_context_path # Try the resolved actual path
                if not _actual_path_to_try and isinstance(url, str) and os.path.exists(os.path.join(PROJECT_ROOT_FOR_CONTEXTS, 'contexts', url)): # if url is just filename
                    _actual_path_to_try = os.path.join(PROJECT_ROOT_FOR_CONTEXTS, 'contexts', url)
                elif not _actual_path_to_try and isinstance(url, str) and os.path.exists(url): # if url is already a valid path
                     _actual_path_to_try = url


                if _actual_path_to_try and os.path.exists(_actual_path_to_try):
                    with open(_actual_path_to_try, 'r', encoding='utf-8') as f_context:
                        context_doc = json.load(f_context)
                    return {'contextUrl': None, 'documentUrl': 'file://' + os.path.abspath(_actual_path_to_try), 'document': context_doc}
                raise jsonld.JsonLdError(f"Context URL {url} (from actual_context) could not be resolved to a local file for expansion.", "jsonld.LoadContextError")

            jsonld.expand(data, {'documentLoader': local_document_loader_for_mismatch})
            return False, message + " However, the document expanded successfully with the provided (mismatched) context."
        except Exception as e_expand:
            return False, message + f" Additionally, JSON-LD expansion with the provided (mismatched) context failed: {str(e_expand)}"

    # If actual_context path matches expected_local_context_path, try to expand
    try:
        def local_document_loader_for_expected(url, options=None):
            # This loader assumes 'url' will be the expected_local_context_path or a relative path from it
            # For simplicity, we'll assume 'url' is the direct path or can be found in 'contexts/'
            _path_to_load = None
            if os.path.exists(url): # If url is already a full path
                _path_to_load = url
            else: # Try to find it in project's contexts dir
                _path_to_load = os.path.join(PROJECT_ROOT_FOR_CONTEXTS, 'contexts', url)

            if os.path.exists(_path_to_load):
                with open(_path_to_load, 'r', encoding='utf-8') as f_context:
                    context_doc = json.load(f_context)
                return {'contextUrl': None, 'documentUrl': 'file://' + os.path.abspath(_path_to_load), 'document': context_doc}
            raise jsonld.JsonLdError(f"Context URL {url} (expected) could not be resolved to a local file.", "jsonld.LoadContextError")

        jsonld.expand(data, {'documentLoader': local_document_loader_for_expected})
        return True, "" # Context matches and expands successfully
    except jsonld.JsonLdError as e:
        return False, f"JSON-LD expansion error (with expected context path '{expected_local_context_path}'): {str(e)}"
    except Exception as e: 
        return False, f"Unexpected error during JSON-LD expansion (with expected context path '{expected_local_context_path}'): {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Validate JSON, JSON-LD, and schema files.")
    parser.add_argument('paths', nargs='+', help="List of file or directory paths to validate.")
    
    parser.add_argument('--run-syntax', action='store_true', help="Run basic JSON syntax validation.")
    parser.add_argument('--run-jsonld', action='store_true', help="Run JSON-LD structure validation.")
    parser.add_argument('--run-schema', action='store_true', help="Run schema validation for example files.")
    parser.add_argument('--run-context', action='store_true', help="Run JSON-LD context utilization checks for example files.")
    
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output (shows success messages).")

    args = parser.parse_args()

    # If no specific checks are requested, run all of them
    run_all_checks = not (args.run_syntax or args.run_jsonld or args.run_schema or args.run_context)

    if args.verbose:
        print("Verbose mode enabled.")
        print(f"Validating paths: {args.paths}")
        if run_all_checks:
            print("Running all validation checks.")
        else:
            if args.run_syntax: print("Syntax check enabled.")
            if args.run_jsonld: print("JSON-LD check enabled.")
            if args.run_schema: print("Schema check enabled.")
            if args.run_context: print("Context check enabled.")
    
    files_to_process = []
    for path_arg in args.paths:
        if os.path.isfile(path_arg):
            files_to_process.append(os.path.abspath(path_arg))
        elif os.path.isdir(path_arg):
            # Recursively find .json and .jsonld files in the directory
            for ext in ('**/*.json', '**/*.jsonld'):
                files_to_process.extend(
                    glob.glob(os.path.join(path_arg, ext), recursive=True)
                )
        else:
            print(f"Warning: Path '{path_arg}' is not a valid file or directory. Skipping.")
    
    # Remove duplicates that might arise from overlapping globs or explicit file + dir
    files_to_process = sorted(list(set(files_to_process)))

    if not files_to_process:
        print("No files found to validate based on the provided paths.")
        return

    # --- Overall counters for summary ---
    total_syntax_errors = 0
    total_jsonld_errors = 0
    total_schema_errors = 0
    total_context_errors = 0
    
    # Determine which files are examples for schema and context checks
    # This assumes examples are in a directory named 'examples' or follow '*_example.json(ld)' pattern
    example_files = [
        f for f in files_to_process 
        if "examples" in os.path.normpath(f).split(os.sep) or "_example.json" in f or "_example.jsonld" in f
    ]
    # For JSON-LD structure checks, we only care about .jsonld files
    jsonld_files = [f for f in files_to_process if f.endswith('.jsonld')]


    # --- Step 2: Basic JSON Syntax Validation ---
    if run_all_checks or args.run_syntax:
        print("\n--- Running Basic JSON Syntax Validation ---")
        current_syntax_errors = 0
        for file_path in files_to_process: # Validate syntax for all found files
            is_valid, error_message = validate_json_syntax(file_path)
            if not is_valid:
                print(f"File: {file_path} - {error_message}")
                current_syntax_errors += 1
            elif args.verbose:
                print(f"File: {file_path} - JSON syntax OK.")
        total_syntax_errors += current_syntax_errors
        if current_syntax_errors == 0:
            print("All checked files have valid JSON syntax.")
        else:
            print(f"\nFound JSON syntax errors in {current_syntax_errors} file(s) during this run.")

    # --- Step 3: JSON-LD Structure Validation ---
    if run_all_checks or args.run_jsonld:
        print("\n--- Running JSON-LD Structure Validation ---")
        current_jsonld_errors = 0
        if not jsonld_files:
            print("No .jsonld files found for JSON-LD structure validation among processed files.")
        else:
            for file_path in jsonld_files:
                is_valid, error_message = validate_jsonld_structure(file_path)
                if not is_valid:
                    print(f"File: {file_path} - {error_message}")
                    current_jsonld_errors += 1
                elif args.verbose:
                     print(f"File: {file_path} - JSON-LD structure OK.")
            total_jsonld_errors += current_jsonld_errors
            if current_jsonld_errors == 0:
                print("All checked .jsonld files have valid JSON-LD structure (or only had syntax errors reported above).")
            else:
                print(f"\nFound JSON-LD processing errors in {current_jsonld_errors} .jsonld file(s).")

    # --- Step 4: Schema Validation for Examples ---
    if run_all_checks or args.run_schema:
        print("\n--- Running Schema Validation for Examples ---")
        current_schema_errors = 0
        if not example_files:
            print("No example files found for schema validation among processed files.")
        else:
            for example_file in example_files:
                if args.verbose: print(f"Processing example for schema: {example_file}")
                # Assuming project root is where 'schemas' and 'examples' dirs are.
                # This might need adjustment if script is run from elsewhere or paths are absolute.
                # For simplicity, let's assume paths are relative to CWD or absolute.
                # map_example_to_schema needs a base_dir to correctly find 'schemas/'
                # We can try to infer base_dir if paths are deep, or require it.
                # For now, let's assume CWD is project root for relative paths.
                schema_file = map_example_to_schema(example_file, base_dir=".") # Use CWD as base for schema lookup
                
                if schema_file:
                    if args.verbose: print(f"  Attempting to validate against schema: {schema_file}")
                    is_valid, error_message = validate_with_schema(example_file, schema_file)
                    if not is_valid:
                        print(f"  File: {example_file} - ERROR (Schema): {error_message}")
                        current_schema_errors += 1
                    elif args.verbose:
                        print(f"  File: {example_file} - SUCCESS (Schema): Validated successfully.")
                elif args.verbose: # Only print warning in verbose, otherwise it's too noisy
                    print(f"  File: {example_file} - WARNING (Schema): No corresponding schema found. Skipping.")
            total_schema_errors += current_schema_errors
            if current_schema_errors == 0:
                print("All processed example files validated successfully against their schemas (or no schema was found/applicable).")
            else:
                print(f"\nFound schema validation errors in {current_schema_errors} example file(s).")

    # --- Step 5: Context Utilization Check ---
    if run_all_checks or args.run_context:
        print("\n--- Running JSON-LD Context Utilization Check for Examples ---")
        current_context_errors = 0
        if not example_files:
            print("No example files found for context utilization check among processed files.")
        else:
            for example_file in example_files:
                if args.verbose: print(f"Processing example for context: {example_file}")
                is_valid, message = check_context_utilization(example_file, base_dir=".") # Use CWD as base
                if not is_valid:
                    print(f"  File: {example_file} - ERROR (Context): {message}")
                    current_context_errors += 1
                elif message and args.verbose: # For warnings like no expected context mapping
                    print(f"  File: {example_file} - WARNING (Context): {message}")
                elif args.verbose:
                    print(f"  File: {example_file} - SUCCESS (Context): Context utilized correctly.")
            total_context_errors += current_context_errors
            if current_context_errors == 0:
                print("All processed example files utilize their JSON-LD contexts correctly (or no specific checks applied).")
            else:
                print(f"\nFound context utilization issues in {current_context_errors} example file(s).")

    print("\n--- Validation Process Finished ---")
    
    print("\n--- Validation Summary ---")
    files_actually_processed_count = len(files_to_process) # Total unique files matched by path arguments
    
    checks_were_run = False

    if run_all_checks or args.run_syntax:
        checks_were_run = True
        print(f"JSON Syntax Validation: {total_syntax_errors} error(s) found out of {files_actually_processed_count} files checked.")
    
    if run_all_checks or args.run_jsonld:
        checks_were_run = True
        num_jsonld_files_checked = len(jsonld_files)
        print(f"JSON-LD Structure Validation: {total_jsonld_errors} error(s) found out of {num_jsonld_files_checked} .jsonld files checked.")

    if run_all_checks or args.run_schema:
        checks_were_run = True
        num_example_files_for_schema = len(example_files)
        print(f"Schema Validation (Examples): {total_schema_errors} error(s) found out of {num_example_files_for_schema} example files processed for schema checks.")

    if run_all_checks or args.run_context:
        checks_were_run = True
        num_example_files_for_context = len(example_files)
        print(f"Context Utilization (Examples): {total_context_errors} error(s) found out of {num_example_files_for_context} example files processed for context checks.")

    if not checks_were_run:
        print("No specific validation checks were selected to run.")
    elif total_syntax_errors == 0 and total_jsonld_errors == 0 and total_schema_errors == 0 and total_context_errors == 0:
        print("\nAll selected validations passed successfully for all processed files!")
    else:
        print("\nSome validations failed. Please review the errors detailed above.")


if __name__ == '__main__':
    main()
