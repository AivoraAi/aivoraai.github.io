/* ============================================================
   AIVORA AI — chatbot.js
   Floating AI Chatbot Widget
   Uses OpenAI API (gpt-3.5-turbo) via direct fetch
   Works on GitHub Pages (client-side only)
   ============================================================ */

(function () {
  'use strict';

  /* ── CONFIGURATION ── */
  const CONFIG = {    
    apiKey: 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
    model: 'gpt-3.5-turbo',
    maxTokens: 500,
    siteContext: `You are the Aivora AI assistant — a helpful, knowledgeable guide for the Aivora AI website (aivoraai.github.io). 
    Your job is to help visitors:
    1. Find the best AI tools for their needs in 2026
    2. Understand how to earn money online with AI and affiliate marketing
    3. Learn how to use AI for writing, video, SEO, automation
    4. Navigate the Aivora AI blog and tool directory
    Be concise, friendly, and professional. Keep answers under 150 words.
    Always suggest relevant pages: product.html for tools, blog.html for guides, contact.html for inquiries.
    If asked about pricing or specific tool details, direct them to the tools directory.`,
    welcomeMessage: "Hi 👋 Welcome to Aivora AI! Ask me about the best AI tools to earn online.",
    botName: 'Aivora AI',
    botAvatar: '🤖',
  };

  /* ── INJECT CSS ── */
  const style = document.createElement('style');
  style.textContent = `
    /* Chatbot Widget Styles */
    #aivora-chat-widget {
      position: fixed;
      bottom: 28px;
      right: 28px;
      z-index: 99999;
      font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Floating Button */
    #aivora-chat-btn {
      width: 58px;
      height: 58px;
      border-radius: 50%;
      background: linear-gradient(135deg, #4f8eff, #8b5cf6);
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 24px rgba(79, 142, 255, 0.45);
      transition: all 0.28s cubic-bezier(.4,0,.2,1);
      position: relative;
      margin-left: auto;
    }
    #aivora-chat-btn:hover {
      transform: scale(1.08);
      box-shadow: 0 8px 32px rgba(79, 142, 255, 0.6);
    }
    #aivora-chat-btn svg {
      width: 26px;
      height: 26px;
      fill: #fff;
      transition: all 0.25s ease;
    }
    #aivora-chat-btn.open svg.icon-chat { display: none; }
    #aivora-chat-btn:not(.open) svg.icon-close { display: none; }

    /* Notification dot */
    .chat-notif-dot {
      position: absolute;
      top: 4px;
      right: 4px;
      width: 12px;
      height: 12px;
      background: #10b981;
      border-radius: 50%;
      border: 2px solid #07090f;
      animation: notifPulse 2s infinite;
    }
    @keyframes notifPulse {
      0%, 100% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.15); opacity: 0.8; }
    }

    /* Unread badge */
    .chat-badge {
      position: absolute;
      top: -4px;
      right: -4px;
      background: #ef4444;
      color: #fff;
      font-size: 11px;
      font-weight: 700;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 2px solid #07090f;
    }
    .chat-badge.hidden { display: none; }

    /* Chat Window */
    #aivora-chat-window {
      position: absolute;
      bottom: 72px;
      right: 0;
      width: 360px;
      height: 520px;
      background: #0d111d;
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 18px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      box-shadow: 0 24px 64px rgba(0,0,0,0.6), 0 0 0 1px rgba(79,142,255,0.1);
      transform: scale(0.9) translateY(12px);
      opacity: 0;
      pointer-events: none;
      transition: all 0.28s cubic-bezier(.4,0,.2,1);
      transform-origin: bottom right;
    }
    #aivora-chat-window.open {
      transform: scale(1) translateY(0);
      opacity: 1;
      pointer-events: all;
    }

    /* Header */
    .chat-header {
      background: linear-gradient(135deg, rgba(79,142,255,0.15), rgba(139,92,246,0.15));
      border-bottom: 1px solid rgba(255,255,255,0.07);
      padding: 16px 18px;
      display: flex;
      align-items: center;
      gap: 12px;
      flex-shrink: 0;
    }
    .chat-header-avatar {
      width: 38px;
      height: 38px;
      border-radius: 50%;
      background: linear-gradient(135deg, #4f8eff, #8b5cf6);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      flex-shrink: 0;
    }
    .chat-header-info { flex: 1 }
    .chat-header-name {
      font-size: 0.94rem;
      font-weight: 700;
      color: #eef2ff;
      font-family: 'Syne', 'DM Sans', sans-serif;
      display: block;
    }
    .chat-header-status {
      font-size: 0.74rem;
      color: #10b981;
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .chat-header-status::before {
      content: '';
      width: 6px;
      height: 6px;
      background: #10b981;
      border-radius: 50%;
    }
    .chat-close-btn {
      background: rgba(255,255,255,0.08);
      border: none;
      border-radius: 8px;
      padding: 6px 8px;
      cursor: pointer;
      color: #8b97b5;
      font-size: 18px;
      line-height: 1;
      transition: all 0.2s;
    }
    .chat-close-btn:hover { background: rgba(255,255,255,0.14); color: #eef2ff; }

    /* Messages area */
    .chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      scrollbar-width: thin;
      scrollbar-color: rgba(255,255,255,0.1) transparent;
    }
    .chat-messages::-webkit-scrollbar { width: 4px; }
    .chat-messages::-webkit-scrollbar-track { background: transparent; }
    .chat-messages::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }

    /* Message bubbles */
    .chat-msg {
      display: flex;
      gap: 8px;
      align-items: flex-end;
      animation: msgSlide 0.25s ease;
    }
    @keyframes msgSlide {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .chat-msg.user { flex-direction: row-reverse; }
    .msg-avatar {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      flex-shrink: 0;
    }
    .msg-avatar.bot { background: linear-gradient(135deg, #4f8eff, #8b5cf6); }
    .msg-avatar.user { background: linear-gradient(135deg, #10b981, #059669); color: #fff; font-size: 12px; font-weight: 700; }
    .msg-bubble {
      max-width: 78%;
      padding: 10px 14px;
      border-radius: 16px;
      font-size: 0.87rem;
      line-height: 1.6;
    }
    .chat-msg.bot .msg-bubble {
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.08);
      color: #c8d0e7;
      border-bottom-left-radius: 4px;
    }
    .chat-msg.user .msg-bubble {
      background: linear-gradient(135deg, rgba(79,142,255,0.25), rgba(139,92,246,0.2));
      border: 1px solid rgba(79,142,255,0.2);
      color: #eef2ff;
      border-bottom-right-radius: 4px;
    }
    .msg-bubble a { color: #4f8eff; text-decoration: underline; }
    .msg-time {
      font-size: 0.66rem;
      color: rgba(139, 151, 181, 0.5);
      margin-top: 3px;
      text-align: right;
    }
    .chat-msg.user .msg-time { text-align: right; }

    /* Typing indicator */
    .typing-indicator {
      display: flex;
      gap: 4px;
      padding: 12px 14px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 16px;
      border-bottom-left-radius: 4px;
      width: fit-content;
    }
    .typing-dot {
      width: 7px;
      height: 7px;
      background: #8b97b5;
      border-radius: 50%;
      animation: typingBounce 1.2s infinite;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typingBounce {
      0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
      30% { transform: translateY(-6px); opacity: 1; }
    }

    /* Quick replies */
    .quick-replies {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      padding: 0 16px 8px;
      flex-shrink: 0;
    }
    .qr-btn {
      padding: 6px 12px;
      background: rgba(79,142,255,0.1);
      border: 1px solid rgba(79,142,255,0.22);
      border-radius: 100px;
      color: #4f8eff;
      font-size: 0.76rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      white-space: nowrap;
    }
    .qr-btn:hover {
      background: rgba(79,142,255,0.2);
      border-color: rgba(79,142,255,0.4);
    }

    /* Input area */
    .chat-input-area {
      padding: 12px 14px;
      border-top: 1px solid rgba(255,255,255,0.07);
      display: flex;
      gap: 9px;
      align-items: flex-end;
      background: rgba(0,0,0,0.2);
      flex-shrink: 0;
    }
    .chat-input {
      flex: 1;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 12px;
      padding: 10px 14px;
      color: #eef2ff;
      font-family: inherit;
      font-size: 0.88rem;
      resize: none;
      outline: none;
      max-height: 90px;
      min-height: 40px;
      line-height: 1.5;
      transition: border-color 0.2s;
    }
    .chat-input:focus { border-color: rgba(79,142,255,0.4); }
    .chat-input::placeholder { color: rgba(139,151,181,0.5); }
    .chat-send-btn {
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: linear-gradient(135deg, #4f8eff, #8b5cf6);
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      transition: all 0.2s;
    }
    .chat-send-btn:hover { opacity: 0.9; transform: scale(1.05); }
    .chat-send-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
    .chat-send-btn svg { width: 16px; height: 16px; fill: #fff; }

    /* Powered by footer */
    .chat-powered {
      text-align: center;
      padding: 6px 0 8px;
      font-size: 0.68rem;
      color: rgba(139,151,181,0.4);
      flex-shrink: 0;
    }
    .chat-powered a { color: rgba(79,142,255,0.6); text-decoration: none; }

    /* Mobile responsive */
    @media (max-width: 480px) {
      #aivora-chat-widget { bottom: 16px; right: 16px; }
      #aivora-chat-window { width: calc(100vw - 32px); right: 0; bottom: 68px; }
    }
  `;
  document.head.appendChild(style);

  /* ── BUILD HTML ── */
  const widget = document.createElement('div');
  widget.id = 'aivora-chat-widget';
  widget.innerHTML = `
    <div id="aivora-chat-window">
      <!-- Header -->
      <div class="chat-header">
        <div class="chat-header-avatar">🤖</div>
        <div class="chat-header-info">
          <span class="chat-header-name">Aivora AI Assistant</span>
          <span class="chat-header-status">Online — Ready to help</span>
        </div>
        <button class="chat-close-btn" id="chat-close-btn" aria-label="Close chat">✕</button>
      </div>

      <!-- Messages -->
      <div class="chat-messages" id="chat-messages"></div>

      <!-- Quick Replies -->
      <div class="quick-replies" id="quick-replies">
        <button class="qr-btn" onclick="aivoraChatSend('Best AI tools to earn money?')">💰 Earn with AI</button>
        <button class="qr-btn" onclick="aivoraChatSend('Free AI tools for beginners?')">🆓 Free tools</button>
        <button class="qr-btn" onclick="aivoraChatSend('Best AI writing tools 2026?')">✍️ Writing AI</button>
        <button class="qr-btn" onclick="aivoraChatSend('How to start AI affiliate marketing?')">📈 Affiliate tips</button>
      </div>

      <!-- Input -->
      <div class="chat-input-area">
        <textarea
          class="chat-input"
          id="chat-input"
          placeholder="Ask anything about AI tools..."
          rows="1"
          maxlength="500"
        ></textarea>
        <button class="chat-send-btn" id="chat-send-btn" aria-label="Send message">
          <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
        </button>
      </div>

      <div class="chat-powered">Powered by <a href="/" target="_blank">Aivora AI</a></div>
    </div>

    <!-- Floating Button -->
    <button id="aivora-chat-btn" aria-label="Open AI chat assistant">
      <span class="chat-notif-dot"></span>
      <span class="chat-badge hidden" id="chat-badge">1</span>

      <!-- Chat icon -->
      <svg class="icon-chat" viewBox="0 0 24 24">
        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
      </svg>

      <!-- Close icon -->
      <svg class="icon-close" viewBox="0 0 24 24">
        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
      </svg>
    </button>
  `;
  document.body.appendChild(widget);

  /* ── STATE ── */
  let isOpen = false;
  let isLoading = false;
  let messageHistory = [
    { role: 'system', content: CONFIG.siteContext }
  ];
  let hasShownWelcome = false;

  /* ── ELEMENTS ── */
  const btn         = document.getElementById('aivora-chat-btn');
  const win         = document.getElementById('aivora-chat-window');
  const messagesEl  = document.getElementById('chat-messages');
  const inputEl     = document.getElementById('chat-input');
  const sendBtn     = document.getElementById('chat-send-btn');
  const closeBtn    = document.getElementById('chat-close-btn');
  const badge       = document.getElementById('chat-badge');
  const qrWrap      = document.getElementById('quick-replies');

  /* ── HELPERS ── */
  function getTime() {
    return new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
  }

  function addMessage(text, role = 'bot') {
    const wrap = document.createElement('div');
    wrap.className = `chat-msg ${role}`;

    const avatar = document.createElement('div');
    avatar.className = `msg-avatar ${role}`;
    avatar.textContent = role === 'bot' ? '🤖' : 'You';

    const inner = document.createElement('div');
    inner.style.display = 'flex';
    inner.style.flexDirection = 'column';
    if (role === 'user') inner.style.alignItems = 'flex-end';

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    // Allow basic HTML in bot messages (links, bold)
    if (role === 'bot') {
      bubble.innerHTML = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
    } else {
      bubble.textContent = text;
    }

    const time = document.createElement('div');
    time.className = 'msg-time';
    time.textContent = getTime();

    inner.appendChild(bubble);
    inner.appendChild(time);
    wrap.appendChild(avatar);
    wrap.appendChild(inner);
    messagesEl.appendChild(wrap);
    scrollToBottom();
    return bubble;
  }

  function addTypingIndicator() {
    const wrap = document.createElement('div');
    wrap.className = 'chat-msg bot';
    wrap.id = 'typing-indicator';

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar bot';
    avatar.textContent = '🤖';

    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

    wrap.appendChild(avatar);
    wrap.appendChild(indicator);
    messagesEl.appendChild(wrap);
    scrollToBottom();
  }

  function removeTypingIndicator() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
  }

  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function showBadge() {
    badge.classList.remove('hidden');
    badge.textContent = '1';
  }
  function hideBadge() {
    badge.classList.add('hidden');
  }

  function setLoading(state) {
    isLoading = state;
    sendBtn.disabled = state;
    inputEl.disabled = state;
  }

  /* ── OPEN / CLOSE ── */
  function openChat() {
    isOpen = true;
    btn.classList.add('open');
    win.classList.add('open');
    hideBadge();

    if (!hasShownWelcome) {
      hasShownWelcome = true;
      setTimeout(() => {
        addMessage(CONFIG.welcomeMessage, 'bot');
      }, 300);
    }
    setTimeout(() => inputEl.focus(), 350);
  }

  function closeChat() {
    isOpen = false;
    btn.classList.remove('open');
    win.classList.remove('open');
  }

  btn.addEventListener('click', () => isOpen ? closeChat() : openChat());
  closeBtn.addEventListener('click', closeChat);

  // Show badge after 3s to draw attention
  setTimeout(() => {
    if (!isOpen) showBadge();
  }, 3000);

  /* ── SEND MESSAGE ── */
  async function sendMessage(text) {
    if (!text.trim() || isLoading) return;

    // Hide quick replies after first message
    qrWrap.style.display = 'none';

    addMessage(text, 'user');
    messageHistory.push({ role: 'user', content: text });

    setLoading(true);
    addTypingIndicator();

    try {
      if (CONFIG.apiKey === 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 || !CONFIG.apiKey) {
        // Demo mode — smart fallback responses
        await new Promise(r => setTimeout(r, 1200));
        removeTypingIndicator();

        const fallbacks = getFallbackResponse(text);
        addMessage(fallbacks, 'bot');
        messageHistory.push({ role: 'assistant', content: fallbacks });
      } else {
        // Real OpenAI API call
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${CONFIG.apiKey}`
          },
          body: JSON.stringify({
            model: CONFIG.model,
            messages: messageHistory,
            max_tokens: CONFIG.maxTokens,
            temperature: 0.7
          })
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        const reply = data.choices[0].message.content.trim();

        removeTypingIndicator();
        addMessage(reply, 'bot');
        messageHistory.push({ role: 'assistant', content: reply });
      }
    } catch (error) {
      removeTypingIndicator();
      addMessage("Sorry, I'm having a quick glitch! 😅 Please try again or [contact us](contact.html) directly — we reply within 24 hours.", 'bot');
      console.error('[Aivora Chatbot]', error);
    } finally {
      setLoading(false);
    }
  }

  /* ── FALLBACK RESPONSES (demo mode) ── */
  function getFallbackResponse(text) {
    const t = text.toLowerCase();

    if (t.includes('earn') || t.includes('money') || t.includes('affiliate')) {
      return "Great question! 💰 The fastest way to earn with AI in 2026 is through **affiliate marketing**. Tools like RankGenius (35% commission) and NeuralFlow (30% commission) pay recurring monthly income. Check our [Affiliate Marketing Guide](blog-ai-affiliate-marketing.html) to get started — some affiliates earn $2,000+/month.";
    }
    if (t.includes('free') || t.includes('beginner') || t.includes('start')) {
      return "For beginners, start with these **free AI tools**: ✍️ **ScribeAI** (writing), 🎨 **PixelMind** (design), 📚 **ScholarAI** (research), 🧩 **CodePilot** (coding). All have free plans — no credit card needed. Read the [Beginners Guide](blog-ai-tools-beginners.html) for a full walkthrough!";
    }
    if (t.includes('writ') || t.includes('blog') || t.includes('content')) {
      return "For AI writing in 2026, **ScribeAI** is our top pick — it's free and writes SEO blog posts, emails, and social media copy in 25+ languages. Also check **MailMind** for email sequences. See the full [AI Writing Tools Guide](blog-ai-writing-tools.html) for rankings and pricing.";
    }
    if (t.includes('seo') || t.includes('rank') || t.includes('google')) {
      return "For SEO in 2026, **RankGenius** is the #1 tool — it handles keyword research, content scoring, and SERP tracking automatically. It pays 35% recurring affiliate commissions too! Read our [AI SEO Guide](blog-ai-seo-2025.html) to learn how Google's AI search changed the rules.";
    }
    if (t.includes('video') || t.includes('youtube') || t.includes('clip')) {
      return "🎬 For AI video tools, **ClipGenius** is trending — it repurposes long videos into viral short clips automatically. **VoiceCraft** is great for AI voiceovers in 40+ languages. Both have affiliate programs paying 25-30% commission. Browse all video tools at the [Tools Directory](product.html).";
    }
    if (t.includes('chatbot') || t.includes('customer') || t.includes('support')) {
      return "For AI chatbots, **ChatSphere** is our recommended tool — it trains on your own business data and handles 70-80% of customer queries automatically. Free plan available! Check the [Tools Directory](product.html) for full pricing and features.";
    }
    if (t.includes('hello') || t.includes('hi') || t.includes('hey')) {
      return "Hello! 👋 I'm the Aivora AI assistant. I can help you find the best AI tools, learn about affiliate marketing, and discover how to earn money online with AI in 2026. What would you like to know?";
    }
    if (t.includes('contact') || t.includes('email') || t.includes('varun')) {
      return "You can reach the Aivora AI team at **Aivoraai@outlook.com** or visit the [Contact page](contact.html). Director Varun Lalwani typically replies within 24 hours. For tool listings and partnerships, mention your interest in the message!";
    }
    if (t.includes('price') || t.includes('cost') || t.includes('paid')) {
      return "Most tools on Aivora AI have **free plans** to start. Paid plans range from $15–$49/month for premium features. We mark each tool as Free 🟢, Freemium 🟡, or Paid 🔵. Browse the full [Tools Directory](product.html) with price filters to find what fits your budget.";
    }
    // Default
    return "Great question! 🤖 Aivora AI covers 200+ curated AI tools for writing, video, SEO, automation, and earning money online. \n\n📚 **Quick links:**\n- [Browse AI Tools](product.html)\n- [Read Blog Guides](blog.html)\n- [Affiliate Marketing Guide](blog-ai-affiliate-marketing.html)\n\nWhat specific AI task can I help with?";
  }

  /* ── GLOBAL FUNCTION for quick replies ── */
  window.aivoraChatSend = function(text) {
    if (!isOpen) openChat();
    inputEl.value = text;
    setTimeout(() => sendMessage(text), 400);
    inputEl.value = '';
  };

  /* ── INPUT EVENTS ── */
  sendBtn.addEventListener('click', () => {
    const text = inputEl.value.trim();
    if (text) { sendMessage(text); inputEl.value = ''; inputEl.style.height = 'auto'; }
  });

  inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const text = inputEl.value.trim();
      if (text) { sendMessage(text); inputEl.value = ''; inputEl.style.height = 'auto'; }
    }
  });

  // Auto-resize textarea
  inputEl.addEventListener('input', () => {
    inputEl.style.height = 'auto';
    inputEl.style.height = Math.min(inputEl.scrollHeight, 90) + 'px';
  });

  console.log('[Aivora AI] Chatbot widget loaded successfully.');

})();
