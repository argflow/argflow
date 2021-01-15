import React, { useState } from "react";
import AddIcon from "@material-ui/icons/Add";
import { Container, Typography, Card, CardActionArea } from "@material-ui/core";

import ItemsList from "../components/ItemsList";
import AddModelDialog from "../components/AddModelDialog";

export default function Home({ models }) {
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  function onAddModel(location, model, name) {
    fetch(`/api/models/${name}`, {
      method: "POST",
      body: JSON.stringify({
        location,
        model,
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
          onClick={() => setShowCreateDialog(true)}
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            paddingTop: 32,
            paddingBottom: 32,
          }}
        >
          <AddIcon style={{ fontSize: 56 }} />
          <Typography variant="h5">Add model</Typography>
        </CardActionArea>
      </Card>
      <Typography variant="h2" gutterBottom>
        Saved models
      </Typography>
      <ItemsList items={models} />
      <AddModelDialog
        open={showCreateDialog}
        models={models}
        onAdd={(location, model, name) => {
          setShowCreateDialog(false);
          onAddModel(location, model, name);
        }}
        onClose={() => setShowCreateDialog(false)}
      />
    </Container>
  );
}
