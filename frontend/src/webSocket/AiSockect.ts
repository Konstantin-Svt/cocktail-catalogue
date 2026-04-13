import { useEffect, useRef, useState } from 'react';

const [wsData, setWsData] = useState(null);
const socket = useRef<WebSocket | null>(null);

useEffect(() => {
    socket.current = new WebSocket('wss://cocktail-catalogue-dev.onrender.com/ws/aifilters/');

    socket.current.onopen = () => {
        console.log('WS Connected ✅');
    };

    socket.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('WS Message:', data);
        setWsData(data); 
    };

    socket.current.onerror = (error) => {
        console.error('WS Error ❌', error);
    };

    socket.current.onclose = () => {
        console.log('WS Disconnected 🔌');
    };


    return () => {
        socket.current?.close();
    };
}, []);


const sendAiFilterRequest = (text: string) => {
    if (socket.current?.readyState === WebSocket.OPEN) {
        socket.current.send(JSON.stringify({ message: text }));
    }
};