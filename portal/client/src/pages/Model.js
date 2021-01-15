import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import AddIcon from "@material-ui/icons/Add";
import {
  Card,
  CardActionArea,
  CircularProgress,
  Container,
  Typography,
} from "@material-ui/core";
import { useHistory } from "react-router";

import ItemsList from "../components/ItemsList";
import CreateExplanationDialog from "../components/CreateExplanationDialog";

export default function Model({ ws }) {
  const history = useHistory();

  const [isGenerating, setGenerating] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [explanations, setExplanations] = useState([]);

  const { modelName } = useParams();

  useEffect(() => {
    async function fetchExplanations() {
      const res = await fetch(`/api/models/${modelName}/explanations`);
      const data = await res.json();
      setExplanations(data);
    }

    fetchExplanations();
    if (ws) {
      function onExGenStart(e) {
        setGenerating(true);
      }

      function onExGenSuccess(e) {
        setGenerating(false);
        history.push(`/models/${modelName}/explanations/${e.name}`);
      }

      ws.addEventListener("exgen-start", onExGenStart);
      ws.addEventListener("exgen-success", onExGenSuccess);

      return () => {
        ws.removeEventListener("exgen-start", onExGenStart);
        ws.removeEventListener("exgen-success", onExGenSuccess);
      };
    }
  }, [ws, modelName, history]);

  function onCreateExplanation(explanationName, input, chi, generator) {
    fetch(`/api/models/${modelName}/explanations/${explanationName}`, {
      method: "POST",
      body: JSON.stringify({
        input,
        chi,
        generator,
      }),
    });
  }

  return (
    <Container style={{ marginTop: 32 }}>
      <Card
        variant="outlined"
        style={{
          border: "1px solid black",
          marginBottom: 32,
        }}
      >
        <CardActionArea
          onClick={() => isGenerating || setShowCreateDialog(true)}
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            paddingTop: 32,
            paddingBottom: 32,
          }}
        >
          {isGenerating ? (
            <>
              <CircularProgress />
              <br />
              <Typography variant="subtitle2">
                Generating explanation...
              </Typography>
            </>
          ) : (
            <>
              <AddIcon style={{ fontSize: 56 }} />
              <Typography variant="h5">Create Explanation</Typography>
            </>
          )}
        </CardActionArea>
      </Card>
      <Typography variant="h2" gutterBottom>
        Explanations for {modelName}
      </Typography>
      <ItemsList items={explanations} />
      <CreateExplanationDialog
        open={showCreateDialog}
        explanations={explanations}
        onCreate={(explanationName, input, chi, generator) => {
          setShowCreateDialog(false);
          onCreateExplanation(explanationName, input, chi, generator);
        }}
        onClose={() => setShowCreateDialog(false)}
      />
    </Container>
  );
}
