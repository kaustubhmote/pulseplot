import { loadStored } from "./history.js";
import { bindEvents } from "./events.js";
import { renderAll } from "./render.js";

loadStored();
bindEvents();
renderAll();
