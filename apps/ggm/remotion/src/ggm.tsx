import React from 'react';
import '@fontsource/montserrat/600.css';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/800.css';
import '@fontsource/montserrat/900.css';
import '@fontsource/dm-sans/400.css';
import '@fontsource/dm-sans/500.css';
import '@fontsource/dm-sans/700.css';
import {AbsoluteFill, Img, staticFile, spring, useCurrentFrame, useVideoConfig, interpolate} from 'remotion';

export const G = {
  blue: '#1A5FE8',
  purple: '#914EFD',
  navy: '#0E1629',
  gray: '#5B6475',
  line: '#E5E8EF',
  bg: '#FFFFFF',
  soft: '#F5F7FB',
};
export const HEAD = 'Montserrat, sans-serif';
export const BODY = '"DM Sans", Inter, sans-serif';
export const CAP = 'Montserrat, sans-serif';

export const Logo: React.FC<{height?: number}> = ({height = 64}) => (
  <div style={{background: '#000', borderRadius: height * 0.35, padding: `${height * 0.18}px ${height * 0.4}px`, display: 'inline-flex'}}>
    <Img src={staticFile('logo.png')} style={{height}} />
  </div>
);

// TikTok-style caption: chunks of text with frame timing.
export type Cap = {from: number; to: number; text: string};
export const Captions: React.FC<{caps: Cap[]; top?: number}> = ({caps, top = 260}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const c = caps.find((x) => frame >= x.from && frame < x.to);
  if (!c) return null;
  const s = spring({frame: frame - c.from, fps, config: {damping: 12, stiffness: 220}});
  const stroke = '#000';
  const sh = [] as string[];
  for (let a = 0; a < 16; a++) {
    const r = 6;
    sh.push(`${(Math.cos((a / 16) * Math.PI * 2) * r).toFixed(1)}px ${(Math.sin((a / 16) * Math.PI * 2) * r).toFixed(1)}px 0 ${stroke}`);
  }
  return (
    <div style={{position: 'absolute', top, left: 70, right: 70, textAlign: 'center', transform: `scale(${0.85 + 0.15 * s})`}}>
      <span style={{fontFamily: CAP, fontWeight: 800, fontSize: 68, lineHeight: 1.22, color: '#fff', textShadow: sh.join(',')}}>{c.text}</span>
    </div>
  );
};

export const useShake = (amp = 1) => {
  const f = useCurrentFrame();
  const x = (Math.sin(f / 7.3) * 4 + Math.sin(f / 2.9) * 1.6 + Math.sin(f / 17) * 6) * amp;
  const y = (Math.cos(f / 6.1) * 4 + Math.sin(f / 3.7) * 1.4 + Math.cos(f / 19) * 5) * amp;
  const r = (Math.sin(f / 23) * 0.6 + Math.sin(f / 5.3) * 0.15) * amp;
  return `translate(${x}px, ${y}px) rotate(${r}deg)`;
};

// Fake phone-camera room behind the laptop.
export const Room: React.FC = () => (
  <AbsoluteFill style={{background: 'linear-gradient(180deg, #3a3530 0%, #2a2622 45%, #6b5640 62%, #8a6c4c 100%)'}}>
    {[[160, 300, 220, '#ffd9a055'], [900, 420, 260, '#fff1d433'], [520, 160, 180, '#ffe3b244'], [980, 120, 120, '#ffffff22']].map(([x, y, r, c], i) => (
      <div key={i} style={{position: 'absolute', left: (x as number) - (r as number), top: (y as number) - (r as number), width: (r as number) * 2, height: (r as number) * 2, borderRadius: '50%', background: `radial-gradient(circle, ${c} 0%, transparent 70%)`, filter: 'blur(10px)'}} />
    ))}
    <div style={{position: 'absolute', left: 0, right: 0, top: 1150, bottom: 0, background: 'repeating-linear-gradient(92deg, #8b6b4a 0px, #946f4b 18px, #7f6143 40px, #8f6d4b 70px)', opacity: 0.55, filter: 'blur(2px)'}} />
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 55%, transparent 40%, #000000aa 100%)'}} />
  </AbsoluteFill>
);

// Laptop with screen content, slight perspective.
export const Laptop: React.FC<{children: React.ReactNode; width?: number}> = ({children, width = 1000}) => {
  const sw = width - 40;
  const sh = sw * 0.625;
  return (
    <div style={{width, perspective: 1800}}>
      <div style={{transform: 'rotateX(6deg)', transformOrigin: 'bottom center'}}>
        <div style={{background: '#111', borderRadius: 26, padding: 20, boxShadow: '0 40px 80px #0009'}}>
          <div style={{width: sw, height: sh, background: '#fff', borderRadius: 6, overflow: 'hidden', position: 'relative'}}>
            {children}
            <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(125deg, #ffffff22 0%, transparent 35%, transparent 70%, #ffffff10 100%)', pointerEvents: 'none'}} />
          </div>
        </div>
      </div>
      <div style={{height: 34, margin: '0 -50px', background: 'linear-gradient(180deg, #c9cbd1, #8e9097)', borderRadius: '0 0 30px 30px', transform: 'perspective(800px) rotateX(55deg)', transformOrigin: 'top'}} />
    </div>
  );
};

export const Cursor: React.FC<{x: number; y: number; click?: number}> = ({x, y, click = 0}) => (
  <div style={{position: 'absolute', left: x, top: y, width: 0, height: 0}}>
    {click > 0 && <div style={{position: 'absolute', left: -20, top: -20, width: 40, height: 40, borderRadius: 20, border: `3px solid ${G.blue}`, opacity: 1 - click, transform: `scale(${0.5 + click})`}} />}
    <svg width="26" height="34" viewBox="0 0 26 34" style={{position: 'absolute', left: 0, top: 0}}>
      <path d="M1 1 L1 27 L8 20 L13 32 L18 30 L13 18 L23 18 Z" fill="#000" stroke="#fff" strokeWidth="2" />
    </svg>
  </div>
);

export const ease = (f: number, a: number, b: number, v0: number, v1: number) =>
  interpolate(f, [a, b], [v0, v1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: (t) => t * t * (3 - 2 * t)});
