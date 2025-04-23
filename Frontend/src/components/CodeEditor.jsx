import React from "react";

const CodeEditor = ({ code, setCode }) => {
  return (
    <div className="p-4 h-full w-full flex flex-col">
      <h2 className="text-xl font-bold mb-2">Code Editor</h2>
      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Write your code here..."
        className="flex-1 w-full p-2 border rounded font-mono bg-gray-100 resize-none"
      />
    </div>
  );
};

export default CodeEditor;
