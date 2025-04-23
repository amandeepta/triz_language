import React from "react";

const InputArea = ({ input, setInput, onRun }) => {
  return (
    <div className="h-full flex flex-col p-2">
      <button
        onClick={onRun}
        className="mb-2 rounded-xl p-2 bg-blue-500 text-white font-bold cursor-pointer"
      >
        Run
      </button>

      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Enter Input Here…"
        className="flex-1 w-full p-2 border rounded font-mono bg-gray-100 resize-none"
      />
    </div>
  );
};

export default InputArea;
