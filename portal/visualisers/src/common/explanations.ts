import {
  Direction,
  NodeType,
  NodeContentType,
  ContributionType,
} from "./types";

/**
 * API response
 */
export interface ExplanationResponse {
  explanation: ExplanationGraph;
  interactions: {
    node: number;
    direction: Direction;
  }[];
  interaction_results: InteractionResult[];
}

/**
 * Explanation graph data as returned by the API.
 */
export interface ExplanationGraph {
  name: string;
  input: number[];
  conclusion: number[];
  nodes: Record<number, ArgumentNode>;
  total_nodes?: number;
}

/**
 * Node data as returned by the API.
 */
export interface ArgumentNode {
  node_type: NodeType;
  content_type: NodeContentType;
  children: Record<number, ArgumentEdge>;
  payload: any;
  strength: number;
  certainty?: number;
}

export interface InteractionResult {
  endpoint: number;
  contribution: {
    contribution_type: ContributionType;
  };
}

/**
 * Child data in the children array
 */
export interface ArgumentEdge {
  contribution_type: string;
}

export function nodeToString(node: ArgumentNode, nodeId: String) {
  if (node.content_type === NodeContentType.STRING) {
    return node.payload;
  }

  return nodeId;
}
