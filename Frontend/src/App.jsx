import React, { useState } from "react";
import CodeEditor from "./components/CodeEditor";
import axios from "axios";

function App() {
  const [code, setCode] = useState("");
  const [tokens, setTokens] = useState([]);
  const [ast, setAst] = useState(null);
  const [ir, setIr] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleRun = async () => {
    setError("");
    setTokens([]);
    setAst(null);
    setIr("");
    setResult(null);

    try {
      const response = await axios.post("http://127.0.0.1:5000/compile", {
        inputCode: code,
      });
      
      
      const data = response.data;
      if (data.error) {
        console.log(data.error);
        setError(data.error); // Show backend's error message
        return;
      }
      setTokens(data.tokens || []);
      setAst(data.ast || null);
      setIr(data.ir || "");
      setResult(data.result ? data.result : null);
    } catch (err) {
      console.error("Error:", err);
      setError("An error occurred while compiling the code.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f172a] to-[#1e293b] text-gray-200 font-sans">
      {/* Header */}
      <header className="flex justify-between items-center px-6 py-4 bg-[#1e293b] shadow-lg border-b border-gray-700">
        <h1 className="text-2xl font-bold tracking-tight text-white">⚙️ Custom Compiler IDE</h1>
        <button
          onClick={handleRun}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 active:scale-95 transition-transform duration-150 text-sm font-semibold rounded-lg shadow"
        >
          ▶ Run Code
        </button>
      </header>

      {/* Main Content */}
      <main className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6 h-[calc(100vh-80px)]">
        {/* Left Panel */}
        <div className="lg:col-span-2 flex flex-col bg-[#0f172a] border border-gray-700 rounded-xl shadow-inner p-4 overflow-hidden">
          <h2 className="text-xl font-semibold mb-3">📝 Code Editor</h2>

          <div className="flex-1 min-h-0 overflow-hidden">
            <CodeEditor code={code} setCode={setCode} />
          </div>

          
        </div>

        {/* Right Panel */}
        <div className="flex flex-col space-y-6 overflow-y-auto pr-1">
          <OutputSection title="🧩 Lexer Tokens" content={tokens.length ? JSON.stringify(tokens, null, 2) : "No tokens"} />
          <OutputSection title="🌲 Parser AST" content={ast ? JSON.stringify(ast, null, 2) : "No AST"} />
          <OutputSection title="⚙️ LLVM IR" content={ir || "No IR"} isMono />
          <ExecutionResult result={result} error={error} />
        </div>
      </main>

    </div>
  );
}

// Output Display Component
function OutputSection({ title, content, isMono = false }) {
  return (
    <section className="bg-[#1e293b] p-4 rounded-xl border border-gray-700 shadow-md transition hover:shadow-xl">
      <h2 className="text-lg font-semibold mb-2">{title}</h2>
      <pre
        className={`text-sm max-h-40 overflow-auto whitespace-pre-wrap ${
          isMono ? "font-mono" : ""
        }`}
      >
        {content}
      </pre>
    </section>
  );
}

// Execution Result Display
function ExecutionResult({ result, error }) {
  return (
    <section className="bg-[#1e293b] p-4 rounded-xl border border-gray-700 shadow-md transition hover:shadow-xl">
      <h2 className="text-lg font-semibold mb-2">💡 Execution Result</h2>

      {error && (
        <p className="text-red-500 font-medium">{error}</p>
      )}

      {!error && result && (
        <>
          <div className="mb-2">
            <strong>Output:</strong>
            <pre className="bg-[#0f172a] p-2 mt-1 rounded-md border border-gray-600 text-sm whitespace-pre-wrap">
              {result.stdout || "(no output)"}
            </pre>
          </div>
          <div>
            <strong>Return Code:</strong> {result.return}
          </div>
        </>
      )}

      {!error && !result && (
        <p className="text-gray-400 text-sm">No result yet.</p>
      )}
    </section>
  );
}

export default App;
