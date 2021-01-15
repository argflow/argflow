import React, { useEffect, useRef } from "react";
import GraphVisualizerPlugin from "./Plugin";
import { ExplanationGraph } from "../common/explanations";

export interface GraphViewProps {
  modelName: string;
  explanationName: string;
  visualiser?: React.MutableRefObject<GraphVisualizerPlugin | null>;
  explanation?: ExplanationGraph | null;
}

const GraphView: React.FC<GraphViewProps> = ({
  modelName,
  explanationName,
  visualiser,
  explanation,
}) => {
  const container = useRef(null);

  useEffect(() => {
    if (container.current) {
      visualiser?.current?.destroy();
      const instance = new GraphVisualizerPlugin(
        modelName,
        explanationName,
        container.current!!,
        explanation
      );
      if (visualiser) {
        visualiser.current = instance;
      }

      return () => {
        if (visualiser) {
          visualiser.current = null;
        }
        instance.destroy();
      };
    }
  }, [modelName, explanationName, container, explanation]);

  return (
    <div
      ref={container}
      style={{ width: "100%", height: "100%", display: "flex" }}
    />
  );
};

export default GraphView;
