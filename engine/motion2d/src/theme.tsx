// UNTERBAU-Look: Miniatur-Modellstadt bei Nacht. Nachtblau, orange Fensterlichter (echtes Licht, kein Leuchteffekt),
// Tilt-Shift-Unschärfe oben/unten (gehört nur Unterbau), Inter sachlich. Zahlen auf einer Bahnhofs-Anzeigetafel (Fallblatt),
// Balken als Häuserzeilen mit Fenstern, Raster aus Modellhäusern (betroffene: Licht aus), Routen als fahrende LKW-Lichter.
import React from "react";
import {AbsoluteFill, useCurrentFrame, interpolate, random, Easing} from "remotion";
import {s, clamp, ease, fmt} from "./lib";

const NIGHT = "#06101F", NAVY = "#0B1B33", ORANGE = "#FF7A1A", WHITE = "#F5F5F2", RED = "#E23C32";
const SANS = "Inter, 'Inter Display', sans-serif";

const Bg: React.FC<{children?: React.ReactNode; hot?: boolean}> = ({children, hot}) => {
  const f = useCurrentFrame();
  // Modellstadt von schräg oben: Straßenraster + Fensterlichter, die vereinzelt an-/ausgehen
  const lights = Array.from({length: 140}).map((_, i) => {
    const x = random(`lx${i}`) * 1920, y = 560 + random(`ly${i}`) * 520;
    const on = random(`lo${i}${Math.floor((f + i * 7) / 45)}`) > (hot ? 0.75 : 0.25);
    return <div key={i} style={{position: "absolute", left: x, top: y, width: 4 + (y - 560) / 90, height: 3 + (y - 560) / 120, background: on ? "#FFB35C" : "#1a2a44", opacity: 0.85}} />;
  });
  return (
    <AbsoluteFill style={{background: `linear-gradient(180deg, ${NIGHT} 0%, ${NAVY} 55%, #0e2340 100%)`}}>
      <AbsoluteFill style={{backgroundImage: "linear-gradient(rgba(140,170,210,0.10) 2px, transparent 2px), linear-gradient(90deg, rgba(140,170,210,0.10) 2px, transparent 2px)",
        backgroundSize: "120px 120px", transform: "perspective(900px) rotateX(62deg) translateY(330px) scale(2.2)", transformOrigin: "50% 100%", backgroundPosition: `0 ${f * 0.6}px`}} />
      <AbsoluteFill style={{maskImage: "linear-gradient(180deg, transparent 0%, black 30%, black 70%, transparent 100%)"}}>{lights}</AbsoluteFill>
      <AbsoluteFill style={{filter: "blur(4px)", maskImage: "linear-gradient(180deg, black 0%, transparent 30%, transparent 70%, black 100%)"}}>{lights}</AbsoluteFill>
      <AbsoluteFill style={{background: "linear-gradient(180deg, rgba(6,16,31,0.92) 0%, rgba(6,16,31,0.55) 45%, rgba(6,16,31,0.35) 100%)"}} />
      {/* Tilt-Shift: oben und unten unscharf */}
      {children}
      <div style={{position: "absolute", right: 46, top: 32, fontFamily: SANS, fontWeight: 900, fontSize: 18, letterSpacing: 3, color: WHITE, opacity: 0.8}}>UNTERBAU</div>
    </AbsoluteFill>
  );
};
const Write: React.FC<{text: string; at: number; style?: React.CSSProperties}> = ({text, at, style}) => {
  const f = useCurrentFrame(); if (f < s(at)) return null;
  const p = interpolate(f, [s(at), s(at + 0.35)], [0, 1], {...clamp, easing: ease});
  return <span style={{fontFamily: SANS, fontWeight: 700, opacity: p, display: "inline-block", transform: `translateY(${(1 - p) * 14}px)`, ...style}}>{text}</span>;
};
const Label: React.FC<{text?: string}> = ({text}) => {
  const f = useCurrentFrame(); if (!text) return null;
  const p = interpolate(f, [s(0.05), s(0.4)], [0, 1], {...clamp, easing: ease});
  return <div style={{position: "absolute", left: 90, top: 62, opacity: p}}>
    <div style={{fontFamily: SANS, fontWeight: 800, fontSize: 26, letterSpacing: 5, color: WHITE, textTransform: "uppercase"}}>{text}</div>
    <div style={{height: 3, width: 70 * p, background: ORANGE, marginTop: 8}} /></div>;
};
/** Route = fahrende LKW-Lichter (Warenstrom) */
const Thread: React.FC<{x1: number; y1: number; x2: number; y2: number; p: number; straight?: boolean}> = ({x1, y1, x2, y2, p, straight}) => {
  const f = useCurrentFrame();
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2 - (straight ? 0 : Math.hypot(x2 - x1, y2 - y1) * 0.1);
  const len = Math.hypot(x2 - x1, y2 - y1) * 1.15; const d = `M${x1},${y1} Q${mx},${my} ${x2},${y2}`;
  return <g><path d={d} fill="none" stroke="#3a5378" strokeWidth={6} strokeDasharray={len} strokeDashoffset={len * (1 - p)} />
    {p > 0.98 && <path d={d} fill="none" stroke="#FFB35C" strokeWidth={5} strokeLinecap="round" strokeDasharray="2 26" strokeDashoffset={-f * 2.2} />}</g>;
};
/** Laternenlicht (warmer Punkt mit Lichtkegel am Boden) */
const Pin: React.FC<{x: number; y: number; k: number}> = ({x, y, k}) => (
  <g transform={`translate(${x},${y}) scale(${k})`}>
    <ellipse cx={0} cy={4} rx={26} ry={9} fill="rgba(255,150,60,0.25)" /><rect x={-2} y={-30} width={4} height={32} fill="#9fb0c8" /><circle cx={0} cy={-32} r={7} fill="#FFD29A" />
  </g>
);
/** Bahnhofs-Anzeigetafel (Fallblatt): jede Ziffer auf eigener Klappe, klappt beim Hochzählen um */
const Board: React.FC<{value: number; prefix?: string; suffix?: string; dec?: number; at: number; dur: number}> = ({value, prefix = "", suffix = "", dec = 0, at, dur}) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [s(at), s(at + dur)], [0, 1], {...clamp, easing: Easing.bezier(0.16, 1, 0.3, 1)});
  const txt = prefix + fmt(value * p, dec) + suffix;
  return <div style={{display: "flex", gap: 8, justifyContent: "center"}}>
    {txt.split("").map((c, i) => {
      const flip = false;
      return <div key={i} style={{width: c === "." || c === "," || c === " " ? 34 : 104, height: 160, background: "linear-gradient(180deg,#1b2433 0%,#141b27 49%,#0a0f17 51%,#141b27 100%)",
        borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", position: "relative", boxShadow: "0 10px 24px rgba(0,0,0,0.6), inset 0 0 0 2px #2a3446"}}>
        <span style={{fontFamily: SANS, fontWeight: 900, fontSize: 120, color: WHITE, transform: flip ? "scaleY(0.6)" : undefined}}>{c}</span>
        <div style={{position: "absolute", left: 0, right: 0, top: "50%", height: 3, background: "#05080d"}} />
      </div>;
    })}
  </div>;
};
/* ---- Unterbau-eigene Symbole: schlichte Infrastruktur-Piktogramme (Strom, Wasser, Schiene, LKW, Rohr ...) ---- */
const L = (st: any) => ({...st, strokeWidth: 6});
const icons: Record<string, (st: any, c: string) => React.ReactNode> = {
  power: (st) => <path {...L(st)} d="M56 6 L22 56 H48 L40 94 L78 40 H52 Z" />,
  water: (st) => <path {...L(st)} d="M50 8 C50 8 20 46 20 64 a30 30 0 0 0 60 0 C80 46 50 8 50 8 Z" />,
  pipe: (st) => <path {...L(st)} d="M6 40 H60 a14 14 0 0 1 14 14 V94 M6 60 H50 a4 4 0 0 1 4 4 V94 M6 34 v32 M66 94 h28" />,
  train: (st) => <g {...L(st)}><rect x={22} y={10} width={56} height={62} rx={10} {...L(st)} /><path {...L(st)} d="M22 44 H78 M34 72 L22 92 M66 72 L78 92 M30 84 H70" /></g>,
  truck: (st) => <g><path {...L(st)} d="M6 28 H60 V72 H6 Z M60 42 H80 L94 58 V72 H60" /><circle cx={24} cy={78} r={8} {...L(st)} /><circle cx={76} cy={78} r={8} {...L(st)} /></g>,
  house: (st) => <path {...L(st)} d="M10 46 L50 12 L90 46 V90 H10 Z M40 90 V64 H60 V90" />,
  tower: (st) => <path {...L(st)} d="M50 6 L30 94 M50 6 L70 94 M36 66 H64 M40 44 H60 M20 30 H80 M50 6 V20" />,
  store: (st) => <path {...L(st)} d="M8 40 L16 12 H84 L92 40 Z M16 40 V90 H84 V40 M30 56 H70 M30 70 H70" />,
  server: (st) => <g>{[10, 40, 70].map((y) => <rect key={y} x={14} y={y} width={72} height={22} rx={3} {...L(st)} />)}</g>,
  phone: (st) => <rect x={30} y={8} width={40} height={84} rx={8} {...L(st)} />,
  ship: (st) => <path {...L(st)} d="M6 60 H94 L80 86 H20 Z M26 58 V36 H62 V58 M44 34 V16" />,
  clock: (st) => <g><circle cx={50} cy={50} r={40} {...L(st)} /><path {...L(st)} d="M50 22 V50 L68 60" /></g>,
  person: (st) => <g><circle cx={50} cy={28} r={14} {...L(st)} /><path {...L(st)} d="M20 92 C20 64 80 64 80 92" /></g>,
  doc: (st) => <path {...L(st)} d="M24 8 H62 L78 24 V92 H24 Z M34 46 H68 M34 60 H68 M34 74 H56" />,
  money: (st) => <g><rect x={8} y={26} width={84} height={48} rx={6} {...L(st)} /><circle cx={50} cy={50} r={12} {...L(st)} /></g>,
  factory: (st) => <path {...L(st)} d="M8 90 V46 L32 60 V46 L56 60 V22 H74 V90 Z" />,
};
/** Station = Modellhaus (isometrisch) mit Fenstern; hot = Licht aus, rote Warnlampe */
const Node: React.FC<{hot?: boolean; children?: React.ReactNode}> = ({hot, children}) => (
  <div style={{width: 200, height: 190, margin: "0 auto", position: "relative", display: "flex", alignItems: "flex-end", justifyContent: "center"}}>
    <svg width={200} height={190} viewBox="0 0 200 190" style={{position: "absolute", left: 0, top: 0}}>
      <path d="M100 20 L180 56 L180 150 L100 186 L20 150 L20 56 Z" fill="#0e1f39" stroke="#2c456b" strokeWidth={2} />
      <path d="M100 20 L180 56 L100 92 L20 56 Z" fill="#183154" />
      <path d="M100 92 L100 186" stroke="#2c456b" strokeWidth={2} />
      {[0, 1, 2].map((r) => [0, 1].map((c) => <path key={`${r}${c}`} d={`M${34 + c * 30} ${80 + r * 26 + c * 13} l16 7 v13 l-16 -7 z`} fill={hot ? "#16233a" : "#FFB35C"} />))}
      {hot && <circle cx={168} cy={40} r={8} fill={RED} />}
    </svg>
    <div style={{position: "absolute", right: 22, top: 88, transform: "scale(0.55)", transformOrigin: "right top"}}>{children}</div>
  </div>
);
/** Raster = Modellhäuser von oben; betroffene: Licht aus */
const Tile: React.FC<{hot?: boolean; icon?: string; i?: number}> = ({hot, i = 0}) => (
  <svg width={66} height={66} viewBox="0 0 66 66">
    <rect x={6} y={14} width={54} height={46} fill="#10223f" stroke="#2c456b" strokeWidth={2} /><path d="M2 16 L33 2 L64 16 Z" fill="#183154" />
    {[0, 1].map((r) => [0, 1, 2].map((c) => <rect key={`${r}${c}`} x={13 + c * 15} y={24 + r * 16} width={9} height={9} fill={hot ? "#16233a" : (random(`w${i}${r}${c}`) > 0.2 ? "#FFB35C" : "#16233a")} />))}
  </svg>
);

export const T = {
  c: {ink: WHITE, muted: "#8a99b0", accent: ORANGE, hot: RED, land: "#0f2241", border: "#2c456b", dot: "#FFB35C", hl: (o: number) => `rgba(255,122,26,${0.18 + 0.4 * o})`,
      track: "#2c456b", panelAccent: ORANGE, nodeInk: WHITE, panelInk: WHITE, cardInk: WHITE, cardHotInk: WHITE, tileInk: WHITE, bubble: "#1f3d66", sheetInk: WHITE, sheetLine: "rgba(245,245,242,0.2)"},
  font: {head: SANS, body: SANS, num: SANS, mono: "DejaVu Sans Mono, monospace"},
  headWeight: 900, headStyle: {letterSpacing: -1} as React.CSSProperties, iconStroke: 6, iconFilter: undefined as string | undefined, mapFilter: undefined as string | undefined,
  glow: false, borderW: 1.0, tileJitter: 0, gridRows: false, num: {sep: ".", decSep: ","},
  Bg, Write, Label, Thread, Pin, Board, icons, Node, Tile, counterPad: "30px 50px",
  tag: {background: "rgba(6,16,31,0.85)", borderLeft: `4px solid ${ORANGE}`, padding: "4px 14px"} as React.CSSProperties, tagText: {color: WHITE} as React.CSSProperties,
  panel: {background: "transparent", padding: "10px 30px"} as React.CSSProperties,
  node: {} as React.CSSProperties, nodeHot: {} as React.CSSProperties,
  card: {background: "linear-gradient(180deg,#132744,#0a1629)", border: "2px solid #2c456b", borderRadius: 6, boxShadow: "0 30px 60px rgba(0,0,0,0.6)"} as React.CSSProperties,
  cardTop: "ANZEIGE · GLEIS 4", cardTopStyle: {fontFamily: SANS, fontWeight: 800, fontSize: 22, letterSpacing: 4, color: "#8a99b0"} as React.CSSProperties,
  cardHot: {background: "linear-gradient(180deg,#3a1a0a,#160904)", border: `3px solid ${ORANGE}`, borderRadius: 6} as React.CSSProperties,
  tile: {} as React.CSSProperties, tileHot: {} as React.CSSProperties,
  sheet: {background: "#0d1d36", border: "2px solid #3a5378", boxShadow: "0 20px 50px rgba(0,0,0,0.7)"} as React.CSSProperties,
  bar: {background: "radial-gradient(#FFB35C 2.6px, transparent 3.2px) 6px 8px / 16px 18px, linear-gradient(90deg, #10223f 0 96%, #0a1629 96% 100%) 0 0 / 60px 100%", border: "2px solid #2c456b"} as React.CSSProperties,
  barHot: {background: "radial-gradient(#FFD29A 3px, transparent 3.6px) 6px 8px / 16px 18px, linear-gradient(90deg, #1b2c4a 0 96%, #0a1629 96% 100%) 0 0 / 60px 100%", border: `3px solid ${ORANGE}`} as React.CSSProperties,
};
