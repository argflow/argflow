import React from "react";
import ReactDOM from "react-dom";

import { createGenerateClassName, StylesProvider } from "@material-ui/core";

import ConversationalUI from "./ConversationalUI";

export default class ConversationVisualiser {
  constructor(modelName, explanationName, container) {
    // We have to create a new div to render into because it seems
    // that React doesn't like rendering into the same container multiple times,
    // so if the visualiser is unloaded and reloaded into the same container
    // it won't re-render.
    this.root = container.appendChild(document.createElement("div"));

    this.root.style.flex = "1";
    this.root.style.overflow = "auto";

    const generateClassName = createGenerateClassName({
      disableGlobal: true,
      productionPrefix: "aui-conv-",
    });

    ReactDOM.render(
      <StylesProvider generateClassName={generateClassName}>
        <ConversationalUI
          modelName={modelName}
          explanationName={explanationName}
        />
      </StylesProvider>,
      this.root
    );
  }

  destroy() {
    ReactDOM.unmountComponentAtNode(this.root);
  }
}
