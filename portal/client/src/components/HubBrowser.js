import React, { useEffect, useState } from "react";
import {
  Button,
  Fade,
  LinearProgress,
  TextField,
  Typography,
} from "@material-ui/core";

export default function HubBrowser({ onSelectModel }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch("/api/hub/models/search?query=" + encodeURIComponent(query))
      .then((res) => res.json())
      .then((json) => {
        setResults(json);
        setLoading(false);
      });
  }, [query]);

  return (
    <div>
      <Fade in={loading} unmountOnExit>
        <LinearProgress />
      </Fade>
      <TextField
        fullWidth
        placeholder="Search"
        value={query || ""}
        onChange={(e) => setQuery(e.target.value)}
        style={{ marginBottom: 16 }}
      />
      <div style={{ padding: "0px 16px" }}>
        {results.map((f) => (
          <div key={f.slug} style={{ display: "flex" }}>
            <div style={{ flex: 1, display: "flex", alignItems: "center" }}>
              <Typography style={{ fontWeight: "500" }} noWrap>
                {f.name}
              </Typography>
            </div>
            <Button onClick={() => onSelectModel(f.slug)}>Select</Button>
          </div>
        ))}
      </div>
    </div>
  );
}
