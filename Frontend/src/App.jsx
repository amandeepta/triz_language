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
      console.log("Response data:", data);

      setTokens(data.tokens || []);
      setAst(data.ast || null);
      setIr(data.ir || "");
      setResult(data.result ? data.result[0] : null);
    } catch (err) {
      console.error("Error:", err);
      setError("An error occurred while sending the code.");
    }
  };

  return (
    <div className="grid grid-cols-6 gap-4 h-screen bg-gray-800 p-4 text-gray-300">
      <div className="col-span-4 flex flex-col">
        <CodeEditor code={code} setCode={setCode} />
        <button
          onClick={handleRun}
          className="mt-4 px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
        >
          Run
        </button>
      </div>

      <div className="col-span-2 flex flex-col space-y-4 overflow-auto">
        <section className="p-2 border border-gray-600 rounded-lg bg-black">
          <h2 className="font-bold mb-2">Lexer Tokens</h2>
          <pre className="text-sm max-h-40 overflow-auto whitespace-pre-wrap">
            {tokens.length > 0 ? JSON.stringify(tokens, null, 2) : "No tokens"}
          </pre>
        </section>

        <section className="p-2 border border-gray-600 rounded-lg bg-black">
          <h2 className="font-bold mb-2">Parser AST</h2>
          <pre className="text-sm max-h-40 overflow-auto whitespace-pre-wrap">
            {ast ? JSON.stringify(ast, null, 2) : "No AST"}
          </pre>
        </section>

        <section className="p-2 border border-gray-600 rounded-lg bg-black">
          <h2 className="font-bold mb-2">LLVM IR</h2>
          <pre className="text-sm max-h-40 overflow-auto whitespace-pre-wrap font-mono">
            {ir || "No IR"}
          </pre>
        </section>

        <section className="p-2 border border-gray-600 rounded-lg bg-black">
          <h2 className="font-bold mb-2">Execution Result</h2>
          {error && <div className="text-red-500">{error}</div>}
          {!error && result && (
            <>
              <div>
                <strong>Output:</strong>
                <pre className="whitespace-pre-wrap">{result.stdout || "(no output)"}</pre>
              </div>
              <div>
                <strong>Return code:</strong> {result.return}
              </div>
            </>
          )}
          {!error && !result && <div>No result</div>}
        </section>
      </div>
    </div>
  );
}

export default App;
