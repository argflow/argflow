import { Graph } from "./graph";
import { NodeType } from "../common/types";

export class GraphRenderer {
  public readonly camera = { x: 0, y: 0, scale: 1 };

  public isHighlightEnabled = false;

  constructor(
    private readonly graph: Graph,
    private readonly canvas: HTMLCanvasElement
  ) {}

  public render(offset = { x: 0, y: 0 }) {
    const ctx = this.canvas.getContext("2d")!!;

    // Update the dimensions of the drawing area with the actual size of the canvas on the screen
    this.canvas.width = this.canvas.clientWidth;
    this.canvas.height = this.canvas.clientHeight;

    // Clear the current viewport
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Apply global transformations.
    // - We transform the coordinate system so that the origin is at the center rather
    //   than the top-left corner.
    // - We then also apply the camera offset and scale transformations.
    ctx.translate(
      this.canvas.width / 2 + this.camera.x + offset.x,
      this.canvas.height / 2 + this.camera.y + offset.y
    );
    ctx.scale(this.camera.scale, this.camera.scale);

    for (const id of this.graph.nodes()) {
      const node = this.graph.node(id);
      switch (node.content.type) {
        case "image": {
          // Draw a translucent border if the node is active
          // This is done by drawing a rect under the image that
          // is slightly larger than the image
          if (node.active) {
            ctx.save();
            ctx.fillStyle = "rgba(0, 0, 0, 0.2)";
            ctx.fillRect(
              node.x - node.width / 2 - 4,
              node.y - node.height / 2 - 4,
              node.width + 8,
              node.height + 8
            );
            ctx.restore();
          }

          // Draw the image itself
          ctx.drawImage(
            node.content.image,
            node.x - node.width / 2,
            node.y - node.height / 2,
            node.width,
            node.height
          );

          // If highlighting is enabled, we darken any non-highlighted
          // nodes (other than input and conclusion).
          if (
            this.isHighlightEnabled &&
            node.data.node_type === NodeType.REGULAR &&
            !node.highlight
          ) {
            ctx.save();
            ctx.fillStyle = "rgba(0,0,0,0.5)";
            ctx.fillRect(
              node.x - node.width / 2,
              node.y - node.height / 2,
              node.width,
              node.height
            );
            ctx.restore();
          }
          break;
        }

        case "text": {
          // draw background
          ctx.beginPath();
          ctx.rect(
            node.x - node.width / 2,
            node.y - node.height / 2,
            node.width,
            node.height
          );
          ctx.stroke();

          // draw foreground text
          ctx.font = node.content.font!!;
          ctx.textBaseline = "middle";
          ctx.fillText(node.content.text, node.x - node.width / 2 + 8, node.y);
          break;
        }
      }
    }

    for (const id of this.graph.edges()) {
      const edge = this.graph.edge(id);
      let from = edge.points[0];

      ctx.beginPath();

      // Draw lines between all control points for the edge
      for (let i = 1; i < edge.points.length; i++) {
        let to = edge.points[i];

        ctx.moveTo(from.x, from.y);
        ctx.lineTo(to.x, to.y);

        from = to;
      }

      // Draw an arrow at the end of the last line segment of the edge
      const a = edge.points[edge.points.length - 2];
      const b = edge.points[edge.points.length - 1];

      // Increase the edge width for highlighted edges
      ctx.lineWidth = this.isHighlightEnabled && edge.highlight ? 3 : 1;
      ctx.strokeStyle = edge.color || "black";
      ctx.stroke();

      // Determine the angle of the line
      const angle = Math.atan2(b.y - a.y, b.x - a.x);

      // Move to tip of arrow
      ctx.moveTo(b.x, b.y);

      // Line from tip to first point
      ctx.lineTo(
        b.x - 10 * Math.cos(angle - Math.PI / 6),
        b.y - 10 * Math.sin(angle - Math.PI / 6)
      );

      // Line from first point to second point
      ctx.lineTo(
        b.x - 10 * Math.cos(angle + Math.PI / 6),
        b.y - 10 * Math.sin(angle + Math.PI / 6)
      );

      // Line from second point back to tip
      ctx.lineTo(b.x, b.y);

      ctx.fillStyle = edge.color || "black";
      ctx.fill();
    }
  }
}
