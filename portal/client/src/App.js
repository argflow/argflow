import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";

import SettingsIcon from "@material-ui/icons/Settings";
import {
  makeStyles,
  AppBar,
  Button,
  Toolbar,
  Typography,
} from "@material-ui/core";

import OptionsMenu from "./components/OptionsMenu";

import Explanation from "./pages/Explanation";
import Model from "./pages/Model";
import NotFound from "./pages/NotFound";
import Home from "./pages/Home";

import WSConnection from "./WSConnection";

const useStyles = makeStyles((theme) => ({
  root: {
    height: "100%",
    display: "flex",
    flexDirection: "column",
  },
  appbar: {
    zIndex: theme.zIndex.drawer + 1,
  },
  content: {
    flex: 1,
    overflow: "auto",
  },
}));

function App() {
  const classes = useStyles();

  const [ws, setWs] = useState(null);
  const [visualisers, setVisualisers] = useState([]);
  const [models, setModels] = useState([]);
  const [showOptions, setShowOptions] = useState(false);
  const [options, setOptions] = useState({
    layout: "single",
    visualiser: {
      left: null,
      right: null,
    },
  });

  useEffect(() => {
    fetch("/api/visualisers")
      .then((res) => res.json())
      .then((visualisers) => {
        setVisualisers(visualisers);
        setOptions((opts) => ({
          ...opts,
          visualiser: {
            left: visualisers[0] || null,
            right: visualisers[1] || null,
          },
        }));
      });
  }, []);

  useEffect(() => {
    async function fetchModels() {
      const res = await fetch(`/api/models`);
      const data = await res.json();
      setModels(data);
    }

    fetchModels();

    const ws = new WebSocket(`ws://${window.location.host}/ws`);
    const conn = new WSConnection(ws);

    conn.addEventListener("reload", () => fetchModels());

    setWs(conn);

    return () => {
      ws.close();
      setWs(null);
    };
  }, []);

  return (
    <div className={classes.root}>
      <AppBar position="static" className={classes.appbar}>
        <Toolbar variant="dense">
          <Typography variant="h6">ArgFlow UI</Typography>
          <div style={{ flex: 1 }} />
          <Button
            color="inherit"
            startIcon={<SettingsIcon />}
            onClick={() => setShowOptions(true)}
          >
            Options
          </Button>
        </Toolbar>
      </AppBar>
      <div className={classes.content}>
        <Router>
          <Switch>
            <Route path="/" exact>
              <Home models={models} />
            </Route>
            <Route path="/models/:modelName/explanations/:explanationName">
              <Explanation options={options} />
            </Route>
            <Route path="/models/:modelName">
              <Model ws={ws} />
            </Route>
            <Route>
              <NotFound />
            </Route>
          </Switch>
        </Router>
      </div>
      <OptionsMenu
        visualisers={visualisers}
        state={options}
        open={showOptions}
        onClose={() => setShowOptions(false)}
        onChange={setOptions}
      />
    </div>
  );
}

export default App;
