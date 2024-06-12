const {useRef, useState, useEffect} = React;
const {fromEvent} = fileSelector;

const app = document.getElementById('app');

function HomePage() {
    const [pythonOutput, setPythonOutput] = useState('');
    const [pythonCode, setPythonCode] = useState('');
    const [dabAnalysisImages, setDabAnalysisImages] = useState([]);
    const [parameters, setParameters] = useState({'analyseNuclei': false});
    return (
        <>
            <div className="grid grid-cols-2">
                <FileZone setPythonCode={setPythonCode} pythonOutput={pythonOutput} setPythonOutput={setPythonOutput} dabAnalysisImages={dabAnalysisImages} setDabAnalysisImages={setDabAnalysisImages} parameters={parameters}/>
                <ParameterForm parameters={parameters} setParameters={setParameters}  dabAnalysisImages={dabAnalysisImages} setDabAnalysisImages={setDabAnalysisImages} />
            </div>
            <Pyodide pythonCode={pythonCode} setPythonCode={setPythonCode} pythonOutput={pythonOutput} setPythonOutput={setPythonOutput} dabAnalysisImages={dabAnalysisImages} />
            </>
    );
}
function FileZone({setPythonCode, pythonOutput, setPythonOutput, dabAnalysisImages, setDabAnalysisImages, parameters}) {

    

    useEffect(() => {
        if (dabAnalysisImages.length > 0 && pythonOutput.length > 0) {
            let pythonOutputObject = JSON.parse(pythonOutput.toString());
            let dabAnalysisImage = dabAnalysisImages[pythonOutputObject.id]
            dabAnalysisImage.outputImage = pythonOutputObject.result
            setDabAnalysisImages(dabAnalysisImages.map((value, index) => {return (index == pythonOutputObject.id) ? dabAnalysisImage : value}));
            // Reset pythonOutput to empty string after using it
            // TODO: Avoid this pattern
            setPythonOutput('')
        }
    }, [pythonOutput])

    async function preview(id) {
        // Set processing message
        let dabAnalysisImage = dabAnalysisImages[id]
        dabAnalysisImage.outputImage = `processing`
        await setDabAnalysisImages(dabAnalysisImages.map((value, index) => {return (index == id) ? dabAnalysisImage : value}))
        
        // Run python
        await setPythonCode(
            `json.dumps({
                "id": ${id},
                "result": analysispreview(
                    ${id},
                    "${dabAnalysisImages[id].file.name}",
                    analyse_nuclei=${parameters.analyseNuclei ? "True" : "False"}
                    )
                })`
        )
    }

    return (
        <>
            <FileDropZone dabAnalysisImages={dabAnalysisImages} setDabAnalysisImages={setDabAnalysisImages} />
            <FileDisplayZone dabAnalysisImages={dabAnalysisImages} preview={preview} parameters={parameters}/>
        </>
    )
}



function FileDropZone({dabAnalysisImages, setDabAnalysisImages}) {

    // Display dabAnalysisImages in console whenever it changes
    useEffect(() => {console.log(dabAnalysisImages)}, [dabAnalysisImages])

    async function uploadFiles(files) {
        // Array destructuring ([...files] so that we get an array of Files instead of a DabAnalysisImages object
        // Then filter for MIME type of image/*
        var imageFiles = [...files].filter((file) => {return file.type.startsWith('image/')});

        // Create new data structure to store images and results together
        var dabAnalysisImages = imageFiles.map((file) => {return {file: file, outputImage: undefined, outputCsv: undefined}})
        setDabAnalysisImages(dabAnalysisImages);

    }
    async function onDrop(evt) {
        evt.preventDefault();
        // Using fromEvent from this react-dropzone/file-selector library to convert drop event into file list
        // is nice because it deals with both directories and files, and traverses directory trees
        const files = await fromEvent(evt);
        uploadFiles(files);
    };
    async function onDragOver(evt) {
        // Stop browser from just opening the file in a new tab
        // Requires intercepting the dragover event as well as the drop event
        evt.preventDefault();
    };

    return (
        <div id="static-modal" data-modal-backdrop="static" tabIndex="-1" aria-hidden="true"
        className={`${dabAnalysisImages.length > 0 ? 'hidden': ''} overflow-y-hidden overflow-x-hidden fixed top-0 right-0 bottom-0 left-0 z-50 flex h-screen justify-center items-center bg-gray-300 bg-opacity-50 `
        }>
            <div
                onDragOver={onDragOver}
                onDrop={onDrop}
                className="flex items-center justify-center w-full h-full min-w-[40rem]"
            >
                <div className="h-full w-full mx-[10rem] items-center justify-center">
                    <div className="flex flex-col w-full h-full items-center justify-center">
                        <label htmlFor="dropzone-file" className="flex flex-col items-center justify-center w-full h-full m-10 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-white dark:hover:bg-bray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600">
                            <svg className="w-10 h-10 mb-3 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                            <p className="mb-2 text-sm text-black text-center"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                        </label>
                        {/* Note: File selector in HTML file input doesn't support choosing both files and directories from the same dialog.
                        For now, drag and drop, or highlight multiple files if you want to upload a whole directory at once */}
                        <input onChange={(evt) => {uploadFiles(evt.target.files)}} id="dropzone-file" type="file" className="hidden" multiple />
                    </div>
                </div>
            </div>
        </div>
    )
}

