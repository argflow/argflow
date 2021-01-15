import React, { useEffect, useLayoutEffect, useRef } from "react";
import { useParams } from "react-router-dom";

import { makeStyles } from "@material-ui/core";

const useStyles = makeStyles({
  root: {
    height: "100%",
    display: "flex",
    flexDirection: "column",
  },
  visualiser: {
    flexGrow: 1,
    display: "flex",
    flexDirection: "column",
  },
});

function SplitView({ left, right }) {
  const container = useRef(null);
  const leftPane = useRef(null);
  const rightPane = useRef(null);
  const dragger = useRef(null);

  useLayoutEffect(() => {
    if (left) {
      left.current = leftPane.current;
    }

    if (right) {
      right.current = rightPane.current;
    }

    const bounds = container.current.getBoundingClientRect();
    const d = dragger.current;

    let width = bounds.width / 2;

    leftPane.current.style.width = width + "px";
    rightPane.current.style.width = width + "px";

    let origin = 0;
    let drag = 0;

    function onMouseDown(e) {
      document.body.style.cursor = "ew-resize";

      origin = e.clientX;

      document.addEventListener("mouseup", onMouseUp, true);
      document.addEventListener("mousemove", onMouseMove, true);
    }

    function onMouseUp() {
      document.body.style.cursor = "default";

      width += drag;

      origin = 0;
      drag = 0;

      document.removeEventListener("mouseup", onMouseUp, true);
      document.removeEventListener("mousemove", onMouseMove, true);
    }

    function onMouseMove(e) {
      // This stops random text from being selected while dragging,
      // doesn't seem to work in firefox though.
      e.preventDefault();

      drag = e.clientX - origin;

      const newWidth = Math.min(
        Math.max(100, width + drag),
        bounds.width - 100
      );

      leftPane.current.style.width = newWidth + "px";
      rightPane.current.style.width = bounds.width - newWidth - 8 + "px";
    }

    d.addEventListener("mousedown", onMouseDown);

    return () => {
      d.removeEventListener("mousedown", onMouseDown);
      left.current = null;
      right.current = null;
    };
  }, [left, right, container, leftPane, rightPane, dragger]);

  return (
    <div ref={container} style={{ display: "flex", height: "100%" }}>
      <div ref={leftPane} style={{ display: "flex" }}></div>
      <div
        ref={dragger}
        style={{ background: "#f4f7f9", width: 8, cursor: "ew-resize" }}
      />
      <div ref={rightPane} style={{ display: "flex" }}></div>
    </div>
  );
}

function loadVisualiser(modelName, explanationName, visualiser, container) {
  const main = visualiser.main;

  let socket = null;
  let instance = null;

  import(/* webpackIgnore: true */ main).then(async (mod) => {
    socket = new WebSocket(
      `ws://${window.location.host}/ws/session?visualiser=${visualiser.id}&model=${modelName}&explanation=${explanationName}`
    );

    socket.addEventListener("open", () => {
      instance = new mod.default(modelName, explanationName, container, socket);
      console.log("instantiated", instance);
    });
  });

  return () => {
    if (instance) {
      console.log("destroying", instance);
      socket.close();
      instance.destroy?.();
      container.innerHTML = "";
    }
  };
}

export default function Explanation({ options }) {
  const classes = useStyles();

  const left = useRef(null);
  const right = useRef(null);

  const { modelName, explanationName } = useParams();

  useEffect(() => {
    const visualiser = options.visualiser.left;
    if (!visualiser || !left.current) return;
    return loadVisualiser(modelName, explanationName, visualiser, left.current);
  }, [
    modelName,
    explanationName,
    left,
    options.visualiser.left,
    options.layout,
  ]);

  useEffect(() => {
    const visualiser = options.visualiser.right;
    if (!visualiser || !right.current) return;
    return loadVisualiser(
      modelName,
      explanationName,
      visualiser,
      right.current
    );
  }, [
    modelName,
    explanationName,
    right,
    options.visualiser.right,
    options.layout,
  ]);

  return (
    <div className={classes.root}>
      {options.layout === "single" ? (
        <div ref={left} style={{ height: "100%", display: "flex" }} />
      ) : (
        <SplitView left={left} right={right} />
      )}
    </div>
  );
}
