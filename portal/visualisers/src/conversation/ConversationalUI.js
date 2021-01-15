import React, { useEffect, useRef, useState } from "react";

import {
  Card,
  CardActionArea,
  CardMedia,
  CircularProgress,
  Divider,
  Typography,
} from "@material-ui/core";

import { nodeToString } from "../common/explanations";
import {
  Direction,
  ContributionType,
  contributionTypesToAdjective,
  NodeContentType,
} from "../common/types";

const styles = {
  cardpadding: 8,
  cardMarginBottom: 10,
};

async function performInteraction(
  modelName,
  explanationName,
  target,
  direction,
  contributionType
) {
  const res = await fetch(
    `/api/models/${modelName}/explanations/${explanationName}/visualisers/argflow_ui.visualisers.ConversationVisualiser`,
    {
      method: "POST",
      body: JSON.stringify({
        interaction_target: target,
        interaction_direction: direction,
        contribution_type: contributionType,
      }),
    }
  );

  return await res.json();
}

function getNode(data, nodeId) {
  return data.explanation.nodes[nodeId];
}

function generateQuestion(node, nodeId, direction, contributionType) {
  const nodeString = nodeToString(node, nodeId);
  const adjective = contributionTypesToAdjective.get(contributionType);
  let question = {
    target: nodeId,
    direction: direction,
    contributionType: contributionType,
    targetString: nodeString,
  };

  if (
    node.content_type === NodeContentType.IMAGE ||
    node.content_type === NodeContentType.WDCLOUD
  ) {
    if (typeof node.payload === "string" || node.payload instanceof String) {
      question.image = node.payload;
    } else {
      question.image = node.payload.feature.payload;
    }
  }

  if (direction === Direction.FROM) {
    question.text = `To what nodes does the node ${nodeString} ${adjective} contribute to?`;
  } else {
    question.text = `What factors ${adjective} contribute to the node ${nodeString}?`;
  }

  return question;
}

// Generates a list of questions for data
function generateQuestions(data) {
  const possibleInteractions = data.interactions;

  let questions = [];
  for (const interaction of possibleInteractions) {
    const node = getNode(data, interaction.node);

    // TODO: More contribution types here
    const contributionTypes = [
      ContributionType.SUPPORT,
      ContributionType.ATTACK,
    ];
    for (const contributionType of contributionTypes) {
      questions.push(
        generateQuestion(
          node,
          interaction.node,
          interaction.direction,
          contributionType
        )
      );
    }
  }

  return questions;
}

function generateAnswer(question, data) {
  const interactionResults = data.interaction_result;
  const endpoints = interactionResults.map((r) => ({
    id: r.endpoint,
    node: getNode(data, r.endpoint),
  }));

  let answer = { nodes: endpoints.map((n) => n.id) };

  const adjective = contributionTypesToAdjective.get(question.contributionType);
  if (endpoints.length === 0) {
    if (question.direction === Direction.FROM) {
      answer.text =
        `The node ${question.targetString} does not ${adjective} contribute ` +
        `to any nodes.`;
    } else {
      answer.text =
        `There are no nodes that contribute ${adjective} to ` +
        `the node ${question.targetString}.`;
    }
    return answer;
  }

  const plural = endpoints.length > 1;
  const endpointStrings = endpoints.map((n) => nodeToString(n.node, n.id));
  if (
    endpoints.every(
      (e) =>
        e.node.content_type === NodeContentType.IMAGE ||
        e.node.content_type === NodeContentType.WDCLOUD
    )
  ) {
    if (question.direction === Direction.FROM) {
      answer.text =
        `The node ${question.targetString} contributes ${adjective} to the ` +
        `following node${plural ? "s" : ""}:`;
    } else {
      answer.text =
        `The above node${plural ? "s" : ""} ` +
        `contribute${!plural ? "s" : ""} ${adjective} to ` +
        `the node ${question.targetString}.`;
    }

    answer.images = endpoints.map((e) =>
      typeof e.node.payload === "string" || e.node.payload instanceof String
        ? e.node.payload
        : e.node.payload.feature.payload
    );
    return answer;
  }

  if (question.direction === Direction.FROM) {
    answer.text =
      `The node ${question.targetString} contributes ${adjective} to the ` +
      `node${plural ? "s" : ""} ${endpointStrings.join(", ")}.`;
  } else {
    answer.text =
      `The node${plural ? "s" : ""} ${endpointStrings.join(", ")} ` +
      `contribute${!plural ? "s" : ""} ${adjective} to the ` +
      `node ${question.targetString}.`;
  }

  return answer;
}