function FileDisplayZone({dabAnalysisImages, preview, parameters}) {

    return (
        <table className="text-left w-full h-dvh">
            <thead className="bg-black flex text-white w-full">
			<tr className="flex w-full mb-4">
				<th className="p-4 w-1/3">FileName</th>
				<th className="p-4 w-1/3">Image</th>
				<th className="p-4 w-1/3">Output preview</th>
			</tr>
		</thead>
            <tbody className="bg-grey-light flex flex-col items-center justify-between overflow-auto w-full h-full">
                {dabAnalysisImages.map((file, index)=>(
                    <tr className="flex w-full mb-4" key={index}>
                        <td className="p-4 w-1/3">{file.file.name}</td>
                        <td className="p-4 w-1/3"><ImageFileViewer file={file.file} /></td>
                        <td className="p-4 w-1/3"><OutputPreviewViewer dabImage={file} id={index} preview={preview} /></td>
                    </tr>
                ))}
            </tbody>
        </table>
    )
}

function ZoomableImage({src}) {
    const [zoomed, setZoomed] = useState(false);
    const divZoomedClasses = "overflow-y-hidden overflow-x-hidden fixed top-0 right-0 bottom-0 left-0 z-50 flex justify-center items-center w-full h-full m-0 bg-gray-300 bg-opacity-50  cursor-zoom-out";
    const divUnzoomedClasses = "cursor-zoom-in h-30";
    const imgZoomedClasses = "object-scale-down h-[calc(100vh-2rem)] border-2 border-gray-300 border-dashed rounded-lg ";
    const imgUnzoomedClasses= "object-scale-down h-full";
    return (
        <>
            {/* Show unzoomed version at all times so layout isn't messed up during zoom */}
            <div className={divUnzoomedClasses} onClick={() => {setZoomed(true)}}>
                <img src={src} className={imgUnzoomedClasses}/>
            </div>
            {/* Show zoomed version only when 'zoomed' is true */}
            {zoomed && <div className={divZoomedClasses} onClick={() => {setZoomed(false)}}>
                <img src={src} className={imgZoomedClasses}/>
            </div>}
        </>
    )
}

function ImageFileViewer({file}) {

    const [imgSrc, setImgSrc] = useState('');

    useEffect(() => {
        // Only set imgSrc once FileReader has loaded
        const reader = new FileReader()

        reader.onloadend = () => {
          // Check image MIME type using start of base64 string
          if (reader.result.startsWith("data:image/tiff")) {
            // If tiff image, we need Array Buffer instead of DataURL
            const tiffReader = new FileReader()
            tiffReader.onloadend = () => {
                Tiff.initialize({TOTAL_MEMORY: 16777216 * 10});
                var tiff = new Tiff({buffer: tiffReader.result});
                // Create canvas with image, then convert that canvas to a base64 DataURL
                // to set as img src
                setImgSrc(tiff.toCanvas().toDataURL());
            }
            tiffReader.readAsArrayBuffer(file)
          } else {
            // If other image, just directly set the base64 DataURL as img src
            setImgSrc(reader.result);
          }
        }
        reader.readAsDataURL(file)
    }, [file])

    return <ZoomableImage src={imgSrc}/>
}

function OutputPreviewViewer({dabImage, id, preview}) {
    if (dabImage && dabImage.outputImage == 'processing') {
        // this is not a very responsive way of putting up a 'running' message
        return <p>Running...</p>
    } else if (dabImage && dabImage.outputImage) {
        return <ZoomableImage src={`data:image/png;base64,${dabImage.outputImage}`} />
    } else {
        return (
            <>
            <button onClick={async () => {await preview(id)}} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Run Preview Analysis</button>
            </>
        )
        }

}

