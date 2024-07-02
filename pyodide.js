// See https://dev.to/lambertbrady/python-in-react-with-pyodide-1mof
// https://gist.github.com/lambertbrady/3b70a860b1ee6118d141f477c914e5c2

function Pyodide({
  pythonCode,
  setPythonOutput,
  dabAnalysisImages,
  setPythonCode,
  downloadZip,
  setDownloadZip
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
            import pandas as pd
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
                    data = D.imread(input_filepath)
                    image_mask_asyn, table_asyn, thresh = D.analyse_DAB(data, input_filepath)
                    return plot_and_save_masks(data, image_mask_asyn, output_filepath=output_filepath)
                else:
                    return f"No file exists at {input_filepath}"
            
            def plot_and_save_masks(data, mask, output_filepath=None):
                fig, axes = D.plot_masks(data, mask)
                plt.tight_layout()
                if output_filepath:
                    if os.path.exists(output_filepath):
                        os.remove(output_filepath)
                    fig.savefig(output_filepath)
                img_out = io.BytesIO()
                fig.savefig(img_out, format="png")
                img_out.seek(0)
                imgdata = img_out.read()

                b64string = b64encode(imgdata).decode('UTF-8')
                return b64string

            def batch_analyse():
                input_dir = 'input'
                output_dir = 'output-final'
                file_list = [os.path.join(input_dir, filename) for filename in os.listdir(input_dir)]
                im_dict = D.imdict_read(file_list)
                tables = []
                for i, (filename, image_mask_asyn, table_asyn) in enumerate(D.analyse_DAB_multiimage(im_dict)):
                    output_filepath = os.path.join(output_dir, os.path.basename(filename))
                    image_mask_asyn_serialized = plot_and_save_masks(D.imread(filename), image_mask_asyn, output_filepath=output_filepath)
                    tables.append(table_asyn)
                    if i < len(im_dict) - 1:
                        status = 'generator in progress'
                    else:
                        status = 'generator completed'
                        pd.concat(tables).reset_index(drop=True).to_csv(os.path.join(output_dir, 'table_asyn.csv'))
                        shutil.make_archive('output-final', format="zip", root_dir="output-final")

                    # Get just the id part of the filename
                    # e.g. input/41-foobar.png -> 41
                    id = filename.split('/')[1].split('-')[0]
                    yield status, id, filename, image_mask_asyn_serialized
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

  // Download output-final.zip from pyodide FS when downloadZip is set true
  useEffect(() => {
    (async function (pyodide) {
      if (!isPyodideLoading && downloadZip && await pyodide.FS.analyzePath('output-final.zip').exists) {
        const bytes = await pyodide.FS.readFile("output-final.zip")
        var blob = new Blob([bytes], {type: "application/x-zip"})
        var link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = "output.zip";
        link.click();
      }
      setDownloadZip(false);
    })(pyodide.current)
  }, [isPyodideLoading, downloadZip, pyodide, setDownloadZip])

}
