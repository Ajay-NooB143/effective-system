import { useState } from "react";
import { sendChatMessage } from "../services/api";
import styles from "./ChatBox.module.css";

export default function ChatBox({ context }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSend(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;

    const userMsg = { role: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const reply = await sendChatMessage(text, context);
      setMessages((prev) => [...prev, { role: "ai", text: reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "ai", text: "⚠️ Error reaching AI. Check that the server is running." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.wrapper}>
      <h3 className={styles.heading}>🤖 Ask the Trading Coach</h3>

      <div className={styles.messages}>
        {messages.length === 0 && (
          <p className={styles.placeholder}>
            Ask any trading question related to this stop…
          </p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={m.role === "user" ? styles.userMsg : styles.aiMsg}
          >
            <span className={styles.roleLabel}>
              {m.role === "user" ? "You" : "Coach"}
            </span>
            <p>{m.text}</p>
          </div>
        ))}
        {loading && (
          <div className={styles.aiMsg}>
            <span className={styles.roleLabel}>Coach</span>
            <p className={styles.thinking}>Thinking…</p>
          </div>
        )}
      </div>

      <form onSubmit={handleSend} className={styles.form}>
        <input
          className={styles.input}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. What is an order block?"
          disabled={loading}
        />
        <button className={styles.btn} type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