function ParameterForm({parameters, setParameters, dabAnalysisImages, setDabAnalysisImages}) {

    function setParametersFromForm (evt) {
        // When the form values change, update the parameters state so that the
        // entry with key evt.target.name (e.g. asyn_LMean) has the new value
        // but other value stay the same
        if (evt.target.type == "checkbox") {
            setParameters({ ...parameters, [evt.target.name]: evt.target.checked});
        } else {
            setParameters({ ...parameters, [evt.target.name]: evt.target.value});
        }

        // Remove preview images
        setDabAnalysisImages(dabAnalysisImages.map((dabAnalysisImage) => { return {...dabAnalysisImage, outputImage: undefined} }))
    }
    return (
        <div className="space-y-12 m-[1rem]">
            <div className="border-b border-gray-900/10 pb-12">

                <h2 className="text-base font-semibold leading-7 text-gray-900">Parameters</h2>
                <p className="mt-1 text-sm leading-6 text-gray-600">N.B. Changing parameters will clear any preview runs</p>

                <form id="parameterForm" onChange={setParametersFromForm} className="w-full max-w-lg">

                    {/* <div id="asynParameters" className="w-full">
                        <div className="w-full px-3 mb-6">
                            <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="asyn_LMean">asyn_LMean:</label>
                            <input className="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500" type="number" id="asyn_LMean" name="asyn_LMean" defaultValue={parameters["asyn_LMean"]} step="0.01" />
                        </div>

                        <div className="w-full px-3 mb-6">
                            <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="asyn_aMean">asyn_aMean:</label>
                            <input className="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500" type="number" id="asyn_aMean" name="asyn_aMean" defaultValue={parameters["asyn_aMean"]} step="0.01" />
                        </div>

                        <div className="w-full px-3 mb-6">
                            <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="asyn_bMean">asyn_bMean:</label>
                            <input className="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500" type="number" id="asyn_bMean" name="asyn_bMean" defaultValue={parameters["asyn_bMean"]} step="0.01" />
                        </div>

                        <div className="w-full px-3 mb-6">
                            <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="asyn_threshold">asyn_threshold:</label>
                            <input className="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500" type="number" id="asyn_threshold" name="asyn_threshold" defaultValue={parameters["asyn_threshold"]} step="0.01" />
                        </div>
                    </div> */}

                    {/* TODO: Remove analyseNuclei button from being hidden when nuclei analysis enabled*/}
                    <div className="w-full px-3 mb-6">
                        <label htmlFor="analyseNuclei" className="w-4 h-4 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600" >Analyse Nuclei?:</label>
                        <input type="checkbox" id="analyseNuclei" name="analyseNuclei" className="ms-2 text-sm font-medium text-gray-900 dark:text-gray-300"/>
                    </div>

                    {/* <div id="nucleiParameters" className={`${ parameters['analyseNuclei'] ? '': 'hidden'}`}>
                        <label htmlFor="nuclei_LMean">nuclei_LMean:</label>
                        <input type="number" id="nuclei_LMean" name="nuclei_LMean" defaultValue={parameters["nuclei_LMean"]} step="0.01" />
                        
                        <label htmlFor="nuclei_aMean">nuclei_aMean:</label>
                        <input type="number" id="nuclei_aMean" name="nuclei_aMean" defaultValue={parameters["nuclei_aMean"]} step="0.01" />
                        
                        <label htmlFor="nuclei_bMean">nuclei_bMean:</label>
                        <input type="number" id="nuclei_bMean" name="nuclei_bMean" defaultValue={parameters["nuclei_bMean"]} step="0.01" />
                        
                        <label htmlFor="nuclei_threshold">nuclei_threshold:</label>
                        <input type="number" id="nuclei_threshold" name="nuclei_threshold" defaultValue={parameters["nuclei_threshold"]} step="0.01" />
                    </div> */}
                </form>
            </div>
            <div className="flex justify-center">
                <button onClick={async () => {console.log("This doesn't do anything yet!")}} className="bg-gray-300 hover:bg-gray-30 text-gray-500 font-bold py-2 px-4 rounded"><span className="line-through">Run all and download</span></button>
            </div>
        </div>
    )
}

const root = ReactDOM.createRoot(app);
root.render(<HomePage />);
