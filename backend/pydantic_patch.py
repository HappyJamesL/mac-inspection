# Pydantic patch for Python 3.13 compatibility
import sys

# Apply patch only for Python 3.13+
if sys.version_info >= (3, 13):
    # Patch pydantic's evaluate_forwardref function
    import pydantic.typing
    
    # Save original function
    original_evaluate_forwardref = pydantic.typing.evaluate_forwardref
    
    def patched_evaluate_forwardref(type_, globalns, localns):
        # For Python 3.13+, we need to handle the new _evaluate signature
        if hasattr(type_, '_evaluate'):
            # Check if we're dealing with a ForwardRef
            import typing
            if isinstance(type_, typing.ForwardRef):
                # Python 3.13+ ForwardRef._evaluate requires recursive_guard parameter
                return type_._evaluate(globalns, localns, recursive_guard=set())
        # Fallback to original behavior
        return original_evaluate_forwardref(type_, globalns, localns)
    
    # Apply the patch
    pydantic.typing.evaluate_forwardref = patched_evaluate_forwardref
    
    print("Applied pydantic patch for Python 3.13 compatibility")
