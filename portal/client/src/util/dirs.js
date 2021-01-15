/**
 * Converts value in bytes to string with appropriate units
 * @param {number} bytes - The converted quantity of bytes
 * @returns {string} - The human-readable value with units
 */
export function toHumanReadableInformationUnits(bytes) {
  const units = ["B", "kB", "MB", "GB", "TB"];
  let currentUnit;
  let currentBytesPerUnit = 1;

  // Test which unit fits best
  for (let unit of units) {
    currentUnit = unit;
    const newBytesPerUnit = currentBytesPerUnit * 1000;
    if (bytes < newBytesPerUnit) {
      // Using bigger unit would result in result less then 1, break
      break;
    }
    currentBytesPerUnit = newBytesPerUnit;
  }

  let result = bytes / currentBytesPerUnit;

  // Only take two decimal places
  result = +result.toFixed(2);

  // Separate value and units by a non-breaking space
  return `${result}\u00a0${currentUnit}`;
}
