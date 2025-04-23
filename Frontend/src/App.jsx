import React, { useEffect, useState } from "react";
import CodeEditor from "./components/CodeEditor";
import InputArea from "./components/InputArea";
import axios from "axios";

function App() {
  const [code, setCode] = useState("");
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("");

  const handleRun = async () => {
    console.log("=== Running code ===");
    console.log("Code:\n", code);
    console.log("Input:\n", input);

    try {
      const response = await axios.post("http://127.0.0.1:5000/", {
        inputCode: code,
        input: input,
      });

      console.log("Response data:", response.data);
      setOutput(JSON.stringify(response.data, null, 2));
    } catch (error) {
      console.error("Error:", error);
      setOutput("An error occurred while sending the code.");
    }
  };

  return (
    <div className="grid grid-cols-6 gap-4 h-screen">
      <div className="col-span-4 border flex">
        <CodeEditor code={code} setCode={setCode} />
      </div>

      <div className="col-span-2 border flex flex-col">
        <div className="flex-1 overflow-auto">
          <InputArea input={input} setInput={setInput} onRun={handleRun} />
        </div>
        <div className="h-32 border p-2 overflow-auto">
          <h2 className="font-bold">Output</h2>
          <div>{output}</div>
        </div>
      </div>
    </div>
  );
}

export default App;
