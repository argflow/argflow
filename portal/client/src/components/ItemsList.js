import React from "react";
import { Link } from "react-router-dom";
import { makeStyles } from "@material-ui/core/styles";
import { blue, deepOrange, deepPurple, green } from "@material-ui/core/colors";
import {
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
} from "@material-ui/core";
import DeleteIcon from "@material-ui/icons/Delete";
import { toHumanReadableInformationUnits } from "../util/dirs.js";

const COLORS = [deepOrange, deepPurple, blue, green];

const useStyles = makeStyles((theme) => ({
  root: {
    width: "100%",
    backgroundColor: theme.palette.background.paper,
  },
  avatar: {
    width: 70,
    height: 70,
    marginRight: 15,
  },
  largerText: {
    fontSize: "1.3em",
  },
}));

function ListItemLink(props) {
  return <ListItem button component={Link} {...props} />;
}

function hash(s) {
  return Math.abs(
    s.split("").reduce((a, b) => {
      a = (a << 5) - a + b.charCodeAt(0);
      return a & a;
    }, 0)
  );
}

function getAvatarStyle(name) {
  const color = COLORS[hash(name) % COLORS.length];
  return {
    background: color[500],
  };
}

function deleteItem(url) {
  fetch(`/api${url}`, {
    method: "DELETE",
  });
}

export default function ItemsList({ items }) {
  const classes = useStyles();

  if (!items) {
    return <></>;
  }

  return (
    <div className={classes.root}>
      <List>
        {items.map((i) => (
          <ListItemLink key={i.name} to={i.url}>
            <ListItemAvatar>
              <Avatar style={getAvatarStyle(i.name)}>
                {i.name[0].toUpperCase()}
              </Avatar>
            </ListItemAvatar>
            <ListItemText
              primary={i.name}
              secondary={
                i.path + ` (${toHumanReadableInformationUnits(i.size)})`
              }
            />
            <ListItemSecondaryAction onClick={() => deleteItem(i.url)}>
              <IconButton edge="end" aria-label="delete">
                <DeleteIcon />
              </IconButton>
            </ListItemSecondaryAction>
          </ListItemLink>
        ))}
      </List>
    </div>
  );
}
