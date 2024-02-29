import { Box as MUIBox, Button, Stack } from '@mui/material';
import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import useWS from 'src/hooks/useWS';

// ----------------------------------------------------------------------

const matrixSize = { x: 13, y: 8, z: 8 };
const spacing = 1.0;

export default function Test() {

    const { currentSession } = useWS();
    useEffect(() => {
        console.log('Game ID: ' + currentSession);
    }, [currentSession]);

    const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);

    const speed = 0.1;

    const team1Color = 0xff0000;
    const team2Color = 0x0000ff;
    const playerCount = 14;

    const playerPositions = Array.from({ length: playerCount }).map((_, i) => ({
        position: new THREE.Vector3(
            (Math.random() * (matrixSize.x - 1) - (matrixSize.x - 1) / 2) * spacing,
            (Math.random() * (matrixSize.y - 1) - (matrixSize.y - 1) / 2) * spacing,
            (Math.random() * (matrixSize.z - 1) - (matrixSize.z - 1) / 2) * spacing
        ),
        color: i < playerCount / 2 ? team1Color : team2Color,
        target: new THREE.Vector3(
            (Math.random() * (matrixSize.x - 1) - (matrixSize.x - 1) / 2) * spacing,
            (Math.random() * (matrixSize.y - 1) - (matrixSize.y - 1) / 2) * spacing,
            (Math.random() * (matrixSize.z - 1) - (matrixSize.z - 1) / 2) * spacing
        )
    }));

    return (
        <Stack spacing={3} direction={'column'} justifyContent={'center'} alignItems={'center'} width={'100%'}>
            <MUIBox component={'div'} width={'100%'} height={'85vh'}>
                <Canvas camera={{ position: [0, 0, 5] }}>
                    <OrbitControls
                        enablePan={true}
                        maxPolarAngle={Math.PI / 2}
                    />
                    <ambientLight intensity={0.5} />
                    <pointLight position={[10, 10, 10]} />
                    <PlayingPitch length={matrixSize.x} width={matrixSize.y} height={matrixSize.z} color={0xffffff} />
                    {playerPositions.map((player, index) => (
                        <PlayerSphere
                            key={index}
                            color={player.color}
                            position={player.position}
                            target={player.target}
                            speed={speed}
                        />
                    ))}
                </Canvas>
            </MUIBox>
            {Array.from({ length: playerCount }).map((_, index) => (
                <Button
                    key={index}
                    onClick={() => { setSelectedPlayer(index) }}
                    variant={'contained'}
                >
                    {index}
                </Button>
            ))}
            <Button onClick={() => { setSelectedPlayer(null) }} variant={'contained'}>
                Clear
            </Button>
        </Stack>
    );
};

// ----------------------------------------------------------------------

type PlayerSphereProps = {
    color: number;
    position: THREE.Vector3;
    target: THREE.Vector3;
    speed: number;
};

function PlayerSphere({ color, position, target, speed }: PlayerSphereProps) {
    const ref = useRef<THREE.Mesh>(null!);

    useFrame(() => {
        ref.current.position.lerp(target, speed);
        if (ref.current.position.distanceTo(target) < 0.1) {
            target.set(
                (Math.random() * (matrixSize.x - 1) - (matrixSize.x - 1) / 2) * spacing,
                (Math.random() * (matrixSize.y - 1) - (matrixSize.y - 1) / 2) * spacing,
                (Math.random() * (matrixSize.z - 1) - (matrixSize.z - 1) / 2) * spacing,
            );
        }
    });

    return (
        <mesh ref={ref} position={position}>
            <sphereGeometry args={[0.20, 164, 164]} />
            <meshBasicMaterial color={color} />
        </mesh>
    );
};

// ----------------------------------------------------------------------

type PlayingPitchProps = {
    length: number;
    width: number;
    height: number;
    color: number;
};

function PlayingPitch({ length, width, height, color }: PlayingPitchProps) {
    // Create a group to hold all parts of the pitch
    const pitchGroup = new THREE.Group();

    // Create the main body of the prism with rectangular top and bottom
    const bodyGeometry = new THREE.BoxGeometry(length * spacing, height * spacing, width * spacing);
    const bodyMaterial = new THREE.MeshBasicMaterial({ color: color, transparent: true, opacity: 0.1, side: THREE.DoubleSide });
    const bodyMesh = new THREE.Mesh(bodyGeometry, bodyMaterial);
    pitchGroup.add(bodyMesh);

    // Create the flat green bottom
    const bottomGeometry = new THREE.BoxGeometry(length, 0.1, width);
    const bottomMaterial = new THREE.MeshBasicMaterial({ color: 0x008000 }); // Green color
    const bottomMesh = new THREE.Mesh(bottomGeometry, bottomMaterial);
    bottomMesh.position.set(0, -(height / 2), 0);
    pitchGroup.add(bottomMesh);

    // Return the group
    return <primitive object={pitchGroup} />;
}
  