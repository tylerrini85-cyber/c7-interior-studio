/** Blender (x, forward, up) -> three.js (x, up, -forward). Layout constants mirrored from tools/blender/layout.py. */
export const b2t = (x: number, y: number, z: number): [number, number, number] => [x, z, -y];

export const DRIVER_EYE: [number, number, number] = b2t(-0.37, -0.12, 0.96);
export const PASSENGER_EYE: [number, number, number] = b2t(0.37, -0.12, 0.96);
export const CABIN_BOUNDS = { minX: -0.62, maxX: 0.62, minY: 0.30, maxY: 1.04, minZ: -0.62, maxZ: 0.56 };
export const SEATBACK_RECLINE = (23 * Math.PI) / 180;
