/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { WebSocketStatus } from "src/@types/types";
import { MAIN_API } from "src/config";

const useWS = () => {

    const { gameID } = useParams();
    const [connectionStatus, setConnectionStatus] = useState<WebSocketStatus>('Uninstantiated');
    const [currentSession, setCurrentSession] = useState<string>('');

    const { readyState, sendJsonMessage, lastJsonMessage } = useWebSocket(
        MAIN_API.web_socket_url + currentSession, {share: true}
    );

    useEffect(() => {
        if (gameID) {
            setCurrentSession(gameID);
        };
    }, [gameID]);

    useEffect(() => { setConnectionStatus(translateState(readyState)) }, [readyState]);

    return { currentSession, connectionStatus, sendJsonMessage, lastJsonMessage };
};

export default useWS;

function translateState(status: ReadyState): WebSocketStatus {
    switch (status) {
        case ReadyState.CLOSED:
            return 'Closed';
        case ReadyState.CLOSING:
            return 'Closing';
        case ReadyState.CONNECTING:
            return 'Connecting';
        case ReadyState.OPEN:
            return 'Open';
    }
    return 'Uninstantiated';
}