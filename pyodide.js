// See https://dev.to/lambertbrady/python-in-react-with-pyodide-1mof
// https://gist.github.com/lambertbrady/3b70a860b1ee6118d141f477c914e5c2

function Pyodide({
  pythonCode,
  setPythonOutput,
  dabAnalysisImages,
  setPythonCode
}) {
  const pyodide = useRef(null)
  const [isPyodideLoading, setIsPyodideLoading] = useState(true)
  const [allDataLoaded, setAllDataLoaded] = useState(false)

  // load pyodide wasm module and initialize it
  useEffect(() => {
    (async function () {
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
            import json
            import io
            from base64 import b64encode
            
            from DAB_Analysis_Functions import DAB

            D = DAB()

            def analysispreview(id, name, analyse_nuclei=False):
                filename = f'{id}-{name}'
                input_dir = 'input'
                output_dir = 'output-preview'
                input_filepath = os.path.join(input_dir, filename)
                output_filepath = os.path.join(output_dir, filename)
                if os.path.exists(input_filepath):
                    # TODO: error handling if imread fails
                    data = D.imread(input_filepath)
                    if analyse_nuclei:
                        image_mask_asyn, table_asyn, image_mask_nuclei, table_nuclei, thresh_asyn, thresh_nuclei = D.analyse_DAB_and_cells(data, filename)
                        masks = np.dstack([image_mask_asyn, image_mask_nuclei])
                    else:
                        image_mask_asyn, table_asyn, thresh = D.analyse_DAB(data, filename)
                        masks = image_mask_asyn
                    fig, axes = D.plot_masks(data, masks)
                    if os.path.exists(output_filepath):
                        os.remove(output_filepath)
                    fig.savefig(output_filepath)

                    # Output as b64 string to send to JS
                    plt.tight_layout()
                    img_out = io.BytesIO()
                    fig.savefig(img_out, format="png")
                    img_out.seek(0)
                    imgdata = img_out.read()

                    b64string = b64encode(imgdata).decode('UTF-8')
                    return b64string

                else:
                    return f"No file exists at {input_filepath}"
            
            def data_mask_to_b64(data, mask):
                fig, axes = D.plot_masks(data, mask)
                plt.tight_layout()
                img_out = io.BytesIO()
                fig.savefig(img_out, format="png")
                img_out.seek(0)
                imgdata = img_out.read()

                b64string = b64encode(imgdata).decode('UTF-8')
                return b64string

            def batch_analyse():
                input_dir = 'input'
                output_dir = 'output-batch'
                file_list = [os.path.join(input_dir, filename) for filename in os.listdir(input_dir)]
                im_dict = D.imdict_read(file_list)
                for i, (filename, image_mask_asyn, table_asyn) in enumerate(D.analyse_DAB_multiimage(im_dict)):
                    image_mask_asyn_serialized = data_mask_to_b64(D.imread(filename), image_mask_asyn)
                    if i < len(im_dict) - 1:
                      status = 'generator in progress'
                    else:
                      status = 'generator completed'
                    yield status, filename, image_mask_asyn_serialized
        `)

      setIsPyodideLoading(false)
    })()
  }, [pyodide])

  // evaluate python code with pyodide and set output
  useEffect(() => {
    if (!isPyodideLoading && allDataLoaded && pythonCode.length > 0) {
      const evaluatePython = async (pyodide, pythonCode) => {
        try {
          return await pyodide.runPython(pythonCode)
        } catch (error) {
          console.error(error)
          return 'Error evaluating Python code. See console for details.'
        }
      }
      (async function () {
        setPythonOutput(await evaluatePython(pyodide.current, pythonCode))
        // Reset pythonCode to empty string after using it
        // TODO: Avoid this pattern
        setPythonCode('')
      })()
    }
  }, [isPyodideLoading, pyodide, pythonCode, allDataLoaded])

  // write to pyodide FS
  useEffect(() => {

    if (!isPyodideLoading && dabAnalysisImages.length > 0 && !allDataLoaded) {
        const writeFiles = async (pyodide, dabAnalysisImages) => {
          await pyodide.runPython("os.mkdir('input'); os.mkdir('output-preview'); os.mkdir('output-final')");
          const fileWrittenPromises = dabAnalysisImages.map((dabAnalysisImage, ind) => {
            // Return a promise per file
            return new Promise((resolve, reject) => {
              const reader = new FileReader();
              reader.onloadend = async () => {
                try {
                  const uint8_view = new Uint8Array(reader.result);
                  let newFileName = `${ind}-${dabAnalysisImage.file.name}`
                  await pyodide.FS.writeFile(`input/${newFileName}`, uint8_view)
                  resolve();
                } catch (err) {
                  reject(err)
                }
              }
              reader.onerror = (error) => {
                reject(error);
              };
              reader.readAsArrayBuffer(dabAnalysisImage.file)
            })
          });
          await Promise.all(fileWrittenPromises);
          return true
        }
        (async function () {
            writeFiles(pyodide.current, dabAnalysisImages).then((result) => {setAllDataLoaded(result)})
        })()
    }
  }, [isPyodideLoading, pyodide, dabAnalysisImages])
}
