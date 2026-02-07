import { useState } from "react";

const API = "http://127.0.0.1:8000"

export default function Invoice(){
    const [file, setFile] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [status, setStatus] = useState(null);
    
    async function handleUpload() {
        if (!file) return;

        setLoading(true)
        setStatus("Uploading invoice...")
        setResult(null)
        setError(null)

        setTimeout(() => setStatus("Reading document..."), 500)
        setTimeout(() => setStatus("Extracting data..."), 1500)

        const formData = new FormData()
        formData.append("file", file)

        try {
            const res = await fetch(`${API}/invoiceDetails`,{
                method:"Post",
                body:formData
            })

            const json = await res.json();
            
            if(!json.success){
                setError(json.error)
            }
            else{
                setResult(json.data);
            }
        }
        finally{
            setLoading(false);
        }
    }

    return(
        <div>
            <h1>Invoice Assistant</h1>

            <input
                type="file"
                accept="image/*,.pdf"
                onChange={(e) => setFile(e.target.files[0])}
                />

            <button onClick={handleUpload}>
                Upload Invoice
            </button>

            {loading && <p>{status}</p>}
            {error && <p className="error">{error}</p>}

            {result && (
            <pre>{JSON.stringify(result, null, 2)}</pre>
            )}

        </div>
    )
}