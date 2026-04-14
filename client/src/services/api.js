import axios from "axios";

const BASE_URL = "/api/ai";

/**
 * Send a chat message to the GPT-4 backend.
 * @param {string} message
 * @param {string} [context]
 * @returns {Promise<string>} reply text
 */
export async function sendChatMessage(message, context = "") {
  const { data } = await axios.post(`${BASE_URL}/chat`, { message, context });
  return data.reply;
}
