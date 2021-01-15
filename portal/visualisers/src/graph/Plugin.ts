import { Graph, GraphRenderer, Node } from "./graph";
import { payloadToImg } from "./word-cloud";
import { NodeContentType, NodeType } from "../common/types";

import { ExplanationGraph } from "../common/explanations";

/**
 * A point in 2D space.
 */
interface Point {
  x: number;
  y: number;
}

/**
 * Preprocesses the explanation graph to replace all image urls with an actual preloaded
 * `HTMLImageElement`.
 */
async function preloadImages(explanation: ExplanationGraph) {
  const promises = [];

  function load(src: string) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.src = src;
    });
  }

  for (const i in explanation.nodes) {
    const node = explanation.nodes[i];
    if (node.content_type === NodeContentType.STRING) continue;
    switch (node.node_type) {
      case NodeType.INPUT:
        promises.push(
          load(payloadToImg(node.payload, node.content_type)).then(
            (img) => (node.payload = img)
          )
        );
        break;

      case NodeType.REGULAR:
        if (
          typeof node.payload === "string" ||
          node.payload instanceof String
        ) {
          promises.push(
            load(payloadToImg(node.payload, node.content_type)).then(
              (img) => (node.payload = { primary: img })
            )
          );
        } else {
          promises.push(
            load("/api/resources/" + node.payload.feature.payload).then(
              (img) => (node.payload.primary = img)
            )
          );
          promises.push(
            load(
              payloadToImg(node.payload.filter.payload, node.content_type)
            ).then((img) => (node.payload.secondary = img))
          );
        }
        break;
    }
  }

  await Promise.all(promises);
}

class MouseTracker {
  private origin: Point | null = null;
  private drag = { x: 0, y: 0 };

  private active: Node | null = null;

  public down: ((node: Node) => void) | null = null;
  public move: ((drag: Point, node: Node | null) => void) | null = null;
  public up: ((isClick: boolean, node: Node | null) => void) | null = null;

  constructor(private visualizer: GraphVisualizerPlugin) {
    this.visualizer
      .getCanvas()
      .addEventListener("mousedown", this.onMouseDown.bind(this));
  }

  private onMouseDown(e: MouseEvent) {
    // Record the initial cursor point at the start of the interaction
    this.origin = { x: e.clientX, y: e.clientY };

    // Add event listeners to detect movement and button release
    // This is added to the body (rather than the canvas, like the mousedown) so that
    // if the user moves the mouse off the canvas (onto the side menu for example) while dragging,
    // it doesn't break if they release the mouse button before moving back to the canvas
    document.body.addEventListener("mousemove", this.onMouseMove.bind(this));
    document.body.addEventListener("mouseup", this.onMouseUp.bind(this));

    const target = e.currentTarget as any | null;
    const { left, top } = target?.getBoundingClientRect();

    // The following code checks to see if the user has clicked on
    // a node (or just some empty space or something)

    const canvas = this.visualizer.getCanvas();
    const camera = this.visualizer.getCamera();

    // Transform the cursor position from screen space to world space (the same
    // coordinate space as the nodes):
    // - first we convert from screen space to canvas coordinates
    // - then the origin of the coordinate space is moved to the center of the canvas
    // - finally the camera offset is subtracted and the result is divided by the zoom scale factor
    //   to get world space coordinates
    const pos = {
      x: (e.clientX - left - canvas.width / 2 - camera.x) / camera.scale,
      y: (e.clientY - top - canvas.height / 2 - camera.y) / camera.scale,
    };

    const graph = this.visualizer.getGraph()!!;
    for (const id of graph.nodes()) {
      const node = graph.node(id);
      // Compute the top-left corner of the node
      const nodePos = {
        x: node.x - node.width / 2,
        y: node.y - node.height / 2,
      };

      // Check if the cursor position is within the node's bounding rect
      if (
        pos.x >= nodePos.x &&
        pos.x <= nodePos.x + node.width &&
        pos.y >= nodePos.y &&
        pos.y <= nodePos.y + node.height
      ) {
        if (node.data.node_type === NodeType.REGULAR) {
          this.active = node;
          this.down?.(node);
          break;
        }
      }
    }
  }

  private onMouseMove(e: MouseEvent) {
    if (this.origin) {
      document.body.style.cursor = "move";

      // Update the current drag offset from the start of the interaction
      this.drag.x = e.clientX - this.origin.x;
      this.drag.y = e.clientY - this.origin.y;

      this.move?.(this.drag, this.active);
    }
  }

