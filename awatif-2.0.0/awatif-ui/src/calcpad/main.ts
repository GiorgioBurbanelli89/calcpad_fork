import van from 'vanjs-core';
import { getViewer } from '../viewer/getViewer';
import { getColorMap } from '../color-map/getColorMap';
import { getLegend } from '../color-map/getLegend';
import { Node } from 'awatif-fem';

// Datos FEM - puedes cambiar estos valores
const nodes = van.state([
  [0, 0, 0],
  [5, 0, 0],
  [5, 5, 0],
  [0, 5, 0],
  [2.5, 2.5, 3],
] as Node[]);

const elements = van.state([
  [0, 1, 4],
  [1, 2, 4],
  [2, 3, 4],
  [3, 0, 4],
]);

// Valores para el color map (desplazamientos, esfuerzos, etc.)
const values = van.state([0, 2, 5, 3, 10]);

// Crear viewer
const viewerElm = getViewer({
  mesh: { nodes, elements },
  settingsObj: {
    nodes: true,
    elements: true,
    nodesIndexes: true,
  },
});

document.body.appendChild(viewerElm);

console.log('Awatif Viewer cargado!');
console.log('Nodos:', nodes.val.length);
console.log('Elementos:', elements.val.length);