function Chatdiv({ type, value }) {
  const isAnswer = type === "answer";
  return (
    <div
      style={{
        display: "flex",
        justifyContent: isAnswer ? "flex-start" : "flex-end",
      }}
    >
      <Card
        style={{
          maxWidth: "calc(100% - 30px)",
          marginBottom: styles.cardMarginBottom,
          padding: styles.cardpadding,
          backgroundColor: isAnswer ? "#3fc380" : "#22a7f0",
        }}
      >
        <div>
          {/* In case of answer */}
          {value.images &&
            value.images.map((img, i) => (
              <img
                key={i}
                src={"/api/resources/" + img}
                alt=""
                style={{
                  width: "100%",
                  maxWidth: 350,
                  marginRight: 5,
                }}
              />
            ))}

          {/* In case of question */}
          {value.image && (
            <img
              src={"/api/resources/" + value.image}
              alt=""
              style={{
                width: "100%",
                maxWidth: 350,
              }}
            />
          )}

          {/* General case */}
          {value.text && <Typography variant="body2">{value.text}</Typography>}
        </div>
      </Card>
    </div>
  );
}

function NewQuestion({ question, onClick }) {
  return (
    <Card
      style={{
        marginBottom: styles.cardMarginBottom,
      }}
    >
      <div style={{ display: "flex" }}>
        {question.image && (
          <CardMedia
            image={"/api/resources/" + question.image}
            style={{ width: 100, height: 100 }}
          />
        )}
        <CardActionArea onClick={() => onClick(question.text)}>
          <div style={{ padding: 8, display: "flex", alignItems: "center" }}>
            {question.text && (
              <Typography variant="body2">{question.text}</Typography>
            )}
          </div>
        </CardActionArea>
      </div>
    </Card>
  );
}

export default function ConversationalUI({ modelName, explanationName }) {
  // Stores the last received data from api
  const [data, setData] = useState(null);

  // Stores the question-answer history
  const [history, setHistory] = useState([]);
  const historyContainer = useRef(null);

  // Stores a list of all possible questions that can be asked currently
  const [questions, setQuestions] = useState([]);
  const [questionsLoading, setQuestionsLoading] = useState(true);

  // Load data from api on first page load
  useEffect(() => {
    fetch(
      `/api/models/${modelName}/explanations/${explanationName}/visualisers/argflow_ui.visualisers.ConversationVisualiser`,
      {
        method: "POST",
        body: JSON.stringify({}),
      }
    )
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        let explanation = data.explanation;
        let nodes = explanation.nodes;

        let input_id = explanation.input[0];
        let conclusion_id = explanation.conclusion[0];

        let input_content =
          explanation.input.length > 1 ? "input" : nodes[input_id].content_type;
        let conclusion_node = nodes[conclusion_id];

        setHistory([
          {
            type: "answer",
            value: {
              text:
                `The system predicted the ${input_content} as being '${conclusion_node.payload}'` +
                ` with ${conclusion_node.certainty}% confidence.`,
            },
          },
        ]);
      });
  }, [modelName, explanationName]);

  // Update list of questions upon change of explanations data
  useEffect(() => {
    if (data) {
      setQuestions(generateQuestions(data));
      setQuestionsLoading(false);
    }
  }, [modelName, explanationName, data]);

  useEffect(() => {
    if (historyContainer) {
      // Scroll to the bottom of the history whenever something is added to it.
      // FIXME: This is a horrible hack to make this work by scrolling after
      // a fixed delay once the UI has actually been updated, so that there is
      // actually something to scroll down to. There is almost certainly a better
      // way to do this.
      window.setTimeout(() => {
        historyContainer.current.scrollTo({
          left: 0,
          top: historyContainer.current.scrollHeight,
          behavior: "smooth",
        });
      }, 500);
    }
  }, [history, historyContainer]);

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <div
        ref={historyContainer}
        style={{ padding: 16, flex: 2, overflowY: "auto" }}
      >
        {/* Already asked questions */}
        {history.map((item, i) => (
          <Chatdiv key={i} type={item.type} value={item.value} />
        ))}
      </div>

      <Divider />

      {/* New Questions */}
      <div style={{ padding: 16, flex: 1, overflowY: "auto" }}>
        {questionsLoading ? (
          <div
            style={{
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <CircularProgress />
          </div>
        ) : (
          <>
            {history.length < questions.length && (
              <Typography style={{ marginBottom: 8 }}>
                Suggested questions:
              </Typography>
            )}

            {questions.length !== 0 &&
              questions.map((q, i) => (
                <NewQuestion
                  key={i}
                  question={q}
                  onClick={() => {
                    setQuestionsLoading(true);
                    performInteraction(
                      modelName,
                      explanationName,
                      q.target,
                      q.direction,
                      q.contributionType
                    ).then((newData) => {
                      let answer = generateAnswer(q, newData);
                      setHistory([
                        ...history,
                        { type: "question", value: q },
                        { type: "answer", value: answer },
                      ]);
                      setQuestions(generateQuestions(newData));
                      setQuestionsLoading(false);
                    });
                  }}
                />
              ))}
          </>
        )}
      </div>
    </div>
  );
}
