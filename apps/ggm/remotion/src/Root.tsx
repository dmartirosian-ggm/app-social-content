import React from 'react';
import {Composition} from 'remotion';
import {TipLight, tipLightDuration, TipProps} from './TipLight';
import {UgcResults, UgcProps} from './UgcResults';
import {MapGrid, MapProps} from './MapGrid';
import {PhoneStat, PhoneStatProps} from './PhoneStat';

// Real props come from the JSON files in apps/ggm/clips/. These defaults only keep the
// compositions valid when opened without props.
const tip: TipProps = {title: 'Contractor tip', steps: [{big: 'Step', small: 'Detail'}], outro: 'Galaxy Growth Media'};
const ugc: UgcProps = {
  client: 'Client', city: 'City', chartTitle: 'Chart', chartSub: 'Period', months: ['A', 'B'], monthsLong: ['A', 'B'],
  values: [1, 2], unit: 'calls', tiles: [], caps: [], duration: 300,
};

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="TipLight" component={TipLight} durationInFrames={tipLightDuration(tip)} fps={30} width={1080} height={1920}
      defaultProps={tip} calculateMetadata={({props}) => ({durationInFrames: tipLightDuration(props)})} />
    <Composition id="Ugc" component={UgcResults} durationInFrames={300} fps={30} width={1080} height={1920}
      defaultProps={ugc} calculateMetadata={({props}) => ({durationInFrames: props.duration})} />
    <Composition id="MapGrid" component={MapGrid} durationInFrames={300} fps={30} width={1080} height={1920}
      defaultProps={{client: 'Client', keyword: 'keyword', top3: 0, total: 49, avgRank: '-', scanDate: '', extra: [], caps: [], duration: 300} as MapProps}
      calculateMetadata={({props}) => ({durationInFrames: props.duration})} />
    <Composition id="PhoneStat" component={PhoneStat} durationInFrames={300} fps={30} width={1080} height={1920}
      defaultProps={{client: 'Client', period: '', months: [], note: '', caps: [], duration: 300} as PhoneStatProps}
      calculateMetadata={({props}) => ({durationInFrames: props.duration})} />
  </>
);
