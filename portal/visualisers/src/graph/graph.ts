import dagre from "dagre";

import { ArgumentEdge, ArgumentNode } from "../common/explanations";
import { ContributionType, NodeContentType, NodeType } from "../common/types";

export { GraphRenderer } from "./renderer";

export interface Node {
  data: ArgumentNode;
  content: ImageNodeContent | TextNodeContent;
  extra?: any;
  strength: number;
  normalisedStrength?: number;
  active?: boolean;
  highlight?: boolean;
}

export interface ImageNodeContent {
  type: "image";
  image: HTMLImageElement;
}

export interface TextNodeContent {
  type: "text";
  text: string;
  font?: string;
}

export interface Edge extends ArgumentEdge {
  points: { x: number; y: number }[];
  color?: string;
  highlight?: boolean;
}

const measureText = (() => {
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d");

  if (!context) {
    throw new Error("failed to get canvas context for text measurement");
  }

  return (text: string, font: string) => {
    context.font = font;
    return context.measureText(text);
  };
})();

export class Graph {
  private readonly graph = new dagre.graphlib.Graph<Node>({ directed: true });

  // We track this to be able to normalise strengths when doing layout
  private maxNodeStrength = 0;

  public layoutOptions = {
    graph: {
      nodesep: 50,
      ranksep: 50,
    },
    input: {
      size: 200,
    },
    argument: {
      size: 150,
      scaling: "linear" as "linear" | "logarithmic",
    },
  };

  constructor() {
    this.graph.setGraph(this.layoutOptions.graph);
    this.graph.setDefaultEdgeLabel(() => ({}));
  }

  public addNode(name: string, node: Node) {
    this.graph.setNode(name, node);
    if (node.strength && node.strength > this.maxNodeStrength) {
      this.maxNodeStrength = node.strength;
    }
  }

  public addEdge(source: string, target: string, edge: ArgumentEdge) {
    let color;
    switch (edge.contribution_type) {
      case ContributionType.SUPPORT:
        color = "green";
        break;
      case ContributionType.ATTACK:
        color = "red";
        break;
      case ContributionType.INDIRECT:
        color = "#bbbbbb";
        break;
      default:
        color = "black";
        break;
    }

    this.graph.setEdge(source, target, {
      ...edge,
      color,
    });
  }

  public nodes() {
    return this.graph.nodes();
  }

  public node(id: string) {
    return this.graph.node(id);
  }

  public edges() {
    return this.graph.edges();
  }

  public edge(edge: dagre.Edge) {
    return this.graph.edge(edge) as Edge;
  }

  public setNodeHighlight(id: string, highlight: boolean) {
    const node = this.graph.node(id);
    if (node) {
      node.highlight = highlight;
    }
  }

  public setEdgeHighlight(source: string, target: string, highlight: boolean) {
    const edge = this.graph.edge(source, target);
    if (edge) {
      edge.highlight = highlight;
    }
  }

  public layout() {
    for (const id of this.graph.nodes()) {
      const node = this.graph.node(id);
      const data = node.data;

      switch (data.node_type) {
        case NodeType.INPUT: {
          const strength = node.strength
            ? node.strength / this.maxNodeStrength
            : 1;

          if (data.content_type === NodeContentType.STRING) {
            const textNode = node.content as TextNodeContent;
            const size = Math.round(
              this.layoutOptions.input.size *
                0.01 *
                Math.min(Math.max(24 * strength, 12), 48)
            );
            textNode.font = size + "px sans-serif";
            node.width = measureText(textNode.text, textNode.font).width + 16;
            node.height = this.layoutOptions.input.size * size * 0.007;
          } else {
            const size = this.layoutOptions.input.size;
            const image = (node.content as ImageNodeContent).image;
            node.width = size * (image.width / image.height);
            node.height = size;
          }
          break;
        }

        case NodeType.CONCLUSION: {
          const textNode = node.content as TextNodeContent;
          textNode.font = "24px sans-serif";
          node.width = measureText(textNode.text, textNode.font).width + 16;
          node.height = 50;
          node.content;
          break;
        }

        case NodeType.REGULAR: {
          const argSize = this.layoutOptions.argument.size;

          let strength = node.strength ? node.strength : 1;

          if (strength) {
            strength = node.strength / this.maxNodeStrength;
          }

          node.normalisedStrength = strength;

          if (this.layoutOptions.argument.scaling === "logarithmic") {
            strength =
              Math.sqrt(Math.log(strength + 1)) / Math.sqrt(Math.log(2));
          }

          if (data.content_type === NodeContentType.STRING) {
            const textNode = node.content as TextNodeContent;
            const size = Math.round(
              this.layoutOptions.argument.size *
                0.015 *
                Math.min(Math.min(24 * node.strength, 12), 48)
            );
            textNode.font = size + "px sans-serif";
            node.width = measureText(textNode.text, textNode.font).width + 16;
            node.height = this.layoutOptions.argument.size * size * 0.01;
          } else {
            const size = Math.min(
              argSize,
              40 + Math.abs(strength) * (argSize - 40)
            );

            node.width = size;
            node.height = size;
          }

          break;
        }
      }
    }

    dagre.layout(this.graph);

    const size = this.getLayoutSize();
    for (const id of this.graph.nodes()) {
      const node = this.graph.node(id);
      node.x = node.x - size.width / 2;
      node.y = node.y - size.height / 2;
    }

    for (const id of this.graph.edges()) {
      const edge = this.graph.edge(id);
      for (const point of edge.points) {
        point.x = point.x - size.width / 2;
        point.y = point.y - size.height / 2;
      }
    }
  }

  /**
   * Computes the bounds of a dagre graph after the layout algorthm has been applied.
   */
  public getLayoutSize() {
    let minX = Number.MAX_SAFE_INTEGER;
    let minY = Number.MAX_SAFE_INTEGER;
    let maxX = 0;
    let maxY = 0;

    for (const id of this.graph.nodes()) {
      const node = this.graph.node(id);
      if (node.x - node.width / 2 < minX) {
        minX = node.x - node.width / 2;
      }

      if (node.x + node.width / 2 > maxX) {
        maxX = node.x + node.width / 2;
      }

      if (node.y - node.height / 2 < minY) {
        minY = node.y - node.height / 2;
      }

      if (node.y + node.height / 2 > maxY) {
        maxY = node.y + node.height / 2;
      }
    }

    const width = maxX - minX;
    const height = maxY - minY;

    return { width: width, height: height };
  }
}
