export function formatScore(score: number): string {
  return score.toFixed(2)
}

export function scorePercent(score: number): number {
  return Math.round(score * 100)
}

export function scoreTone(
  score: number
): "above" | "below" | "average" {
  if (Math.abs(score - 0.5) < 0.001) {
    return "average"
  }

  return score > 0.5 ? "above" : "below"
}
