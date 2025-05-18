import React from "react";
import Tree from "react-d3-tree";

const containerStyles = {
  width: "100%",
  height: "400px",
};

const ASTTree = ({ data }) => {
  if (!data) return <div>No AST available</div>;

  // Recursively convert raw AST JSON into react-d3-tree format
  const convertToTree = (node) => {
    if (!node || typeof node !== "object") return { name: String(node) };

    const children = Object.entries(node).map(([key, value]) => {
      if (Array.isArray(value)) {
        return {
          name: key,
          children: value.map(convertToTree),
        };
      } else if (typeof value === "object") {
        return {
          name: key,
          children: [convertToTree(value)],
        };
      } else {
        return {
          name: `${key}: ${value}`,
        };
      }
    });

    return {
      name: node.type || "Node",
      children,
    };
  };

  const treeData = [convertToTree(data)];

  return (
    <div style={containerStyles}>
      <Tree data={treeData} orientation="vertical" />
    </div>
  );
};

export default ASTTree;
