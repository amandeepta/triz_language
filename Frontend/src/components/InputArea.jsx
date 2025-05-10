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
        className="h-100 w-full p-2 border border-gray-600 focus:outline-none focus:border-blue-500 font-mono bg-black text-gray-300 resize-none rounded-lg"
      />
    </div>
  );
};

export default InputArea;
