import React, { useEffect, useLayoutEffect, useRef, useState } from "react";
import MenuIcon from "@material-ui/icons/Menu";
import ZoomInIcon from "@material-ui/icons/ZoomIn";
import ZoomOutIcon from "@material-ui/icons/ZoomOut";
import {
  Fab,
  FormControl,
  Typography,
  Slider,
  Button,
  makeStyles,
  MenuItem,
  Select,
} from "@material-ui/core";

import GraphView from "./GraphView";
import GraphVisualizerPlugin from "./Plugin";
import { ExplanationGraph } from "../common/explanations";

const useStyles = makeStyles({
  root: {
    width: "100%",
    height: "100%",
    position: "relative",
  },
  menuButton: {
    position: "absolute",
    margin: 16,
  },
  zoomControls: {
    position: "absolute",
    top: 0,
    right: 0,
    margin: 16,
    display: "flex",
    flexDirection: "column",
  },
  menuOverlay: {
    transition: "300ms",
    background: "rgba(0, 0, 0, 0.5)",
    position: "absolute",
    top: 0,
    bottom: 0,
    left: 0,
    right: 0,
  },
  menu: {
    transition: "300ms",
    width: 240,
    background: "white",
    position: "absolute",
    top: 0,
    bottom: 0,
    display: "flex",
    flexDirection: "column",
  },
  menuItem: {
    margin: 16,
  },
});

export interface Props {
  modelName: string;
  explanationName: string;
}

