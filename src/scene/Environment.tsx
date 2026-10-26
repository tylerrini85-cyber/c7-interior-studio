/** Procedural environments (day, sunset, night, showroom): PMREM-lit sky + sun + ground, plus matching scene lights. */
import { useEffect, useMemo } from 'react';
import * as THREE from 'three';
import { useThree } from '@react-three/fiber';
import type { EnvironmentId } from '../project/schema';
import { useStore } from '../state/store';

interface EnvSpec { zenith: string; horizon: string; ground: string; sunColor: string; sunIntensity: number; sunDir: [number, number, number]; ambient: number; hemiSky: string; hemiGround: string; hemi: number; bgBlur: number; exposure: number; envIntensity: number; bgIntensity: number; }

export const ENVIRONMENTS: Record<EnvironmentId, EnvSpec> = {
  day: { zenith: '#2f6fc4', horizon: '#c9dcf0', ground: '#4a4d52', sunColor: '#fff2dc', sunIntensity: 3.0, sunDir: [0.5, 0.8, -0.3], ambient: 0.12, hemiSky: '#9fc0ea', hemiGround: '#3c3835', hemi: 0.35, bgBlur: 0.02, exposure: 0.85, envIntensity: 0.7, bgIntensity: 0.55 },
  sunset: { zenith: '#1f2550', horizon: '#ff8a3c', ground: '#2c2529', sunColor: '#ffa860', sunIntensity: 2.2, sunDir: [-0.9, 0.18, -0.35], ambient: 0.08, hemiSky: '#7a5a8a', hemiGround: '#2c2529', hemi: 0.3, bgBlur: 0.02, exposure: 0.9, envIntensity: 0.7, bgIntensity: 1.0 },
  night: { zenith: '#03040a', horizon: '#0e1220', ground: '#07080b', sunColor: '#aeb8ff', sunIntensity: 0.2, sunDir: [-0.4, 0.7, 0.4], ambient: 0.03, hemiSky: '#141a2c', hemiGround: '#05060a', hemi: 0.15, bgBlur: 0.0, exposure: 1.1, envIntensity: 0.3, bgIntensity: 1.0 },
  showroom: { zenith: '#3a3d44', horizon: '#50545c', ground: '#1e2024', sunColor: '#ffffff', sunIntensity: 1.0, sunDir: [0.3, 0.9, 0.2], ambient: 0.1, hemiSky: '#c9ccd3', hemiGround: '#2a2c31', hemi: 0.35, bgBlur: 0.04, exposure: 1.0, envIntensity: 0.9, bgIntensity: 0.8 },
};

function buildEnvScene(spec: EnvSpec, env: EnvironmentId): THREE.Scene {
  const scene = new THREE.Scene();
  const skyMat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false,
    uniforms: { zenith: { value: new THREE.Color(spec.zenith) }, horizon: { value: new THREE.Color(spec.horizon) }, ground: { value: new THREE.Color(spec.ground) }, sunDir: { value: new THREE.Vector3(...spec.sunDir).normalize() }, sunColor: { value: new THREE.Color(spec.sunColor) }, sunI: { value: spec.sunIntensity } },
    vertexShader: `varying vec3 vDir; void main(){ vDir = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
    fragmentShader: `uniform vec3 zenith, horizon, ground, sunDir, sunColor; uniform float sunI; varying vec3 vDir;
      void main(){ float h = vDir.y; vec3 c = h > 0.0 ? mix(horizon, zenith, pow(h, 0.55)) : mix(horizon, ground, pow(-h, 0.35));
        float s = max(dot(normalize(vDir), sunDir), 0.0); c += sunColor * (pow(s, 600.0) * sunI * 12.0 + pow(s, 8.0) * sunI * 0.25);
        gl_FragColor = vec4(c, 1.0); }`,
  });
  const sky = new THREE.Mesh(new THREE.SphereGeometry(50, 32, 16), skyMat);
  scene.add(sky);
  if (env === 'showroom') {
    // overhead light panels like a studio ceiling for crisp reflections
    for (let i = -2; i <= 2; i++) {
      const panel = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 6), new THREE.MeshBasicMaterial({ color: '#ffffff' }));
      panel.position.set(i * 2.2, 4, 0); panel.rotation.x = Math.PI / 2; scene.add(panel);
    }
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshBasicMaterial({ color: '#34373d' }));
    floor.rotation.x = -Math.PI / 2; floor.position.y = -0.4; scene.add(floor);
  } else if (env === 'night') {
    for (let i = 0; i < 6; i++) {
      const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.25, 8, 8), new THREE.MeshBasicMaterial({ color: '#ffd9a0' }));
      lamp.position.set(Math.cos(i * 1.1) * 14, 4 + (i % 2), Math.sin(i * 1.1) * 14); scene.add(lamp);
    }
  }
  return scene;
}

export function Environment() {
  const { gl, scene } = useThree();
  const env = useStore((s) => s.project?.environment ?? 'showroom');
  const spec = ENVIRONMENTS[env];
  const quality = useStore((s) => s.settings.quality);
  const pmrem = useMemo(() => new THREE.PMREMGenerator(gl), [gl]);

  useEffect(() => {
    const envScene = buildEnvScene(spec, env);
    const target = pmrem.fromScene(envScene, 0.04);
    scene.environment = target.texture;
    scene.background = target.texture;
    scene.backgroundBlurriness = spec.bgBlur;
    scene.environmentIntensity = spec.envIntensity;
    scene.backgroundIntensity = spec.bgIntensity;
    gl.toneMappingExposure = spec.exposure;
    return () => { target.dispose(); };
  }, [spec, env, pmrem, scene, gl]);

  const shadows = quality !== 'mobile';
  const mapSize = quality === 'ultra' ? 2048 : quality === 'high' ? 1024 : 512;
  const sunPos = new THREE.Vector3(...spec.sunDir).normalize().multiplyScalar(6);
  return (
    <>
      <hemisphereLight color={spec.hemiSky} groundColor={spec.hemiGround} intensity={spec.hemi} />
      <ambientLight intensity={spec.ambient * 0.5} />
      <directionalLight position={sunPos.toArray()} intensity={spec.sunIntensity} color={spec.sunColor} castShadow={shadows} shadow-mapSize={[mapSize, mapSize]} shadow-bias={-0.0004} shadow-normalBias={0.02} shadow-camera-near={0.5} shadow-camera-far={14} shadow-camera-left={-2.5} shadow-camera-right={2.5} shadow-camera-top={2.5} shadow-camera-bottom={-2.5} />
      {env === 'showroom' && <>
        <pointLight position={[-0.3, 0.78, -0.25]} intensity={0.22} distance={2.5} decay={2} color="#fff6ea" />
        <pointLight position={[0.3, 0.78, 0.3]} intensity={0.18} distance={2.5} decay={2} color="#fff6ea" />
      </>}
      {env === 'night' && <pointLight position={[0, 1.02, -0.35]} intensity={0.35} distance={2.5} decay={2} color="#ffe0b0" />}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.22, 0]} receiveShadow>
        <planeGeometry args={[40, 40]} />
        <meshStandardMaterial color={spec.ground} roughness={0.95} />
      </mesh>
    </>
  );
}
