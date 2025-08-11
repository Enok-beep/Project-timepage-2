import axios from "axios";

const BASE = process.env.REACT_APP_BACKEND_URL;
const API = `${BASE}/api`;

export const getPalettes = async () => {
  const { data } = await axios.get(`${API}/palettes`);
  return data;
};

export const savePreference = async ({ sessionId, paletteId }) => {
  const { data } = await axios.post(`${API}/preferences`, {
    session_id: sessionId,
    palette_id: paletteId,
  });
  return data; // { session_id, palette_id, updated_at }
};

export const notifyEmail = async (email) => {
  const { data } = await axios.post(`${API}/notify`, { email });
  return data; // { status: "ok" }
};