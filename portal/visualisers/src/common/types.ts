export enum ContributionType {
  SUPPORT = "support",
  ATTACK = "attack",
  NEUTRAL = "neutral",
  INDIRECT = "indirect",
}

export enum NodeType {
  REGULAR = "regular",
  CONCLUSION = "conclusion",
  INPUT = "input",
  NONE = "none",
}

export enum NodeContentType {
  IMAGE = "image",
  STRING = "string",
  WDCLOUD = "wdcloud",
}

export enum Direction {
  FROM = "from",
  TO = "to",
}

export const contributionTypesToAdjective: Map<
  ContributionType,
  string
> = new Map([
  [ContributionType.SUPPORT, "positively"],
  [ContributionType.ATTACK, "negatively"],
]);
