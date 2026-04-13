import { useEffect, useRef, useState } from 'react';

const DEFAULT_WS_URL = 'wss://cocktail-catalogue-uj8l.onrender.com/ws';
export const BASE_WS_URL =
  (import.meta as any).env?.VITE_WS_URL || DEFAULT_WS_URL;

export function useAiWebSocket() {
  const [wsData, setWsData] = useState<any>(null);
  const socket = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`${BASE_WS_URL}/aifilters/`);
    socket.current = ws;

    ws.onopen = () => {
      console.log('WS Connected ✅');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WS Message:', data);
        setWsData(data);
      } catch (e) {
        console.error('JSON parse error ❌', e);
      }
    };

    ws.onerror = (error) => {
      console.error('WS Error ❌', error);
    };

    ws.onclose = () => {
      console.log('WS Disconnected 🔌');
    };

    return () => {
      ws.close();
    };
  }, []);

  const sendAiFilterRequest = (text: string) => {
    if (socket.current?.readyState === WebSocket.OPEN) {
      socket.current.send(JSON.stringify({ message: text }));
    } else {
      console.warn('WebSocket not ready ❗');
    }
  };

  return { wsData, sendAiFilterRequest };
}