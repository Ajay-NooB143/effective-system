const express = require("express");
const { chat } = require("../controllers/aiController");

const router = express.Router();

// POST /api/ai/chat
router.post("/chat", chat);

module.exports = router;
