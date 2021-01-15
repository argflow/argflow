import React from "react";
import ReactDOMServer from "react-dom/server";

/**
 * Get color from strength of words.
 */
function getColor(strength: number) {
  if (strength > 0) {
    return `rgba(0, 255, 0, ${strength})`;
  } else if (strength < 0) {
    return `rgba(255, 0, 0, ${Math.abs(strength)})`;
  } else {
    return "white";
  }
}

/**
 * Split array of words into equal width lines.
 */
function splitLines(arr: any, maxWidth: number) {
  let array = [...arr];

  let lines = [];
  let currentLine = [];
  let currentWidth = 0;

  for (let i = 0; i < array.length; i++) {
    let word = array[i];
    let width = word[0].length;

    if (currentWidth + width < maxWidth) {
      currentLine.push(word);
      currentWidth += width;
    } else {
      lines.push(currentLine);
      currentLine = [word];
      currentWidth = width;
    }
  }

  if (currentLine.length > 0) {
    lines.push(currentLine);
  }

  return lines;
}

/**
 * Convert a payload into an image with given aspect ratio (width / height)
 */
export function payloadToImg(payload: any, type: any, aspectRatio = 5) {
  if (type === "wdcloud") {
    let res = 1000;
    let width = Math.sqrt(res ** 2 * aspectRatio);
    let height = Math.sqrt(res ** 2 / aspectRatio);

    let letters = (payload as any[])
      .map((e) => e[0].length + 1)
      .reduce((a, b) => a + b);

    let fontSize = res / Math.sqrt(letters);

    let svg = ReactDOMServer.renderToStaticMarkup(
      <svg xmlns="http://www.w3.org/2000/svg" width={width} height={height}>
        <rect
          x="0"
          y="0"
          width={width}
          height={height}
          fill="white"
          stroke="black"
          strokeWidth="5"
        />
        <foreignObject width={width} height={height}>
          <body
            // @ts-ignore
            xmlns="http://www.w3.org/1999/xhtml"
            style={{
              width: "100%",
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <div>
              {splitLines(payload, Math.sqrt(aspectRatio * letters) * 1.5).map(
                (line, index) => (
                  <div
                    key={index}
                    style={{
                      display: "flex",
                      justifyContent: "center",
                      marginBottom: fontSize / 6,
                    }}
                  >
                    {line.map((word, index) => (
                      <div
                        key={index}
                        style={{
                          backgroundColor: getColor(word[1]),
                          fontSize: fontSize,
                          fontFamily: "sans-serif",
                          marginRight: fontSize / 3,
                        }}
                      >
                        {word[0]}
                      </div>
                    ))}
                  </div>
                )
              )}
            </div>
          </body>
        </foreignObject>
      </svg>
    );

    return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
  } else {
    return "/api/resources/" + payload;
  }
}
