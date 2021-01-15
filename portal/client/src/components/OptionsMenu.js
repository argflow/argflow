import React, { useCallback } from "react";

import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  MenuItem,
  TextField,
} from "@material-ui/core";

export default function OptionsMenu({
  open,
  state,
  visualisers,
  onClose,
  onChange,
}) {
  const { layout, visualiser } = state || {};

  const onVisualiserChange = useCallback(
    (e, pane) => {
      onChange &&
        onChange({
          ...state,
          visualiser: {
            ...state.visualiser,
            [pane]: visualisers.find((v) => v.id === e.target.value),
          },
        });
    },
    [visualisers, state, onChange]
  );

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Options</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Control the appearance and layout of the visualiser screen.
        </DialogContentText>
        <TextField
          select
          fullWidth
          label="Layout"
          value={layout || "single"}
          style={{ marginTop: 8, marginBottom: 8 }}
          onChange={(e) =>
            onChange && onChange({ ...state, layout: e.target.value })
          }
        >
          <MenuItem value="single">Single</MenuItem>
          <MenuItem value="split">Split</MenuItem>
        </TextField>
        {layout === "single" ? (
          <TextField
            select
            fullWidth
            label="Visualiser"
            value={visualiser.left ? visualiser.left.id : ""}
            onChange={(e) => onVisualiserChange(e, "left")}
            style={{ flex: 1, marginTop: 8, marginBottom: 8 }}
          >
            {visualisers.map((v) => (
              <MenuItem key={v.id} value={v.id}>
                {v.name}
              </MenuItem>
            ))}
          </TextField>
        ) : (
          <div style={{ display: "flex", paddingTop: 8, paddingBottom: 8 }}>
            <TextField
              select
              label="Left"
              value={visualiser.left ? visualiser.left.id : ""}
              onChange={(e) => onVisualiserChange(e, "left")}
              style={{ flex: 1 }}
            >
              {visualisers.map((v) => (
                <MenuItem key={v.id} value={v.id}>
                  {v.name}
                </MenuItem>
              ))}
            </TextField>
            <div style={{ width: 16 }} />
            <TextField
              select
              label="Right"
              value={visualiser.right ? visualiser.right.id : ""}
              onChange={(e) => onVisualiserChange(e, "right")}
              style={{ flex: 1 }}
            >
              {visualisers.map((v) => (
                <MenuItem key={v.id} value={v.id}>
                  {v.name}
                </MenuItem>
              ))}
            </TextField>
          </div>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}
