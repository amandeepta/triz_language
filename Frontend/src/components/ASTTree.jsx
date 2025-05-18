import React, { useState } from "react";

// Recursive Tree Node
export default function ASTNode({ node }) {
  const [open, setOpen] = useState(true);

  if (!node || typeof node !== "object") {
    return <span>{String(node)}</span>;
  }

  const keys = Object.keys(node);

  return (
    <div className="pl-4 border-l border-gray-600">
      {keys.map((key) => {
        const child = node[key];

        // If child is a primitive or null
        if (typeof child !== "object" || child === null) {
          return (
            <div key={key} className="mb-1">
              <strong>{key}:</strong> <span>{String(child)}</span>
            </div>
          );
        }

        // If child is an array, render each element
        if (Array.isArray(child)) {
          return (
            <div key={key} className="mb-1">
              <strong>{key}:</strong>
              <div className="pl-4">
                {child.length > 0 ? (
                  child.map((item, idx) => (
                    <div key={idx} className="mb-1">
                      <button
                        className="font-semibold text-blue-400 hover:underline"
                        onClick={() => setOpen(!open)}
                      >
                        {open ? "▼" : "▶"} [{idx}]
                      </button>
                      {open && <ASTNode node={item} />}
                    </div>
                  ))
                ) : (
                  <span> (empty)</span>
                )}
              </div>
            </div>
          );
        }

        // child is an object (nested node)
        return (
          <div key={key} className="mb-1">
            <button
              className="font-semibold text-blue-400 hover:underline"
              onClick={() => setOpen(!open)}
            >
              {open ? "▼" : "▶"} {key}
            </button>
            {open && <ASTNode node={child} />}
          </div>
        );
      })}
    </div>
  );
}
