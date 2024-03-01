import { Box as MUIBox, Button, Stack, Typography } from '@mui/material';
import { useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import useWS from 'src/hooks/useWS';

// ----------------------------------------------------------------------

type PlayerPosition = {
    id: number;
    position: THREE.Vector3;
    target: THREE.Vector3;
};

type TeamPositions = {
    Chaser_1: PlayerPosition;
    Chaser_2: PlayerPosition;
    Chaser_3: PlayerPosition;
    Beater_1: PlayerPosition;
    Beater_2: PlayerPosition;
    Keeper: PlayerPosition;
    Seeker: PlayerPosition;
}

export default function Test() {

    const { connectionStatus, lastJsonMessage, sendJsonMessage } = useWS();

    const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);
    const [gameOver, setGameOver] = useState<boolean>(false);
    const [team1Score, setTeam1Score] = useState<number>(0);
    const [team2Score, setTeam2Score] = useState<number>(0);

    const [totalTime, setTotalTime] = useState<number>(0);
    const [currentTime, setCurrentTime] = useState<number>(0);

    const [matrixSize, setMatrixSize] = useState<{ x: number, y: number, z: number }>();
    const [spacing, setSpacing] = useState<number>();
    const [speed, setSpeed] = useState<number>();
    const [team1Color, setTeam1Color] = useState<number>();
    const [team2Color, setTeam2Color] = useState<number>();

    const [team1, setTeam1] = useState<TeamPositions>();
    const [team2, setTeam2] = useState<TeamPositions>();

    function sendNewMessage(message: string) {
        sendJsonMessage({
            type: 'start_game',
            text: message
        });
    };

    useEffect(() => {
        if (lastJsonMessage && Object.keys(lastJsonMessage).includes('type')) {
            const content = (lastJsonMessage as any);
            if (content.type === 'game_state_update') {
                const settings = content.message.settings;
                if (!matrixSize || !spacing || !speed || !team1Color || !team2Color) {
                    setMatrixSize(settings.matrix_size);
                    setSpacing(settings.spacing);
                    setTeam1Color(settings.team_1_color);
                    setTeam2Color(settings.team_2_color);
                    setSpeed(settings.speed);
                };

                setTotalTime(settings.total_time);
                setCurrentTime(settings.current_time);

                const team_1 = content.message.team_1;
                const team_2 = content.message.team_2;

                setTeam1(team_1);
                setTeam2(team_2);

                setTeam1Score(content.message.score.team_1);
                setTeam2Score(content.message.score.team_2);
            } else if (content.type === 'game_over') {
                setGameOver(true);
            } else {
                console.log('state update');
            }
        }
    }, [lastJsonMessage]);

    if (!matrixSize || !spacing || !speed || !team1Color || !team2Color) {
        return (
            <Stack spacing={3} direction={'column'} justifyContent={'center'} alignItems={'center'} width={'100%'}>
                <Typography variant={'h3'}>Status: {connectionStatus}</Typography>
                <Button onClick={() => { sendNewMessage('start') }} variant={'contained'}>
                    Start Game
                </Button>
            </Stack>
        );
    };

    const renderPlayerSpheres = (team: typeof team1 | typeof team2, teamColor: number) => {
        return team && Object.keys(team).map((position, index) => {
            const player = team[position as keyof typeof team];
            const positionVector = new THREE.Vector3(player.position.x * spacing, player.position.y * spacing, player.position.z * spacing);
            const targetVector = new THREE.Vector3(player.target.x * spacing, player.target.y * spacing, player.target.z * spacing);
    
            return (
                <PlayerSphere
                    key={index}
                    id={player.id}
                    color={teamColor}
                    position={positionVector}
                    target={targetVector}
                    speed={speed}
                    spacing={spacing}
                    label={position[0]}
                    selectedPlayer={selectedPlayer}
                />
            );
        });
    };    

    return (
        <Stack spacing={3} direction={'column'} justifyContent={'center'} alignItems={'center'} width={'100%'}>
            {gameOver ?
                <Typography variant={'h3'}>Game Over</Typography> :
                <Typography variant={'h3'}>{currentTime}/{totalTime}</Typography>
            }
            <Typography variant={'h3'}>Status: {connectionStatus}</Typography>
            <MUIBox component={'div'} width={'100%'} height={'25vh'}>
                <Canvas camera={{ position: [0, 10, 5] }}>
                    <OrbitControls
                        enablePan={true}
                        maxPolarAngle={Math.PI / 2}
                    />
                    <ambientLight intensity={0.5} />
                    <directionalLight position={[0, 10, 0]} intensity={1} />
                    <pointLight position={[10, 10, 10]} />
                    <PlayingPitch
                        length={matrixSize.x}
                        width={matrixSize.y}
                        height={matrixSize.z}
                        color={0xffffff}
                        spacing={spacing}
                    />
                    {renderPlayerSpheres(team1, team1Color)}
                    {renderPlayerSpheres(team2, team2Color)}
                </Canvas>
            </MUIBox>
            <Stack spacing={3} direction={'row'} justifyContent={'center'} alignItems={'center'} width={'100%'}>
                <Stack spacing={3} direction={'column'} justifyContent={'center'} alignItems={'center'} width={'100%'}>
                    <Typography variant={'h3'}>Team 1 Score: {team1Score}</Typography>
                    {team1 && Object.keys(team1).map((position, index) => {
                        const player = team1[position as keyof typeof team1];
                        return (
                            <Button key={index} onClick={() => { setSelectedPlayer(player.id) }} variant={'contained'}>
                                {position}
                            </Button>
                        );
                    })}
                </Stack>
                <Stack spacing={3} direction={'column'} justifyContent={'center'} alignItems={'center'} width={'100%'}>
                    <Typography variant={'h3'}>Team 2 Score: {team2Score}</Typography>
                    {team2 && Object.keys(team2).map((position, index) => {
                        const player = team2[position as keyof typeof team2];
                        return (
                            <Button key={index} onClick={() => { setSelectedPlayer(player.id) }} variant={'contained'}>
                                {position}
                            </Button>
                        );
                    })}
                </Stack>
            </Stack>
            <Button onClick={() => { setSelectedPlayer(null) }} variant={'contained'}>
                Clear
            </Button>
        </Stack>
    );
};

