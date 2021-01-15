import React from "react";
import ReactDOM from "react-dom";

import { blue } from "@material-ui/core/colors";
import {
  createGenerateClassName,
  createMuiTheme,
  StylesProvider,
  ThemeProvider,
} from "@material-ui/core";

import App from "./App";

export default class GraphVisualiser {
  constructor(
    modelName: string,
    explanationName: string,
    private readonly container: HTMLDivElement
  ) {
    // This stops the material-ui styles conflicting with the main app
    const generateClassName = createGenerateClassName({
      disableGlobal: true,
      productionPrefix: "aui-graph-",
    });

    const theme = createMuiTheme({
      palette: {
        primary: blue,
      },
    });

    ReactDOM.render(
      <StylesProvider generateClassName={generateClassName}>
        <ThemeProvider theme={theme}>
          <App modelName={modelName} explanationName={explanationName} />
        </ThemeProvider>
      </StylesProvider>,
      container
    );
  }

  destroy() {
    ReactDOM.unmountComponentAtNode(this.container);
  }
}
