import React, { useEffect, useState } from "react";
import DescriptionIcon from "@material-ui/icons/Description";
import FolderIcon from "@material-ui/icons/Folder";
import {
  Box,
  Button,
  Card,
  CardActionArea,
  CircularProgress,
  Icon,
  Typography,
} from "@material-ui/core";

async function getFiles(path) {
  const url = path
    ? `/api/files?path=${encodeURIComponent(path)}`
    : "/api/files";
  const res = await fetch(url);
  return await res.json();
}

function File({ name, isFolder, onClick }) {
  return (
    <Card
      style={{
        marginBottom: 5,
        backgroundColor: isFolder ? "#eeeeee" : "white",
      }}
      elevation={0}
      onClick={onClick ? onClick : undefined}
    >
      <CardActionArea>
        <Box display="flex" alignItems="center" padding="2px">
          <Icon style={{ marginRight: 8, marginLeft: 8 }}>
            {isFolder ? <FolderIcon /> : <DescriptionIcon />}
          </Icon>
          <Typography noWrap>{name}</Typography>
        </Box>
      </CardActionArea>
    </Card>
  );
}

export default function FileBrowser({ onSelectFile }) {
  const [path, setPath] = useState("");
  const [curFiles, setCurFiles] = useState(null);
  const [loading, setLoading] = useState(false);

  function updatePath(path) {
    setPath(path);
    setLoading(true);

    getFiles(path).then((data) => {
      setPath(data.path);
      setCurFiles(data);
      setLoading(false);
    });
  }

  function goUp() {
    updatePath(path.substring(0, path.lastIndexOf("/")));
  }

  useEffect(() => {
    updatePath();
  }, []);

  return (
    <div>
      <Typography style={{ marginBottom: 10 }}>Path: {path}</Typography>
      <File isFolder name=".." onClick={() => goUp()} />
      {loading ? (
        <CircularProgress />
      ) : (
        curFiles && (
          <Box>
            <Box>
              {curFiles.folders.map((f, i) => (
                <File
                  key={i}
                  name={f.name}
                  isFolder
                  onClick={() => updatePath(f.path)}
                />
              ))}
            </Box>
            <Box>
              {curFiles.files.map((f, i) => (
                <File
                  key={i}
                  name={f.name}
                  onClick={() => onSelectFile(f.path)}
                />
              ))}
            </Box>
            <Box
              display="flex"
              justifyContent="flex-end"
              marginTop="16px"
              marginBottom="16px"
            >
              <Button variant="outlined" onClick={() => onSelectFile(path)}>
                Select Folder
              </Button>
            </Box>
          </Box>
        )
      )}
    </div>
  );
}