// ----------------------------------------------------------------------

// type PlayerSphereProps = {
//     id: number;
//     color: number;
//     position: THREE.Vector3;
//     target: THREE.Vector3;
//     speed: number;
//     spacing: number;
//     label: string;
//     selectedPlayer: number | null;
// };

// function PlayerSphere({ id, color, position, target, speed, spacing, label, selectedPlayer }: PlayerSphereProps) {
//     const ref = useRef<THREE.Mesh>(null!);
//     const material = new THREE.MeshBasicMaterial({ color: color });

//     useFrame(() => {
//         const targetVector = new THREE.Vector3(target.x * spacing, target.y * spacing, target.z * spacing);
//         ref.current.position.lerp(targetVector, speed);
//         material.color.set(id === selectedPlayer ? 0xffffff : color);
//     });

//     return (
//         <mesh ref={ref} position={position} material={material}>
//             <sphereGeometry args={[0.20, 164, 164]} />
//         </mesh>
//     );
// };

type PlayerSphereProps = {
    id: number;
    color: number;
    position: THREE.Vector3;
    target: THREE.Vector3;
    speed: number;
    spacing: number;
    label: string;
    selectedPlayer: number | null;
};

function PlayerSphere({ id, color, position, target, speed, spacing, label, selectedPlayer }: PlayerSphereProps) {
    const ref = useRef<THREE.Mesh>(null!);
    const material = new THREE.MeshPhongMaterial({ color: color, shininess: 100 });

    useFrame(() => {
        const targetVector = new THREE.Vector3(target.x * spacing, target.y * spacing, target.z * spacing);
        ref.current.position.lerp(targetVector, speed);
        material.color.set(id === selectedPlayer ? 0xffffff : color);
    });

    return (
        <mesh ref={ref} position={position} material={material}>
            <sphereGeometry args={[0.20, 32, 32]} />
        </mesh>
    );
};

// ----------------------------------------------------------------------

type PlayingPitchProps = {
    length: number;
    width: number;
    height: number;
    color: number;
    spacing: number;
};

function PlayingPitch({ length, width, height, color, spacing }: PlayingPitchProps) {
    const pitchGroup = useMemo(() => {
        const group = new THREE.Group();

        // Create the main body of the prism with rectangular top and bottom
        const bodyGeometry = new THREE.BoxGeometry(length * spacing, height * spacing, width * spacing);
        const bodyMaterial = new THREE.MeshBasicMaterial({ color: color, transparent: true, opacity: 0.025, side: THREE.DoubleSide });
        const bodyMesh = new THREE.Mesh(bodyGeometry, bodyMaterial);
        group.add(bodyMesh);

        // Create the flat green bottom
        const bottomGeometry = new THREE.BoxGeometry(length, 0.1, width);
        const bottomMaterial = new THREE.MeshPhongMaterial({ color: 0x008000 }); // Green color
        const bottomMesh = new THREE.Mesh(bottomGeometry, bottomMaterial);
        bottomMesh.position.set(0, -(height * spacing / 2) - 0.05, 0);
        group.add(bottomMesh);

        return group;
    }, [length, width, height, color, spacing]);

    return <primitive object={pitchGroup} />;
}