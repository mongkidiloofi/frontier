<script lang="ts">
  export let finalScore: number | null = 0;
  export let recency: number | null = 0;
  export let reputation: number | null = 0;
  export let popularity: number | null = 0;

  const formatScore = (score: number | null) => ((score ?? 0) * 100);

  const radius = 10;
  const circumference = 2 * Math.PI * radius;
  $: strokeDashoffset = circumference - (formatScore(finalScore) / 100) * circumference;
</script>

<div class="score-display-wrapper" title={`Score: ${formatScore(finalScore).toFixed(0)}%`}>
  <div class="score-ring-container">
    <svg class="score-ring" viewBox="0 0 24 24">
      <circle class="ring-bg" cx="12" cy="12" r={radius} />
      <circle
        class="ring-fg"
        cx="12"
        cy="12"
        r={radius}
        stroke-dasharray={circumference}
        stroke-dashoffset={strokeDashoffset}
      />
    </svg>
    <span class="score-percent">{formatScore(finalScore).toFixed(0)}</span>
  </div>
  <div class="score-bars" title={`Recency: ${formatScore(recency).toFixed(0)}%\nReputation: ${formatScore(reputation).toFixed(0)}%\nPopularity: ${formatScore(popularity).toFixed(0)}%`}>
    <div class="bar recency-bar" style="width: {formatScore(recency)}%"></div>
    <div class="bar reputation-bar" style="width: {formatScore(reputation)}%"></div>
    <div class="bar popularity-bar" style="width: {formatScore(popularity)}%"></div>
  </div>
</div>

<style>
  .score-display-wrapper { display: flex; align-items: center; gap: var(--space-3); }
  .score-ring-container { position: relative; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; }
  .score-ring { width: 100%; height: 100%; transform: rotate(-90deg); }
  .score-ring circle { fill: transparent; stroke-width: 3; }
  .ring-bg { stroke: var(--color-border); }
  .ring-fg { stroke: var(--color-text-primary); transition: stroke-dashoffset 0.3s ease; }
  .score-percent { position: absolute; font-size: 0.6rem; font-weight: 600; color: var(--color-text-secondary); }
  .score-bars { display: flex; flex-direction: column; gap: 3px; width: 30px; }
  .bar { height: 4px; border-radius: var(--border-radius-full); }
  .recency-bar { background-color: #60a5fa; }
  .reputation-bar { background-color: #4ade80; }
  .popularity-bar { background-color: #c084fc; }
</style>