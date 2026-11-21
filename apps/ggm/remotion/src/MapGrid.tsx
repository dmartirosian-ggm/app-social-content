import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate, random} from 'remotion';
import {G, HEAD, BODY, Captions, Cap, Logo, useShake} from './ggm';

// A Google Maps rank scan shown on a phone held in the hand. Only counts from the scan are
// drawn (how many of the grid points ranked in the top 3), never invented positions.
export type MapProps = {
  client: string;
  keyword: string;
  top3: number;
  total: number;
  avgRank: string;
  scanDate: string;
  extra: {label: string; value: string}[];
  caps: Cap[];
  duration: number;
};

const Streets: React.FC = () => {
  const lines = [] as React.ReactNode[];
  for (let i = 0; i < 14; i++) {
    const y = 40 + i * 70 + random('sy' + i) * 30;
    lines.push(<line key={'h' + i} x1={0} x2={720} y1={y} y2={y + (random('sk' + i) - 0.5) * 80} stroke="#fff" strokeWidth={i % 4 === 0 ? 14 : 6} />);
    const x = 30 + i * 55 + random('sx' + i) * 20;
    lines.push(<line key={'v' + i} y1={0} y2={1100} x1={x} x2={x + (random('sv' + i) - 0.5) * 90} stroke="#fff" strokeWidth={i % 5 === 0 ? 14 : 6} />);
  }
  return (
    <svg width={720} height={1100} style={{position: 'absolute', inset: 0}}>
      <rect width={720} height={1100} fill="#EEF1E8" />
      <path d="M0 820 C 180 760, 300 900, 720 840 L720 1100 L0 1100 Z" fill="#CFE3F5" />
      <rect x={430} y={120} width={180} height={140} rx={20} fill="#D9EBD3" />
      <rect x={80} y={520} width={140} height={110} rx={20} fill="#D9EBD3" />
      {lines}
    </svg>
  );
};

export const MapGrid: React.FC<MapProps> = (p) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const shake = useShake(0.8);
  const n = 7;
  const shown = Math.round(interpolate(f, [70, 190], [0, p.top3], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const zoom = interpolate(f, [0, 60, 210, 260], [0.95, 1.0, 1.0, 1.12], {extrapolateRight: 'clamp'});
  const panel = spring({frame: f - 200, fps, config: {damping: 200}});
  return (
    <AbsoluteFill style={{background: 'linear-gradient(180deg, #3a3530 0%, #2a2622 50%, #4b3d30 100%)'}}>
      <AbsoluteFill style={{transform: `${shake} scale(${zoom})`, transformOrigin: '50% 60%'}}>
        {/* phone */}
        <div style={{position: 'absolute', left: 160, top: 560, width: 760, height: 1300, borderRadius: 90, background: '#0b0b0d', padding: 20, boxShadow: '0 50px 100px #000a', transform: 'rotate(-3deg)'}}>
          <div style={{position: 'relative', width: 720, height: 1260, borderRadius: 72, overflow: 'hidden', background: '#fff', fontFamily: BODY}}>
            <div style={{height: 150, padding: '56px 36px 0', display: 'flex', alignItems: 'center', gap: 16, borderBottom: `1px solid ${G.line}`}}>
              <Logo height={34} />
              <div style={{fontSize: 22, color: G.gray}}>Map rankings</div>
            </div>
            <div style={{padding: '22px 36px 10px'}}>
              <div style={{fontFamily: HEAD, fontWeight: 700, fontSize: 30, color: G.navy}}>{p.client}</div>
              <div style={{fontSize: 22, color: G.gray, marginTop: 4}}>"{p.keyword}" · scanned {p.scanDate}</div>
            </div>
            <div style={{position: 'relative', height: 820, overflow: 'hidden'}}>
              <Streets />
              {Array.from({length: n * n}).map((_, i) => {
                const r = Math.floor(i / n), c = i % n;
                const on = i < shown;
                const s = spring({frame: f - 70 - i * (120 / (n * n)), fps, config: {damping: 14}});
                return (
                  <div key={i} style={{position: 'absolute', left: 70 + c * 96 - 30, top: 70 + r * 104 - 30, width: 60, height: 60, borderRadius: 30,
                    background: on ? '#1E9E5A' : '#9AA3B2', color: '#fff', fontFamily: HEAD, fontWeight: 800, fontSize: 19,
                    display: 'flex', alignItems: 'center', justifyContent: 'center', border: '4px solid #fff', boxShadow: '0 4px 10px #0003',
                    transform: `scale(${on ? s : 0.6})`, opacity: on ? 1 : 0.35}}>
                    {on ? <svg width="30" height="30" viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="#fff" strokeWidth="3.4" strokeLinecap="round" strokeLinejoin="round" /></svg> : null}
                  </div>
                );
              })}
            </div>
            <div style={{position: 'absolute', left: 24, right: 24, bottom: 28 - (1 - panel) * 300, background: '#fff', borderRadius: 28, boxShadow: '0 -10px 40px #0002', padding: '22px 28px', display: 'flex', gap: 22}}>
              <div style={{flex: 1}}>
                <div style={{fontSize: 18, color: G.gray}}>Spots in the top 3 on Google Maps</div>
                <div style={{fontFamily: HEAD, fontWeight: 800, fontSize: 44, color: G.navy}}>{shown} of {p.total}</div>
              </div>
              <div style={{flex: 1}}>
                <div style={{fontSize: 18, color: G.gray}}>Average rank</div>
                <div style={{fontFamily: HEAD, fontWeight: 800, fontSize: 44, color: G.navy}}>{p.avgRank}</div>
              </div>
            </div>
            {p.extra.length > 0 && f > 330 && (
              <div style={{position: 'absolute', left: 24, right: 24, top: 260, background: '#fff', borderRadius: 24, padding: '18px 24px', boxShadow: '0 10px 40px #0003', opacity: interpolate(f, [330, 345], [0, 1], {extrapolateRight: 'clamp'})}}>
                {p.extra.map((e) => (
                  <div key={e.label} style={{display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: `1px solid ${G.line}`, fontSize: 22}}>
                    <span style={{color: G.gray}}>{e.label}</span><span style={{fontWeight: 700, color: G.navy}}>{e.value}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </AbsoluteFill>
      <Captions caps={p.caps} top={250} />
    </AbsoluteFill>
  );
};
