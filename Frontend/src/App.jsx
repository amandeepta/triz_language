import React, { useState } from "react";
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
      const response = await axios.post("http://127.0.0.1:5000/compile", {
        inputCode: code,
      });

      console.log("Response data:", response.data);
      setOutput(JSON.stringify(response.data, null, 2));
    } catch (error) {
      console.error("Error:", error);
      setOutput("An error occurred while sending the code.");
    }
  };

  return (
    <div className="grid grid-cols-6 gap-4 h-screenb bg-gray-800">
      <div className="col-span-4 flex">
        <CodeEditor code={code} setCode={setCode} />
      </div>

      <div className="col-span-2 flex flex-col">
        <div className="flex-1 overflow-auto">
          <InputArea input={input} setInput={setInput} onRun={handleRun} />
        </div>
        <div className="h-105 w-200 p-2 overflow-auto border border-gray-600 bg-black text-gray-300 rounded-lg">
          <h2 className="font-bold text-gray-300">Output</h2>
          <div>{output}</div>
        </div>
      </div>
    </div>
  );
}

export default App;