const App: React.FC<Props> = ({ modelName, explanationName }) => {
  const classes = useStyles();

  const [showMenu, setShowMenu] = useState(false);

  const [opacity, setOpacity] = useState<number>(0);
  const [left, setLeft] = useState(-240);

  const [horizontalSpacing, setHorizontalSpacing] = useState(50);
  const [verticalSpacing, setVerticalSpacing] = useState(50);
  const [inputSize, setInputSize] = useState(200);
  const [argumentSize, setArgumentSize] = useState(150);
  const [selectedPruningLimit, setSelectedPruningLimit] = useState(20);
  const [selectedPruningLayerLimit, setSelectedPruningLayerLimit] = useState(5);
  const [appliedPruningLimit, setAppliedPruningLimit] = useState(20);
  const [appliedPruningLayerLimit, setAppliedPruningLayerLimit] = useState(5);
  const [scaling, setScaling] = useState<"linear" | "logarithmic">("linear");

  const [explanation, setExplanation] = useState<ExplanationGraph | null>(null);

  if (explanation === null) {
    fetchExplanation(appliedPruningLimit, appliedPruningLayerLimit);
  }

  const visualiser = useRef<GraphVisualizerPlugin | null>(null);

  useLayoutEffect(() => {
    if (showMenu) {
      window.requestAnimationFrame(() => {
        setOpacity(1);
        setLeft(0);
      });
    }
  }, [showMenu]);

  useEffect(() => {
    const graph = visualiser.current?.getGraph();
    if (graph) {
      graph.layoutOptions.graph.nodesep = horizontalSpacing;
      graph.layoutOptions.graph.ranksep = verticalSpacing;
      graph.layoutOptions.input.size = inputSize;
      graph.layoutOptions.argument.size = argumentSize;
      graph.layoutOptions.argument.scaling = scaling;
      graph.layout();
    }

    const renderer = visualiser.current?.getRenderer();
    if (renderer) {
      renderer.render();
    }
  }, [horizontalSpacing, verticalSpacing, inputSize, argumentSize, scaling]);

  function zoom(value: number) {
    const v = visualiser.current;
    if (v) {
      const renderer = v.getRenderer();
      if (renderer) {
        renderer.camera.scale += value;
        renderer.render();
      }
    }
  }

  function applyPruning(
    selectedPruningLimit: number,
    selectedPruningLayerLimit: number,
    appliedPruningLimit: number,
    appliedPruningLayerLimit: number
  ) {
    if (
      selectedPruningLimit !== appliedPruningLimit ||
      selectedPruningLayerLimit !== appliedPruningLayerLimit
    ) {
      setAppliedPruningLimit(selectedPruningLimit);
      setAppliedPruningLayerLimit(selectedPruningLayerLimit);
      fetchExplanation(selectedPruningLimit, selectedPruningLayerLimit);
    }
  }

  function fetchExplanation(
    appliedPruningLimit: number,
    appliedPruningLayerLimit: number
  ) {
    fetch(
      `/api/models/${modelName}/explanations/${explanationName}/visualisers/argflow_ui.visualisers.GraphVisualiser`,
      {
        method: "POST",
        body: JSON.stringify({
          prune: true,
          limit: appliedPruningLimit,
          layer_limit: appliedPruningLayerLimit,
        }),
      }
    )
      .then((res) => res.json())
      .then((data) => {
        setExplanation(data);
      });
  }

  return (
    <div className={classes.root}>
      <Fab className={classes.menuButton} onClick={() => setShowMenu(true)}>
        <MenuIcon />
      </Fab>
      <div className={classes.zoomControls}>
        <Fab
          size="small"
          style={{ marginBottom: 16 }}
          onClick={() => zoom(0.2)}
        >
          <ZoomInIcon />
        </Fab>
        <Fab size="small" onClick={() => zoom(-0.2)}>
          <ZoomOutIcon />
        </Fab>
      </div>
      {showMenu && (
        <>
          <div
            className={classes.menuOverlay}
            style={{ opacity }}
            onClick={() => {
              setOpacity(0);
              setLeft(-240);
              setTimeout(() => setShowMenu(false), 300);
            }}
          />
          <div className={classes.menu} style={{ left }}>
            <FormControl className={classes.menuItem}>
              <Typography>Horizontal Spacing</Typography>
              <Slider
                min={30}
                max={200}
                value={horizontalSpacing}
                onChange={(_e, v) => setHorizontalSpacing(v as number)}
              />
            </FormControl>
            <FormControl className={classes.menuItem}>
              <Typography>Vertical Spacing</Typography>
              <Slider
                min={30}
                max={200}
                value={verticalSpacing}
                onChange={(_e, v) => setVerticalSpacing(v as number)}
              />
            </FormControl>
            <FormControl className={classes.menuItem}>
              <Typography>Input Size</Typography>
              <Slider
                min={50}
                max={500}
                value={inputSize}
                onChange={(_e, v) => setInputSize(v as number)}
              />
            </FormControl>
            <FormControl className={classes.menuItem}>
              <Typography>Argument Size</Typography>
              <Slider
                min={50}
                max={500}
                value={argumentSize}
                onChange={(_e, v) => setArgumentSize(v as number)}
              />
            </FormControl>
            <FormControl className={classes.menuItem}>
              <Typography>Scaling</Typography>
              <Select
                value={scaling}
                onChange={(e) => setScaling(e.target.value as any)}
              >
                <MenuItem value="linear">Linear</MenuItem>
                <MenuItem value="logarithmic">Logarithmic</MenuItem>
              </Select>
            </FormControl>
            <FormControl className={classes.menuItem}>
              <Typography>Regular Nodes Limit</Typography>
              <Slider
                min={0}
                max={explanation?.total_nodes || 20}
                value={selectedPruningLimit}
                onChange={(_e, v) => setSelectedPruningLimit(v as number)}
              />
            </FormControl>
            <FormControl className={classes.menuItem}>
              <Typography>Max Nodes Per Layer</Typography>
              <Slider
                min={0}
                max={explanation?.total_nodes || 20}
                value={selectedPruningLayerLimit}
                onChange={(_e, v) => setSelectedPruningLayerLimit(v as number)}
              />
            </FormControl>
            <FormControl className={classes.menuItem}>
              <Button
                variant="contained"
                onClick={() =>
                  applyPruning(
                    selectedPruningLimit,
                    selectedPruningLayerLimit,
                    appliedPruningLimit,
                    appliedPruningLayerLimit
                  )
                }
              >
                Apply Pruning
              </Button>
            </FormControl>
            <FormControl className={classes.menuItem}>
              <Button
                variant="contained"
                onClick={() => {
                  const renderer = visualiser.current?.getRenderer();
                  if (renderer) {
                    renderer.camera.x = 0;
                    renderer.camera.y = 0;
                    renderer.camera.scale = 1;
                    renderer.render();
                  }
                }}
              >
                Reset Camera
              </Button>
            </FormControl>
            <FormControl className={classes.menuItem}>
              <Button
                variant="contained"
                onClick={() => {
                  const canvas = visualiser.current?.getCanvas();
                  if (canvas) {
                    const a = document.createElement("a");
                    a.href = canvas.toDataURL();
                    a.setAttribute("download", "graph.png");
                    a.click();
                  }
                }}
              >
                Export as Image
              </Button>
            </FormControl>
          </div>
        </>
      )}
      <GraphView
        modelName={modelName}
        explanationName={explanationName}
        visualiser={visualiser}
        explanation={explanation}
      />
    </div>
  );
};

export default App;