  private onMouseUp() {
    if (!this.origin) return;

    document.body.removeEventListener("mousemove", this.onMouseMove);
    document.body.removeEventListener("mouseup", this.onMouseUp);

    document.body.style.cursor = "default";

    this.origin = null;

    const camera = this.visualizer.getCamera();

    camera.x += this.drag.x;
    camera.y += this.drag.y;

    this.up?.(
      Math.abs(this.drag.x) < 5 && Math.abs(this.drag.y) < 5,
      this.active
    );

    this.active = null;

    this.drag.x = 0;
    this.drag.y = 0;
  }
}

export default class GraphVisualizerPlugin {
  private canvas: HTMLCanvasElement;

  private graph?: Graph;
  private renderer?: GraphRenderer;

  private mouseTracker: MouseTracker | null = null;
  private resizeObserver = new ResizeObserver(this.onResize.bind(this));

  constructor(
    modelName: string,
    explanationName: string,
    private readonly container: HTMLDivElement,
    private explanation?: ExplanationGraph | null
  ) {
    this.canvas = document.createElement("canvas");

    const bounds = this.container.getBoundingClientRect();

    this.canvas.style.width = bounds.width + "px";
    this.canvas.style.height = bounds.height + "px";

    // Remove previously added canvas elements
    // TODO: This seems a bit hacky, there should be a better way
    const containerChildren = this.container.children;
    for (var i = 0; i < containerChildren.length; i++) {
      if (containerChildren[i].nodeName === "CANVAS") {
        this.container.removeChild(containerChildren[i]);
      }
    }

    this.container.appendChild(this.canvas);

    if (explanation) {
      this._init();
    }
  }

  public getCanvas() {
    return this.canvas;
  }

  public getCamera() {
    return this.renderer!!.camera;
  }

  public getGraph() {
    return this.graph;
  }

  public getRenderer() {
    return this.renderer;
  }

  private async _init() {
    await preloadImages(this.explanation!!);

    this.graph = this.buildGraph();
    this.renderer = new GraphRenderer(this.graph, this.canvas);

    // Set the initial camera scale to the adjust to the width of the graph (+ a bit of margin)
    const size = this.graph.getLayoutSize();
    const xScale = this.canvas.clientWidth / (size.width + 64);
    const yScale = this.canvas.clientHeight / (size.height + 64);
    if (Math.abs(xScale) > Math.abs(yScale)) {
      this.renderer.camera.scale = yScale;
    } else {
      this.renderer.camera.scale = xScale;
    }

    this.renderer.render();

    this.mouseTracker = new MouseTracker(this);

    this.mouseTracker.move = (drag) => this.renderer!!.render(drag);

    this.mouseTracker.down = (node) => {
      node.active = true;
      this.renderer!!.render();
    };

    this.mouseTracker.up = (isClick, node) => {
      if (node) {
        node.active = false;
        this.renderer!!.render();

        if (
          isClick &&
          node.data.payload.secondary &&
          node.data.content_type !== NodeContentType.STRING
        ) {
          new GraphOverlay(this.container, node);
        }
      }
    };

    this.canvas.addEventListener("wheel", (e) => {
      const camera = this.renderer!!.camera;
      // TODO: Improve this calculation somehow to have a more linear scrolling behaviour
      camera.scale = Math.max(camera.scale - e.deltaY * 0.001, 0.1);
      this.renderer!!.render();
    });

    this.resizeObserver.observe(this.container);
  }

  private buildGraph() {
    const graph = new Graph();

    for (const [i, node] of Object.entries(this.explanation!!.nodes)) {
      switch (node.node_type) {
        case NodeType.INPUT:
          if (node.content_type === NodeContentType.STRING) {
            graph.addNode(i.toString(), {
              data: node,
              strength: node.strength,
              content: {
                type: "text",
                text: node.payload,
              },
            });
          } else {
            graph.addNode(i.toString(), {
              data: node,
              strength: node.strength,
              content: {
                type: "image",
                image: node.payload,
              },
            });
          }
          break;

        case NodeType.CONCLUSION:
          graph.addNode(i.toString(), {
            data: node,
            strength: node.strength,
            content: {
              type: "text",
              text: node.payload + " (" + node.certainty?.toFixed(2) + "%)",
            },
          });
          break;

        case NodeType.REGULAR:
          if (node.content_type === NodeContentType.STRING) {
            graph.addNode(i.toString(), {
              data: node,
              strength: node.strength,
              content: {
                type: "text",
                text: node.payload,
              },
            });
          } else {
            graph.addNode(i.toString(), {
              data: node,
              strength: node.strength,
              content: {
                type: "image",
                image: node.payload.primary,
              },
            });
          }
          break;

        case NodeType.NONE:
          throw new Error("Shouldn't be trying to add none node!");
      }

      for (const ch in node.children) {
        graph.addEdge(i.toString(), ch.toString(), node.children[ch]);
      }
    }

    graph.layout();

    return graph;
  }

