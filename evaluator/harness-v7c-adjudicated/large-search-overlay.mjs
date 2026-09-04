const frozenEnglishPattern = String.raw`@"(?i)no results|nothing found|not found"`;
const correctedEnglishPattern = String.raw`@"(?i)no(?:\s+matching)?\s+(?:results|recordings)|nothing found|not found"`;

export function applyV7cLargeSearchCorrection(source) {
  const occurrences = source.split(frozenEnglishPattern).length - 1;
  if (occurrences !== 1) {
    throw new Error(`Expected one frozen V7 English no-results pattern, found ${occurrences}.`);
  }
  const corrected = source.replace(frozenEnglishPattern, correctedEnglishPattern);
  if (corrected.includes(frozenEnglishPattern)) {
    throw new Error("The frozen English no-results pattern remained after correction.");
  }
  return corrected;
}

