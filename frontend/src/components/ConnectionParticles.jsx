/**
 * Written by Clayton Durepos
 */

import { useEffect, useMemo, useState, memo } from 'react';
import Particles, { initParticlesEngine } from '@tsparticles/react';
import { loadSlim } from '@tsparticles/slim';

/**
 * Shared particle background that visualizes faculty connections.
 * Memoized to prevent re-renders when parent component state changes.
 */
const ConnectionParticles = memo(function ConnectionParticles({
  className = '',
  colors = ['#ffffff', '#b5c7ff'],
  linkColor = '#bcd1ff',
  quantity = 60,
}) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let mounted = true;

    initParticlesEngine(async (engine) => {
      await loadSlim(engine);
    }).then(() => mounted && setReady(true));

    return () => {
      mounted = false;
    };
  }, []);

  const particleId = useMemo(
    () => `connectionParticles-${Math.random().toString(36).slice(2, 10)}`,
    []
  );

  const options = useMemo(
    () => ({
      fullScreen: { enable: false },
      background: { color: 'transparent' },
      particles: {
        number: { value: quantity, density: { enable: true, area: 800 } },
        color: { value: colors },
        links: {
          enable: true,
          distance: 160,
          color: linkColor,
          opacity: 0.3,
          width: 1,
        },
        move: {
          enable: true,
          speed: 1.1,
          direction: 'none',
          outModes: { default: 'bounce' },
        },
        opacity: { value: 0.8 },
        size: { value: { min: 1, max: 3 } },
        shape: { type: 'circle' },
      },
      interactivity: {
        events: {
          onHover: { enable: true, mode: 'grab' },
          onClick: { enable: true, mode: 'push' },
        },
        modes: {
          grab: { distance: 200, links: { opacity: 0.5 } },
          push: { quantity: 2 },
        },
      },
    }),
    [colors, linkColor, quantity]
  );

  if (!ready) {
    return null;
  }

  return <Particles id={particleId} className={className} options={options} />;
});

export default ConnectionParticles;


