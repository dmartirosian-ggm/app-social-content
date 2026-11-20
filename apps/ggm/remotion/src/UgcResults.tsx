import React from 'react';
import {AbsoluteFill, useCurrentFrame, interpolate} from 'remotion';
import {G, BODY, HEAD, Captions, Cap, Room, Laptop, Cursor, Logo, useShake, ease} from './ggm';

export type UgcProps = {
  client: string;
  city: string;
  chartTitle: string;
  chartSub: string;       // period / source line on screen
  months: string[];       // short labels
  monthsLong: string[];   // for tooltip
  values: number[];
  unit: string;           // "calls" / "clicks"
  tiles: {label: string; value: string; note: string}[];
  caps: Cap[];
  duration: number;
};

const Dashboard: React.FC<UgcProps & {hover: number; draw: number}> = (p) => {
  const W = 960, H = 600;
  const cx = 40, cy = 205, cw = 560, ch = 300;
  const max = Math.max(...p.values) * 1.15;
  const n = p.values.length;
  const pts = p.values.map((v, i) => [cx + (i / (n - 1)) * cw, cy + ch - (v / max) * ch]);
  const shown = Math.max(2, Math.ceil(p.draw * n));
  const path = pts.slice(0, shown).map((q, i) => `${i ? 'L' : 'M'}${q[0].toFixed(1)},${q[1].toFixed(1)}`).join(' ');
  const area = path + ` L${pts[shown - 1][0]},${cy + ch} L${cx},${cy + ch} Z`;
  const hp = pts[n - 1];
  return (
    <div style={{width: W, height: H, fontFamily: BODY, color: G.navy, position: 'relative', background: '#fff'}}>
      <div style={{height: 64, borderBottom: `1px solid ${G.line}`, display: 'flex', alignItems: 'center', padding: '0 24px', gap: 16}}>
        <Logo height={30} />
        <div style={{fontSize: 15, color: G.gray}}>Client dashboard</div>
        <div style={{marginLeft: 'auto', fontSize: 15, fontWeight: 700}}>{p.client}</div>
      </div>
      <div style={{display: 'flex', gap: 22, padding: '14px 40px 0', fontSize: 14, color: G.gray}}>
        {['Overview', 'Calls & leads', 'Search', 'Map rankings', 'Reviews'].map((t, i) => (
          <div key={t} style={{paddingBottom: 8, borderBottom: i === 0 ? `3px solid ${G.blue}` : '3px solid transparent', color: i === 0 ? G.navy : G.gray, fontWeight: i === 0 ? 700 : 500}}>{t}</div>
        ))}
      </div>
      <div style={{position: 'absolute', left: cx, top: 120, fontFamily: HEAD, fontWeight: 700, fontSize: 21}}>{p.chartTitle}</div>
      <div style={{position: 'absolute', left: cx, top: 150, fontSize: 13, color: G.gray}}>{p.chartSub}</div>
      <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
        {[0, 0.25, 0.5, 0.75, 1].map((t) => (
          <g key={t}>
            <line x1={cx} x2={cx + cw} y1={cy + ch * t} y2={cy + ch * t} stroke={G.line} />
            <text x={cx + cw + 8} y={cy + ch * t + 4} fontSize={11} fill={G.gray} fontFamily="DM Sans">{Math.round(max * (1 - t))}</text>
          </g>
        ))}
        <defs><linearGradient id="ar" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor={G.blue} stopOpacity="0.22" /><stop offset="1" stopColor={G.blue} stopOpacity="0" /></linearGradient></defs>
        <path d={area} fill="url(#ar)" />
        <path d={path} fill="none" stroke={G.blue} strokeWidth={3} />
        {pts.slice(0, shown).map((q, i) => <circle key={i} cx={q[0]} cy={q[1]} r={4} fill="#fff" stroke={G.blue} strokeWidth={2.5} />)}
        {p.months.map((m, i) => <text key={m + i} x={pts[i][0]} y={cy + ch + 22} fontSize={12} fill={G.gray} textAnchor="middle" fontFamily="DM Sans">{m}</text>)}
        {p.hover > 0 && <line x1={hp[0]} x2={hp[0]} y1={cy} y2={cy + ch} stroke={G.navy} strokeDasharray="4 4" opacity={p.hover * 0.5} />}
      </svg>
      {p.hover > 0 && (
        <div style={{position: 'absolute', left: hp[0] - 150, top: hp[1] - 70, width: 135, background: G.navy, color: '#fff', borderRadius: 8, padding: '8px 10px', fontSize: 13, opacity: p.hover}}>
          <div style={{color: '#B8C0D0'}}>{p.monthsLong[n - 1]}</div>
          <div style={{fontWeight: 700, fontSize: 16}}>{p.values[n - 1]} {p.unit}</div>
        </div>
      )}
      <div style={{position: 'absolute', left: 660, top: 120, width: 270, display: 'flex', flexDirection: 'column', gap: 14}}>
        {p.tiles.map((t) => (
          <div key={t.label} style={{border: `1px solid ${G.line}`, borderRadius: 10, padding: '12px 14px'}}>
            <div style={{fontSize: 12.5, color: G.gray}}>{t.label}</div>
            <div style={{fontFamily: HEAD, fontWeight: 700, fontSize: 30, marginTop: 2}}>{t.value}</div>
            <div style={{fontSize: 12, color: '#13915a', fontWeight: 700}}>{t.note}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const UgcResults: React.FC<UgcProps> = (p) => {
  const f = useCurrentFrame();
  const shake = useShake(1);
  const D = p.duration;
  // camera: wide -> push into chart -> push into last point -> pull back for CTA
  const zoom = interpolate(f, [0, 60, 150, 260, 330, D - 90, D - 60], [1.0, 1.0, 1.55, 1.55, 1.9, 1.9, 1.05], {extrapolateRight: 'clamp', easing: (t) => t * t * (3 - 2 * t)});
  const panX = interpolate(f, [0, 60, 150, 260, 330, D - 90, D - 60], [0, 0, 90, 90, -80, -80, 0], {extrapolateRight: 'clamp'});
  const panY = interpolate(f, [0, 60, 150, 260, 330, D - 90, D - 60], [0, 0, -40, -40, 30, 30, 0], {extrapolateRight: 'clamp'});
  const draw = ease(f, 70, 200, 0, 1);
  const cursorX = interpolate(f, [0, 200, 270, 300], [300, 420, 620, 640], {extrapolateRight: 'clamp'});
  const cursorY = interpolate(f, [0, 200, 270, 300], [520, 430, 330, 300], {extrapolateRight: 'clamp'});
  const hover = ease(f, 280, 295, 0, 1);
  const click = f >= 285 && f < 300 ? (f - 285) / 15 : 0;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <AbsoluteFill style={{transform: `${shake} scale(${zoom}) translate(${panX}px, ${panY}px)`, transformOrigin: '50% 58%'}}>
        <Room />
        <div style={{position: 'absolute', left: 40, top: 760}}>
          <Laptop>
            <div style={{transform: 'scale(1)', transformOrigin: 'top left', position: 'relative'}}>
              <Dashboard {...p} hover={hover} draw={draw} />
              <Cursor x={cursorX} y={cursorY} click={click} />
            </div>
          </Laptop>
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(0deg, #00000000 60%, #00000018 100%)', mixBlendMode: 'multiply'}} />
      <Captions caps={p.caps} top={300} />
    </AbsoluteFill>
  );
};
