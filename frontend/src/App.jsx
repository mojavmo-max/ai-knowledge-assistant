import { useState, useEffect, useRef } from "react"

const API = "https://ai-knowledge-assistant-qsrn.onrender.com"

function App() {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState("")
  const [loading, setLoading] = useState(false)

  
  const [question, setQuestion] = useState("")
  const [messages, setMessages] = useState([])

  const chatEndRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({behavior: "smooth"})
  }, [messages])

  async function uploadFile() {
    if(!file) return

    const formData = new FormData()
    formData.append("file", file)

    setStatus("Uploading...")
    setLoading(true)

    try{
      const res = await fetch(`${API}/documents`, {
        method: "POST",
        body: formData,
      })

      const data = await res.json()

      if(res.ok){
        setStatus(`Uploaded: ${data.chunks || ""}`)
      } else{
        setStatus(data.detail || "Upload failed")
      }
    }
    catch(e){
      setStatus("Something went wrong")
    }
    finally{
      setLoading(false)
    }
  }

  async function sendQuestion() {
    if(!question) return

    const userMessage = {role: "user", text: question}
    setMessages((m) => [...m, userMessage])
    setQuestion("")
    setLoading(true)

    try{
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers:{"Content-Type": "application/json"},
        body: JSON.stringify({question}),
      })

      const data = await res.json()

      if(!res.ok){
        throw new Error("API error")
      } 

      const botMessage = {role: "bot", text: data.answer}
      setMessages((m) => [...m, botMessage])
    }
    catch(e){
      setMessages((m) => [...m, {role: "bot", text: "Something went wrong"}])
    }
    finally{
      setLoading(false)
    }
  }

  return (
    <>
    <div style={{
      maxWidth: "720px",
      margin: "40px auto",
      fontFamily: "system-ui, sans-serif"
    }}>
      <div style={{ padding : "40px", maxWidth: "600px"}}>
        <h1>AI Knowledge Assistant</h1>

        <p style={{color: "#555"}}> Upload PDFs and ask questions using AI </p>
        

        <h3>1. Upload documents </h3>
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files[0])}
        ></input>

        <br /><br />

        <button onClick={uploadFile} disabled={loading} 
          style={{
            padding: "8px 14px",
            borderRadius: "6px",
            border: "1px solid #ccc",
            cursor: "pointer"
          }}
        >
          {loading? "Uploading...": "Upload PDF"}</button>
        <p>{status}</p>

        <hr/>


        <h3>2. Ask questions </h3>
        <div style={{border: "1px solid #ccc", padding: "10px", minHeight: "200px"}}>
          <div style={{
              border: "1px solid #ddd",
              padding: "10px", 
              borderRadius: "6px"
            }}>
            {messages.map((m, i) => (
              <div key={i} style={{
                marginBottom:"8px",
                background: m.role == "user"? "#f1f5f9" : "#e0f2fe",
                padding:"6px 10px",
                borderRadius: "6px"
                }}>
                <b>{m.role === "user"? "You" : "AI"}:</b> {m.text}
              </div>
            ))}
            {loading && <p>AI is thinking...</p>}
            <div ref={chatEndRef} />
          </div>
        </div>

        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
          style={{width: "80%", padding: "8px 14px", margin: "5px"}}  
        >
        </input>

        <button onClick={sendQuestion} disabled={loading}
          style={{
            padding: "8px 14px",
            borderRadius: "6px",
            border: "1px solid #ccc",
            cursor: "pointer"
          }}
        >
          {loading? "Thinking...": "Send"}
        </button>
      </div>
      </div>
    </>
  )
}

export default App
