// File: frontend/src/lib/actions/intersect.ts

/**
 * A Svelte action that triggers a callback when an element intersects the viewport.
 *
 * Usage:
 * <div use:intersect={onIntersect} />
 */
export function intersect(node: HTMLElement, onIntersect: () => void) {
  const observer = new IntersectionObserver(
    (entries) => {
      // The callback is fired when the element is intersecting
      if (entries[0].isIntersecting) {
        onIntersect();
      }
    },
    {
      root: null, // observes intersections relative to the viewport
      rootMargin: '200px', // Pre-load content when the sentinel is 200px away from the viewport
      threshold: 0.1,
    }
  );

  observer.observe(node);

  // Cleanup function when the component is destroyed
  return {
    destroy() {
      observer.unobserve(node);
    },
  };
}