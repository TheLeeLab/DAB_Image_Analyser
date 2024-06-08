// See https://dev.to/lambertbrady/python-in-react-with-pyodide-1mof
// https://gist.github.com/lambertbrady/3b70a860b1ee6118d141f477c914e5c2

function Pyodide({
  pythonCode,
  setPyodideOutput
}) {
  const pyodide = useRef(null)
  const [isPyodideLoading, setIsPyodideLoading] = useState(true)

  // load pyodide wasm module and initialize it
  useEffect(() => {
    ;(async function () {
      pyodide.current = await globalThis.loadPyodide();
      await pyodide.current.loadPackage(
        ["numpy", "matplotlib", "scikit-image", "opencv-python", "pandas"]
      );
        // imports required for python
        await pyodide.current.runPythonAsync(`
            import os
            # Copy DAB_Analysis_Functions.py from where it lives on our server (http://example.com/DAB_Analysis_Functions.py)
            # to the Emscripten MEMFS filesystem (/home/pyodide/...) where pyodide has access to it.
            if not os.path.exists("DAB_Analysis_Functions.py"):
                from pyodide.http import pyfetch
                response = await pyfetch("DAB_Analysis_Functions.py")
                with open("DAB_Analysis_Functions.py", "wb") as f:
                    f.write(await response.bytes())

            import matplotlib.pyplot as plt
            import base64
            import os
            import numpy as np
            import shutil
            
            from DAB_Analysis_Functions import DAB

            def hello(name):
                return f'Hello {name}'
            
            D = DAB()
        `)

      setIsPyodideLoading(false)
    })()
  }, [pyodide])

  // evaluate python code with pyodide and set output
  useEffect(() => {
    if (!isPyodideLoading) {
      const evaluatePython = async (pyodide, pythonCode) => {
        try {
          return await pyodide.runPython(pythonCode)
        } catch (error) {
          console.error(error)
          return 'Error evaluating Python code. See console for details.'
        }
      }
      ;(async function () {
        setPyodideOutput(await evaluatePython(pyodide.current, pythonCode))
      })()
    }
  }, [isPyodideLoading, pyodide, pythonCode])
}
