import React from "react";

function AstTree({ node }) {
  if (!node) return null;

  return (
    <div className="ml-4 border-l border-gray-600 pl-4">
      <div className="mb-1">
        <span className="font-mono text-blue-300">{node.type}</span>
        {node.value !== undefined && (
          <span className="text-green-400">: {JSON.stringify(node.value)}</span>
        )}
        {node.name !== undefined && (
          <span className="text-yellow-300"> ({node.name})</span>
        )}
      </div>

      {/* Recurse through children */}
      {node.left && <AstTree node={node.left} />}
      {node.right && <AstTree node={node.right} />}
      {node.body && Array.isArray(node.body) && node.body.map((child, idx) => (
        <AstTree key={idx} node={child} />
      ))}
      {node.statements && node.statements.map((child, idx) => (
        <AstTree key={idx} node={child} />
      ))}
      {node.value && typeof node.value === "object" && !Array.isArray(node.value) && (
        <AstTree node={node.value} />
      )}
    </div>
  );
}

export default AstTree;
