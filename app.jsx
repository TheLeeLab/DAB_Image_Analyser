const {useState, useEffect} = React;
const {fromEvent} = fileSelector;
const app = document.getElementById('app');

function HomePage() {
    return (
        <div>
            <FileZone />
        </div>
    );
}
function FileZone() {


    const [fileList, setFileList] = useState([]);

    return (
        <>
            <FileDropZone fileList={fileList} setFileList={setFileList}/>
            <FileDisplayZone fileList={fileList} />
        </>
    )
}

function FileDropZone({fileList, setFileList}) {

    // Display fileList in console whenever it changes
    useEffect(() => {console.log({fileList})}, [fileList])

    async function uploadFiles(files) {
        // Array destructuring so that we get an array of Files instead of a FileList object
        setFileList([...files]);

        // If we did it this way, we would allow you to add files to the files that are already
        // there instead of replacing them... but you could add the same file multiple times
        // setFileList([...fileList, ...files]);
    }
    async function onDrop(evt) {
        evt.preventDefault();
        const files = await fromEvent(evt);
        uploadFiles(files);
    };
    async function onDragOver(evt) {
        // Stop browser from just opening the file in a new tab
        // Requires intercepting the dragover event as well as the drop event
        evt.preventDefault();
    };

    return (
        <>
        <div
            // onDragEnter={onDragEnter}
            // onDragLeave={onDragLeave}
            onDragOver={onDragOver}
            onDrop={onDrop}
            // className={tailwindClasses}
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
        </>
    )
}

function FileDisplayZone({fileList}) {
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
                {fileList.map((file, index)=>(
                    <tr className="flex w-full mb-4" key={index}>
                        <td className="p-4 w-1/3">{file.name}</td>
                        <td className="p-4 w-1/3">{file.name}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    )
}

const root = ReactDOM.createRoot(app);
root.render(<HomePage />);
