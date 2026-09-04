const frozenRussianPattern = String.raw`@"(?i)не\s+найден|ничего|нет\s+(результат|совпад|запис)|совпадени.*нет"`;
const correctedRussianPattern = String.raw`@"(?i)не\s+найден|ничего|нет.{0,32}(результат|совпад|запис)|(результат|совпад|запис|подходящ).{0,32}(не\s+найден|нет)|совпадени.*нет"`;
const frozenEnglishPattern = String.raw`@"(?i)no\s+(results|matches|recordings)|nothing\s+(found|matches)|not\s+found|zero\s+results"`;
const correctedEnglishPattern = String.raw`@"(?i)no.{0,32}(results|matches|recordings)|(results|matches|recordings).{0,32}(not\s+found|none)|nothing\s+(found|matches)|not\s+found|zero\s+results"`;

export const frozenRussianNoResultsPattern = String.raw`(?i)не\s+найден|ничего|нет\s+(результат|совпад|запис)|совпадени.*нет`;
export const correctedRussianNoResultsPattern = String.raw`(?i)не\s+найден|ничего|нет.{0,32}(результат|совпад|запис)|(результат|совпад|запис|подходящ).{0,32}(не\s+найден|нет)|совпадени.*нет`;
export const frozenEnglishNoResultsPattern = String.raw`(?i)no\s+(results|matches|recordings)|nothing\s+(found|matches)|not\s+found|zero\s+results`;
export const correctedEnglishNoResultsPattern = String.raw`(?i)no.{0,32}(results|matches|recordings)|(results|matches|recordings).{0,32}(not\s+found|none)|nothing\s+(found|matches)|not\s+found|zero\s+results`;

export function applyLargeSearchCorrection(source) {
  const russianOccurrences = source.split(frozenRussianPattern).length - 1;
  const englishOccurrences = source.split(frozenEnglishPattern).length - 1;
  if (russianOccurrences !== 2 || englishOccurrences !== 2) {
    throw new Error(`Expected two frozen patterns per language, found ru=${russianOccurrences}, en=${englishOccurrences}.`);
  }
  const corrected = source
    .replaceAll(frozenRussianPattern, correctedRussianPattern)
    .replaceAll(frozenEnglishPattern, correctedEnglishPattern);
  if (
    corrected.includes(frozenRussianPattern)
    || corrected.includes(frozenEnglishPattern)
    || corrected.split(correctedRussianPattern).length - 1 !== 2
    || corrected.split(correctedEnglishPattern).length - 1 !== 2
  ) {
    throw new Error("Corrected no-results overlay was not applied exactly twice per language.");
  }
  return corrected;
}
