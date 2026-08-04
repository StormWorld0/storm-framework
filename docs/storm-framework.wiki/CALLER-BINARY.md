## Caller Binary Storm Framework Explanation

The caller used to invoke binary modules has been upgraded with three different mechanisms. For example, binaries using PyO3, Ctypes, Shared Objects, and others are now handled differently. We separate the invocation methods for these binaries to make them easier to distinguish and to improve execution handling.

**1. call_bin:** This is to call the binary executable without extension as used by modules in Storm Framework.

**2. call_cty:** This is to call a binary that uses CPython methods, the caller will handle this automatically to use `ctypes.DLL` so you just have to call the binary name.

**2. call_so:** This is to call binary `.so` or **Shared Object** for example, with PyO3, you would normally need to perform a specific import in Python. However, with this system, you can use it dynamically by simply calling its name. You may also include the extension if needed, especially to avoid false positives or conflicts with other binary names.

## Import and usage examples

```python
from lib.roar.calling import call_bin, call_cty, call_so

# Binary without extension
A = call_bin("storm")

# CPython binaries that use Ctypes
# can call by name only or by extension
# just adjust it to the binary output.
B = call_cty("storm")

# Binary shared objects or Py03
C = call_so("storm")
C = call_so("storm.so")
```

>[!Important]
>Because the caller is designed to make things easier for developers, such as contributors who want to share code with the Storm Framework, we always remind you that you must ensure the code passes dynamic compilation and is properly tested through GitHub Actions.
>
>We also recommend writing modules in either Python or Golang. If the module is written in another language, such as Rust, you must follow the strict Storm Framework vendor standards, and we do not recommend doing so.
>
>One final thing: we only accept source code, not precompiled binaries. If a PR includes prebuilt binaries, the Maintainers will immediately reject it.
