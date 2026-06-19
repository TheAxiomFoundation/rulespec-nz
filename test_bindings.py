import sys
import os

# Append the build directory of rulespec-nz to path or try to import it
try:
    import rulespec_nz
    print("Successfully imported rulespec_nz module!")
    res = rulespec_nz.sum_as_string(40, 2)
    print(f"sum_as_string(40, 2) = {res}")
    assert res == "42"
    print("Verification tests passed!")
except ImportError as e:
    print(f"Failed to import rulespec_nz: {e}")
    sys.exit(1)
