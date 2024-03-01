// routes
import { PATH_PAGE } from './routes/paths';

// API
// ----------------------------------------------------------------------

export const HOST_API = '';

export const MAIN_API = {
  web_socket_url: "ws://127.0.0.1:8000/game/",
  // web_socket_url: "wss://nftybot.django.nftyarcade.io/chat/",
  base_url: "http://localhost:8080/",
  // base_url: "http://192.168.1.226:8080/",
  // base_url: "https://asoiaf-decks.com:8080/",
  asset_url_base: "https://assets.asoiaf-decks.com/",
};

// ROOT PATH AFTER LOGIN SUCCESSFUL
// ----------------------------------------------------------------------
export const PATH_AFTER_LOGIN = PATH_PAGE.home;
export const NAVBAR = {
  BASE_HEIGHT: 64,
};
export const DEFAULT_BG_IMG = `linear-gradient(rgba(0, 0, 0, 0.40), rgba(0, 0, 0, 0.40)), url("${MAIN_API.asset_url_base}additional-assets/bg_stone-floor.png")`;
export const LANDING_BG_IMG = `linear-gradient(rgba(0, 0, 0, 0.40), rgba(0, 0, 0, 0.75)), url("https://media.harrypotterfanzone.com/the-quidditch-pitch.jpg")`;