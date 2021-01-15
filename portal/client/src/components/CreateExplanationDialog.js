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

export default function CreateExplanationDialog({
  explanations,
  open,
  onCreate,
  onClose,
}) {
  const [chis, setChis] = useState([]);
  const [generators, setGenerators] = useState(["default"]);

  const [input, setInput] = useState("");
  const [explanationName, setExplanationName] = useState("");
  const [chi, setChi] = useState(chis[0] ?? null);
  const [generator, setGenerator] = useState("default");

  const explanationNames = explanations.map((e) => e["name"]);

  useEffect(() => {
    if (open) {
      fetch("/api/chis")
        .then((res) => res.json())
        .then((json) => {
          setChis(json);
          setChi(json[0] ?? null);
        });

      fetch("/api/generators")
        .then((res) => res.json())
        .then((json) => {
          setGenerators(json);
          setGenerator(json[0]);
        });
    } else {
      setInput("");
    }
  }, [open]);

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>Create explanation</DialogTitle>
      <DialogContent>
        <div>
          <div style={{ marginBottom: 16 }}>
            <Typography variant="h6">Explanation name</Typography>
            <TextField
              label="Explanation name"
              multiline
              fullWidth
              value={explanationName}
              onChange={(e) => setExplanationName(e.target.value)}
            />
            {explanationNames.includes(explanationName) && (
              <Typography style={{ color: "red" }}>
                Explanation with this name already exists, please choose a
                different name.
              </Typography>
            )}
          </div>
          <div style={{ marginBottom: 16 }}>
            <Typography variant="h6">Input</Typography>
            <TextField
              label="Input"
              multiline
              fullWidth
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
          </div>
          <div style={{ marginBottom: 16 }}>
            <Typography variant="h6">Chi</Typography>
            <Select
              disabled={chis.length === 0}
              fullWidth
              value={chi?.value ?? ""}
              onChange={(e) =>
                setChi(chis.find((chi) => chi.value === e.target.value))
              }
            >
              {chis.map(({ name, value }) => (
                <MenuItem key={value} value={value}>
                  {name}
                </MenuItem>
              ))}
            </Select>
          </div>
          <div>
            <Typography variant="h6">Generator</Typography>
            <Select
              disabled={chis.length === 0}
              fullWidth
              value={generator}
              onChange={(e) => setGenerator(e.target.value)}
            >
              {generators.map((g) => (
                <MenuItem key={g} value={g}>
                  {g}
                </MenuItem>
              ))}
            </Select>
          </div>
        </div>
      </DialogContent>
      <DialogActions>
        <Button
          disabled={
            !explanationName || explanationNames.includes(explanationName)
          }
          onClick={() =>
            onCreate(explanationName, input, chi?.value, generator)
          }
        >
          Create explanation
        </Button>
      </DialogActions>
    </Dialog>
  );
}
