import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate} from 'remotion';
import {G, HEAD, BODY, Captions, Cap, Logo, Room, useShake} from './ggm';

// A phone held over a desk, showing a client's lead numbers for two months side by side,
// with the big numbers counting up.
export type PhoneStatProps = {
  client: string;
  period: string;           // e.g. "Leads from the website"
  months: {label: string; rows: {label: string; value: number}[]}[];
  note: string;             // small line under the cards: where the numbers come from
  caps: Cap[];
  duration: number;
};

export const PhoneStat: React.FC<PhoneStatProps> = (p) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const shake = useShake(1);
  const zoom = interpolate(f, [0, 60, 200, 260, 380, 430], [1.0, 1.0, 1.0, 1.18, 1.18, 1.0], {extrapolateRight: 'clamp'});
  const panY = interpolate(f, [200, 260, 380, 430], [0, 0, 0, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <AbsoluteFill style={{transform: `${shake} scale(${zoom}) translateY(${panY}px)`, transformOrigin: '50% 72%'}}>
        <Room />
        <div style={{position: 'absolute', left: 170, top: 600, width: 740, height: 1320, borderRadius: 90, background: '#0b0b0d', padding: 20, boxShadow: '0 50px 100px #000a', transform: 'rotate(2deg)'}}>
          <div style={{width: 700, height: 1280, borderRadius: 72, overflow: 'hidden', background: G.soft, fontFamily: BODY, color: G.navy}}>
            <div style={{height: 150, padding: '56px 36px 0', display: 'flex', alignItems: 'center', gap: 16, background: '#fff', borderBottom: `1px solid ${G.line}`}}>
              <Logo height={34} />
              <div style={{fontSize: 22, color: G.gray}}>Leads</div>
            </div>
            <div style={{padding: '26px 34px 8px'}}>
              <div style={{fontFamily: HEAD, fontWeight: 700, fontSize: 30}}>{p.client}</div>
              <div style={{fontSize: 22, color: G.gray, marginTop: 4}}>{p.period}</div>
            </div>
            {p.months.map((m, mi) => {
              const d = 40 + mi * 100;
              const s = spring({frame: f - d, fps, config: {damping: 200}});
              return (
                <div key={m.label} style={{margin: '18px 30px', background: '#fff', borderRadius: 26, padding: '22px 28px', border: `1px solid ${G.line}`,
                  opacity: s, transform: `translateY(${(1 - s) * 40}px)`, boxShadow: mi === p.months.length - 1 ? `0 10px 30px ${G.blue}22` : 'none'}}>
                  <div style={{fontSize: 22, color: G.gray, fontWeight: 700}}>{m.label}</div>
                  <div style={{display: 'flex', gap: 20, marginTop: 10}}>
                    {m.rows.map((r) => {
                      const v = Math.round(interpolate(f, [d + 5, d + 55], [0, r.value], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
                      return (
                        <div key={r.label} style={{flex: 1}}>
                          <div style={{fontFamily: HEAD, fontWeight: 800, fontSize: 64, color: mi === p.months.length - 1 ? G.blue : G.navy}}>{v}</div>
                          <div style={{fontSize: 20, color: G.gray}}>{r.label}</div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
            <div style={{margin: '10px 34px', fontSize: 18, color: G.gray}}>{p.note}</div>
          </div>
        </div>
      </AbsoluteFill>
      <Captions caps={p.caps} top={260} />
    </AbsoluteFill>
  );
};
