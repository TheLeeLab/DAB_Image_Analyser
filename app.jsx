const {useRef, useState, useEffect} = React;
const {fromEvent} = fileSelector;

const app = document.getElementById('app');

function HomePage() {
    const [pythonOutput, setPythonOutput] = useState('');
    const [pythonCode, setPythonCode] = useState('');
    const [dabAnalysisImages, setDabAnalysisImages] = useState([]);
    // useEffect(() => {console.log(pythonOutput)}, [pythonOutput])
    return (
        <div>
            <FileZone setPythonCode={setPythonCode} pythonOutput={pythonOutput} dabAnalysisImages={dabAnalysisImages} setDabAnalysisImages={setDabAnalysisImages} />
            <Pyodide pythonCode={pythonCode} pythonOutput={pythonOutput} setPythonOutput={setPythonOutput} dabAnalysisImages={dabAnalysisImages} />
        </div>
    );
}
function FileZone({setPythonCode, pythonOutput, dabAnalysisImages, setDabAnalysisImages}) {

    

    useEffect(() => {
        if (dabAnalysisImages.length > 0 && pythonOutput) {
            let pythonOutputObject = JSON.parse(pythonOutput.toString());
            let dabAnalysisImage = dabAnalysisImages[pythonOutputObject.id]
            dabAnalysisImage.outputImage = pythonOutputObject.result
            setDabAnalysisImages(dabAnalysisImages.map((value, index) => {return (index == pythonOutputObject.id) ? dabAnalysisImage : value}));
        }
    }, [pythonOutput])

    function preview(id) {
        // TODO: Setting the processing message first won't actually work, because these are asynchronous,
        // so we can't be sure that they will happen in the right order.
        // // Set processing message
        // let dabAnalysisImage = dabAnalysisImages[id]
        // dabAnalysisImage.outputImage = `processing file ${dabAnalysisImages[id].file.name}`
        // setDabAnalysisImages(dabAnalysisImages.map((value, index) => {return (index == id) ? dabAnalysisImage : value}))
        
        // Run python
        setPythonCode('json.dumps({"id": ' + id + ', "result": analysispreview(' + id + ', "' + dabAnalysisImages[id].file.name + '")})')
    }

    return (
        <>
            <FileDropZone dabAnalysisImages={dabAnalysisImages} setDabAnalysisImages={setDabAnalysisImages} />
            <FileDisplayZone dabAnalysisImages={dabAnalysisImages} preview={preview}/>
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
        <div
            onDragOver={onDragOver}
            onDrop={onDrop}
            className="flex items-center justify-center w-full"
        >
            <div className="max-w-2xl mx-auto">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <label htmlFor="dropzone-file" className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-bray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600">
                        <svg className="w-10 h-10 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                        <p className="mb-2 text-sm text-gray-500 dark:text-gray-400"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                    </label>
                    {/* Note: File selector in HTML file input doesn't support choosing both files and directories from the same dialog.
                    For now, drag and drop, or highlight multiple files if you want to upload a whole directory at once */}
                    <input onChange={(evt) => {uploadFiles(evt.target.files)}} id="dropzone-file" type="file" className="hidden" multiple />
                </div>
            </div>
        </div>
    )
}

function FileDisplayZone({dabAnalysisImages, preview}) {

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

function ImageFileViewer({file}) {

    const [imgSrc, setImgSrc] = useState('');

    useEffect(() => {
        // Only set imgSrc once FileReader has loaded
        const reader = new FileReader()

        reader.onloadend = () => {
          setImgSrc(reader.result)
        }
        reader.readAsDataURL(file)
    }, [file])

    return <img src={imgSrc}/>
}

function OutputPreviewViewer({dabImage, id, preview}) {
    if (dabImage && dabImage.outputImage) {
        return <img src={`data:image/png;base64,${dabImage.outputImage}`}></img>
    } else {
        return <button onClick={() => {preview(id)}} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Run Preview Analysis</button>
    }

}

const root = ReactDOM.createRoot(app);
root.render(<HomePage />);
