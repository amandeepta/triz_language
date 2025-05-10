import React from "react";

const CodeEditor = ({ code, setCode }) => {
  return (
    <div className="p-4 h-full w-full flex flex-col">
      <h2 className="text-xl font-bold mb-2 text-gray-300">Code Editor</h2>
      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Write your code here..."
        className="flex-1 w-full p-2 border border-gray-600 focus:outline-none focus:border-blue-500 font-mono bg-black resize-none text-gray-300 rounded-lg"
      />
    </div>
  );
};

export default CodeEditor;
