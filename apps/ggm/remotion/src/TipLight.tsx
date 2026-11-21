import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame, interpolate, spring, useVideoConfig} from 'remotion';
import {G, HEAD, BODY, Logo} from './ggm';
export type TipProps = {title: string; steps: {big: string; small: string}[]; outro: string; eyebrow?: string};

const SCENE = 105;
const useIn = (d = 0) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: f - d, fps, config: {damping: 200}});
  return {opacity: s, transform: `translateY(${interpolate(s, [0, 1], [50, 0])}px)`};
};
const Fade: React.FC<{children: React.ReactNode}> = ({children}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{opacity: interpolate(f, [0, 8, SCENE - 8, SCENE], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>{children}</AbsoluteFill>;
};
const grad = `linear-gradient(90deg, ${G.blue}, ${G.purple})`;

const Bg: React.FC = () => (
  <AbsoluteFill style={{background: '#fff'}}>
    <AbsoluteFill style={{backgroundImage: `linear-gradient(${G.line}88 1px, transparent 1px), linear-gradient(90deg, ${G.line}88 1px, transparent 1px)`, backgroundSize: '60px 60px'}} />
    <div style={{position: 'absolute', left: -200, top: 1400, width: 800, height: 800, borderRadius: 400, background: `radial-gradient(circle, ${G.purple}22, transparent 70%)`}} />
    <div style={{position: 'absolute', right: -250, top: -100, width: 800, height: 800, borderRadius: 400, background: `radial-gradient(circle, ${G.blue}1c, transparent 70%)`}} />
  </AbsoluteFill>
);

const Title: React.FC<{text: string; eyebrow: string}> = ({text, eyebrow}) => {
  const a = useIn(0);
  const words = text.split(' ');
  const hl = words.slice(-2).join(' ');
  const rest = words.slice(0, -2).join(' ');
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', padding: 80, textAlign: 'center'}}>
      <div style={{...a, color: G.purple, fontFamily: HEAD, fontWeight: 700, fontSize: 38, letterSpacing: 6, marginBottom: 36}}>{eyebrow}</div>
      <div style={{...a, color: G.navy, fontFamily: HEAD, fontWeight: 800, fontSize: 96, lineHeight: 1.15}}>
        {rest}{' '}
        <span style={{background: grad, color: '#fff', padding: '0 18px', borderRadius: 14, boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone'}}>{hl}</span>
      </div>
    </AbsoluteFill>
  );
};

const Step: React.FC<{n: number; total: number; big: string; small: string}> = ({n, total, big, small}) => {
  const f = useCurrentFrame();
  const a = useIn(0), b = useIn(10);
  const p = interpolate(f, [0, SCENE], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{justifyContent: 'center', padding: 90}}>
      <div style={{...a, width: 120, height: 120, borderRadius: 30, background: grad, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: HEAD, fontSize: 60, fontWeight: 800, marginBottom: 50, boxShadow: `0 16px 40px ${G.blue}44`}}>{n}</div>
      <div style={{...a, color: G.navy, fontFamily: HEAD, fontSize: 94, fontWeight: 800, lineHeight: 1.1}}>{big}</div>
      <div style={{...b, color: G.gray, fontFamily: BODY, fontSize: 50, lineHeight: 1.4, marginTop: 40}}>{small}</div>
      <div style={{position: 'absolute', bottom: 210, left: 90, right: 90, height: 12, borderRadius: 6, background: G.line}}>
        <div style={{width: `${((n - 1 + p) / total) * 100}%`, height: 12, borderRadius: 6, background: grad}} />
      </div>
    </AbsoluteFill>
  );
};

const Outro: React.FC<{line: string}> = ({line}) => {
  const a = useIn(0), b = useIn(12);
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', padding: 90, textAlign: 'center'}}>
      <div style={{...a, color: G.navy, fontFamily: HEAD, fontSize: 76, fontWeight: 800, lineHeight: 1.18}}>{line}</div>
      <div style={{...b, marginTop: 64, padding: '28px 52px', borderRadius: 16, background: G.blue, color: '#fff', fontFamily: HEAD, fontSize: 46, fontWeight: 700, boxShadow: `0 16px 40px ${G.blue}55`}}>galaxygrowthmedia.com</div>
    </AbsoluteFill>
  );
};

export const tipLightDuration = (p: TipProps) => SCENE * (p.steps.length + 2);
export const TipLight: React.FC<TipProps> = (p) => (
  <AbsoluteFill>
    <Bg />
    <div style={{position: 'absolute', top: 110, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}><Logo height={64} /></div>
    <Sequence durationInFrames={SCENE}><Fade><Title text={p.title} eyebrow={p.eyebrow ?? 'CONTRACTOR TIP'} /></Fade></Sequence>
    {p.steps.map((s, i) => (
      <Sequence key={i} from={SCENE * (i + 1)} durationInFrames={SCENE}><Fade><Step n={i + 1} total={p.steps.length} big={s.big} small={s.small} /></Fade></Sequence>
    ))}
    <Sequence from={SCENE * (p.steps.length + 1)} durationInFrames={SCENE}><Outro line={p.outro} /></Sequence>
  </AbsoluteFill>
);
