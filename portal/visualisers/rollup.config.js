import path from "path";

import babel from "@rollup/plugin-babel";
import commonjs from "@rollup/plugin-commonjs";
import replace from "@rollup/plugin-replace";
import typescript from "@rollup/plugin-typescript";
import { nodeResolve } from "@rollup/plugin-node-resolve";

const output = path.resolve(__dirname, "../argflow_ui/visualisers/js");

export default [
  {
    input: "src/conversation/index.js",
    output: {
      file: path.join(output, "argflow-ui-conversation.js"),
      format: "es",
    },
    plugins: [
      typescript(),
      babel({ babelHelpers: "bundled" }),
      nodeResolve({ browser: true }),
      commonjs(),
      replace({
        "process.env.NODE_ENV": JSON.stringify("production"),
      }),
    ],
  },
  {
    input: "src/graph/index.tsx",
    output: {
      file: path.join(output, "argflow-ui-graph.js"),
      format: "es",
    },
    plugins: [
      typescript(),
      babel({ babelHelpers: "bundled" }),
      nodeResolve({ browser: true }),
      commonjs(),
      replace({
        "process.env.NODE_ENV": JSON.stringify("production"),
      }),
    ],
  },
];