  private onResize() {
    const bounds = this.container.getBoundingClientRect();

    this.canvas.style.width = bounds.width + "px";
    this.canvas.style.height = bounds.height + "px";

    this.renderer?.render();
  }

  public destroy() {
    this.resizeObserver.unobserve(this.canvas);
  }
}

class GraphOverlay {
  private overlay: HTMLDivElement;
  private content: HTMLDivElement;

  constructor(private container: HTMLDivElement, node: Node) {
    this.overlay = this.createOverlay();
    this.content = this.createOverlayContent();

    const secondaryContentContainer = document.createElement("div");

    secondaryContentContainer.style.flex = "5";
    secondaryContentContainer.style.padding = "16px";
    secondaryContentContainer.style.display = "flex";
    secondaryContentContainer.style.alignItems = "center";
    secondaryContentContainer.style.justifyContent = "center";

    this.content.appendChild(secondaryContentContainer);

    const secondaryContent = node.data.payload.secondary.cloneNode() as HTMLImageElement;

    secondaryContent.style.maxWidth = "100%";
    secondaryContent.addEventListener("click", (e) => e.stopPropagation());

    secondaryContentContainer.appendChild(secondaryContent);

    const arrowContainer = document.createElement("div");

    arrowContainer.style.flex = "1";
    arrowContainer.style.display = "flex";
    arrowContainer.style.alignItems = "center";
    arrowContainer.style.justifyContent = "center";
    arrowContainer.innerHTML = `
      <svg viewBox="0 0 200 100" height="100" fill="#00ea00">
        <defs>
          <marker
            id="arrowhead"
            markerWidth="5"
            markerHeight="7"
            refX="0"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 5 3.5, 0 7" />
          </marker>
        </defs>
        <line
          x1="0"
          y1="50"
          x2="150"
          y2="50"
          stroke="#00ea00"
          stroke-width="8"
          marker-end="url(#arrowhead)"
        />
      </svg>
    `;

    this.content.appendChild(arrowContainer);

    const featureContainer = document.createElement("div");

    featureContainer.style.flex = "5";
    featureContainer.style.padding = "16px";
    featureContainer.style.display = "flex";
    featureContainer.style.flexDirection = "column";
    featureContainer.style.alignItems = "center";
    featureContainer.style.justifyContent = "center";

    this.content.appendChild(featureContainer);

    const primaryContent = node.data.payload.primary.cloneNode() as HTMLImageElement;

    primaryContent.style.maxWidth = "100%";
    primaryContent.style.border = "1px solid black";
    primaryContent.addEventListener("click", (e) => e.stopPropagation());

    featureContainer.appendChild(primaryContent);

    const strength = document.createElement("p");

    console.log(node);

    strength.innerText =
      "Strength: " + (node.normalisedStrength || node.strength).toFixed(2);
    strength.style.fontFamily = "sans-serif";
    strength.style.backgroundColor = "white";
    strength.style.padding = "8px";
    primaryContent.style.border = "1px solid black";
    strength.style.borderRadius = "4px";

    featureContainer.appendChild(strength);
  }

  private createOverlay() {
    const overlay = document.createElement("div");
    const bounds = this.container.getBoundingClientRect();

    overlay.style.position = "absolute";
    overlay.style.width = bounds.width + "px";
    overlay.style.height = bounds.height + "px";
    overlay.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
    overlay.style.opacity = "0";
    overlay.style.transition = "opacity 400ms";

    this.container.appendChild(overlay);

    const observer = new ResizeObserver(() => {
      const bounds = this.container.getBoundingClientRect();
      overlay.style.width = bounds.width + "px";
      overlay.style.height = bounds.height + "px";
    });

    const remove = () => {
      overlay.removeEventListener("click", remove);
      observer.unobserve(this.container);
      overlay.style.opacity = "0";
      window.setTimeout(() => this.container.removeChild(overlay), 400);
    };

    observer.observe(this.container);
    overlay.addEventListener("click", remove);

    window.requestAnimationFrame(() => {
      overlay.style.opacity = "1";
    });

    return overlay;
  }

  private createOverlayContent() {
    const content = document.createElement("div");

    content.style.width = "100%";
    content.style.height = "100%";
    content.style.display = "flex";

    this.overlay.appendChild(content);

    return content;
  }
}
