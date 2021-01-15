import React, { useEffect, useState } from "react";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Select,
  TextField,
  Typography,
} from "@material-ui/core";

import FileBrowser from "./FileBrowser";
import HubBrowser from "./HubBrowser";

export default function AddModelDialog({ open, models, onAdd, onClose }) {
  const [hubEnabled, setHubEnabled] = useState(false);
  const [location, setLocation] = useState("fs");
  const [model, setModel] = useState(null);
  const [modelName, setModelName] = useState("");
  const modelNames = models.map((m) => m["name"]);

  useEffect(() => {
    if (open) {
      fetch("/api/hub/enabled")
        .then((res) => res.json())
        .then((json) => setHubEnabled(json));
    } else {
      setModel(null);
      setModelName("");
    }
  }, [open]);

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>Add model</DialogTitle>
      <DialogContent>
        <div style={{ marginBottom: 16 }}>
          <Typography variant="h6">From</Typography>
          <Select
            fullWidth
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          >
            <MenuItem value={"fs"}>Filesystem</MenuItem>
            {hubEnabled && <MenuItem value={"hub"}>Model Hub</MenuItem>}
          </Select>
        </div>
        {model === null ? (
          location === "fs" ? (
            <div>
              <Typography variant="h6">Select a Model</Typography>
              <FileBrowser onSelectFile={(path) => setModel(path)} />
            </div>
          ) : (
            <div>
              <Typography variant="h6">Find a Model</Typography>
              <HubBrowser onSelectModel={(slug) => setModel(slug)} />
            </div>
          )
        ) : (
          <div>
            <div style={{ display: "flex" }}>
              <Typography variant="h6" style={{ flex: 1 }}>
                Selected Model
              </Typography>
              <Button
                variant="outlined"
                color="primary"
                size="small"
                onClick={() => setModel(null)}
              >
                Change
              </Button>
            </div>
            <Typography>{model}</Typography>
            <br />
            <Typography variant="h6">Model name</Typography>
            <TextField
              label="Model name"
              multiline
              fullWidth
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
            />
            {modelNames.includes(modelName) && (
              <Typography style={{ color: "red" }}>
                Model with this name already exists, please choose a different
                name.
              </Typography>
            )}
          </div>
        )}
      </DialogContent>
      <DialogActions>
        {model && (
          <Button
            disabled={!modelName || modelNames.includes(modelName)}
            onClick={() => onAdd(location, model, modelName)}
          >
            Add model
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}
