<template>
  <div class="chat-page">

    <!-- Top Bar -->
    <header class="topbar">

      <button class="back-button" @click="goBack">
        ← Back to book
      </button>

      <div class="book-title">
        <span>📖</span>
        <strong>{{ book.title }}</strong>
      </div>

      <button class="new-chat-button" @click="newChat" :disabled="loading || sending">
        + New Chat
      </button>

    </header>


    <!-- Main Chat Layout -->
    <main class="chat-layout">

      <!-- Chat History -->
      <aside class="chat-history">

        <div class="history-header">
          <h2>Chat History</h2>

          <button @click="newChat" :disabled="loading || sending">
            +
          </button>
        </div>


        <div class="history-list">

          <div
            v-for="chat in chatHistory"
            :key="chat.id"
            class="history-item"
            :class="{ active: chat.id === activeChatId }"
            @click="selectChat(chat.id)"
          >

            <div class="chat-icon">
              💬
            </div>

            <div class="history-info">

              <h3>
                {{ chat.title }}
              </h3>

              <p>
                {{ chat.lastMessage }}
              </p>

              <span>
                {{ chat.updated }}
              </span>

            </div>

          </div>

        </div>

      </aside>


      <!-- Current Chat -->
      <section class="conversation">

        <!-- Conversation Header -->
        <div class="conversation-header">

          <div>

            <h1>
              {{ activeChat.title }}
            </h1>

            <p>
              Ask anything about {{ book.title }}
            </p>

          </div>

          <button class="menu-button">
            ⋮
          </button>

        </div>


        <!-- Messages -->
        <div class="messages">
          <p v-if="loading">Loading conversations...</p>
          <p v-if="error" role="alert" style="color:#b91c1c">{{ error }}</p>
          <p v-if="sending">ReadMate is thinking...</p>

          <div
            v-for="message in activeChat.messages"
            :key="message.id"
            class="message-row"
            :class="message.role"
          >

            <div
              v-if="message.role === 'assistant'"
              class="ai-avatar"
            >
              ✨
            </div>


            <div class="message-content">

              <span class="message-name">
                {{
                  message.role === 'user'
                    ? 'You'
                    : 'ReadMate AI'
                }}
              </span>

              <div class="message-bubble">

                <p>
                  {{ message.content }}
                </p>

              </div>

            </div>

          </div>

        </div>


        <!-- Input -->
        <div class="input-area">

          <div class="input-wrapper">

            <textarea
              v-model="messageInput"
              placeholder="Ask something about this book..."
              rows="1"
              @keydown.enter.exact.prevent="sendMessage"
            ></textarea>

            <button
              class="send-button"
              @click="sendMessage"
              :disabled="!messageInput.trim() || sending || loading || !activeChatId"
            >
              ➤
            </button>

          </div>

          <p class="input-hint">
            ReadMate AI answers using the context of this book.
          </p>

        </div>

      </section>

    </main>

  </div>
</template>


<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getBook, getReadingProgress, getBookChats, createChat,
  getChatMessages, sendChatMessage
} from '../services/api'

const route = useRoute()
const router = useRouter()
const book = ref({ title: 'Your book' })
const chatHistory = ref([])
const activeChatId = ref(null)
const messageInput = ref('')
const loading = ref(false)
const sending = ref(false)
const error = ref('')
const currentChapter = ref(1)
const activeChat = computed(() => chatHistory.value.find(c => c.id === activeChatId.value) || { title: 'New conversation', messages: [] })

function formatDate(value) {
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '' : date.toLocaleDateString()
}
function normalizeChat(chat) {
  return {
    ...chat,
    title: chat.title || 'New chat',
    lastMessage: '',
    updated: formatDate(chat.updated_at),
    messages: []
  }
}
async function loadChats() {
  loading.value = true
  error.value = ''
  try {
    chatHistory.value = (await getBookChats(route.params.id)).map(normalizeChat)
    if (chatHistory.value.length) await selectChat(chatHistory.value[0].id)
    else await newChat()
  } catch (err) {
    error.value = err.message || 'Could not load conversations.'
  } finally {
    loading.value = false
  }
}
async function selectChat(id) {
  if (sending.value) return
  error.value = ''
  try {
    const messages = await getChatMessages(id)
    const chat = chatHistory.value.find(c => c.id === id)
    if (!chat) return
    chat.messages = messages
    chat.lastMessage = messages.at(-1)?.content || ''
    activeChatId.value = id
  } catch (err) {
    error.value = err.message || 'Could not open this conversation.'
  }
}
async function newChat() {
  if (sending.value) return
  error.value = ''
  try {
    const chat = normalizeChat(await createChat(route.params.id))
    chatHistory.value.unshift(chat)
    activeChatId.value = chat.id
  } catch (err) {
    error.value = err.message || 'Could not create a conversation.'
  }
}
async function sendMessage() {
  const text = messageInput.value.trim()
  if (!text || sending.value || !activeChatId.value) return
  sending.value = true
  error.value = ''
  const id = activeChatId.value
  const chat = chatHistory.value.find(c => c.id === id)
  messageInput.value = ''
  try {
    await sendChatMessage(id, text, currentChapter.value)
    const messages = await getChatMessages(id)
    if (chat) {
      chat.messages = messages
      chat.lastMessage = messages.at(-1)?.content || text
      if (chat.title === 'New chat' || chat.title === 'New conversation') chat.title = text.slice(0, 60)
      chat.updated = 'Just now'
    }
  } catch (err) {
    error.value = err.message || 'Could not send message.'
    messageInput.value = text
    // The server may have saved the user message before the AI request failed.
    try { if (chat) chat.messages = await getChatMessages(id) } catch (_) { /* keep prior messages */ }
  } finally {
    sending.value = false
  }
}
function goBack() { router.push(`/book/${route.params.id}`) }
async function initialize() {
  activeChatId.value = null
  chatHistory.value = []
  try {
    const [bookData, progress] = await Promise.all([
      getBook(route.params.id), getReadingProgress(route.params.id)
    ])
    book.value = bookData
    currentChapter.value = Math.max(1, Number(progress.current_chapter) || 1)
  } catch (err) {
    error.value = err.message || 'Could not load book details.'
  }
  await loadChats()
}
onMounted(initialize)
watch(() => route.params.id, initialize)
</script>


<style scoped>

* {
  box-sizing: border-box;
}


.chat-page {
  height: 100vh;

  display: flex;
  flex-direction: column;

  background: #f7f7f7;

  color: #111;
}


/* TOP BAR */

.topbar {

  height: 70px;

  flex-shrink: 0;

  background: white;

  border-bottom: 1px solid #e5e5e5;

  display: flex;

  align-items: center;

  justify-content: space-between;

  padding: 0 30px;

}


.back-button {

  border: none;

  background: transparent;

  cursor: pointer;

  font-size: 14px;

}


.book-title {

  display: flex;

  align-items: center;

  gap: 10px;

}


.new-chat-button {

  border: none;

  background: #111;

  color: white;

  padding: 10px 15px;

  border-radius: 8px;

  cursor: pointer;

}


/* LAYOUT */

.chat-layout {

  flex: 1;

  display: flex;

  min-height: 0;

}


/* HISTORY */

.chat-history {

  width: 300px;

  flex-shrink: 0;

  background: white;

  border-right: 1px solid #e5e5e5;

  padding: 22px 15px;

  overflow-y: auto;

}


.history-header {

  display: flex;

  align-items: center;

  justify-content: space-between;

  padding: 0 8px 18px;

}


.history-header h2 {

  margin: 0;

  font-size: 18px;

}


.history-header button {

  border: none;

  background: #f2f2f2;

  width: 30px;

  height: 30px;

  border-radius: 7px;

  cursor: pointer;

  font-size: 18px;

}


.history-list {

  display: flex;

  flex-direction: column;

  gap: 5px;

}


.history-item {

  display: flex;

  gap: 12px;

  padding: 13px 10px;

  border-radius: 10px;

  cursor: pointer;

}


.history-item:hover {

  background: #f4f4f4;

}


.history-item.active {

  background: #f0f0f0;

}


.chat-icon {

  width: 34px;

  height: 34px;

  flex-shrink: 0;

  background: white;

  border: 1px solid #ddd;

  border-radius: 8px;

  display: flex;

  align-items: center;

  justify-content: center;

}


.history-info {

  min-width: 0;

}


.history-info h3 {

  margin: 0;

  font-size: 14px;

  white-space: nowrap;

  overflow: hidden;

  text-overflow: ellipsis;

}


.history-info p {

  margin: 5px 0;

  color: #777;

  font-size: 12px;

  white-space: nowrap;

  overflow: hidden;

  text-overflow: ellipsis;

}


.history-info span {

  font-size: 11px;

  color: #aaa;

}


/* CONVERSATION */

.conversation {

  flex: 1;

  display: flex;

  flex-direction: column;

  min-width: 0;

}


.conversation-header {

  height: 82px;

  flex-shrink: 0;

  background: white;

  border-bottom: 1px solid #e5e5e5;

  display: flex;

  align-items: center;

  justify-content: space-between;

  padding: 0 35px;

}


.conversation-header h1 {

  margin: 0;

  font-size: 19px;

}


.conversation-header p {

  margin: 5px 0 0;

  color: #888;

  font-size: 13px;

}


.menu-button {

  border: none;

  background: transparent;

  font-size: 24px;

  cursor: pointer;

}


/* MESSAGES */

.messages {

  flex: 1;

  overflow-y: auto;

  padding: 35px;

  display: flex;

  flex-direction: column;

  gap: 25px;

}


.message-row {

  display: flex;

  gap: 12px;

  max-width: 750px;

}


.message-row.user {

  margin-left: auto;

  flex-direction: row-reverse;

}


.ai-avatar {

  width: 36px;

  height: 36px;

  flex-shrink: 0;

  border-radius: 50%;

  background: #111;

  color: white;

  display: flex;

  align-items: center;

  justify-content: center;

}


.message-content {

  max-width: 650px;

}


.message-name {

  display: block;

  font-size: 11px;

  color: #888;

  margin-bottom: 5px;

}


.message-row.user .message-name {

  text-align: right;

}


.message-bubble {

  background: white;

  border: 1px solid #e5e5e5;

  border-radius: 12px;

  padding: 13px 16px;

}


.message-bubble p {

  margin: 0;

  line-height: 1.6;

  font-size: 14px;

}


.message-row.user .message-bubble {

  background: #111;

  color: white;

  border: none;

}


/* INPUT */

.input-area {

  background: white;

  border-top: 1px solid #e5e5e5;

  padding: 18px 30px 14px;

}


.input-wrapper {

  max-width: 850px;

  margin: auto;

  display: flex;

  align-items: flex-end;

  gap: 10px;

  border: 1px solid #ddd;

  border-radius: 13px;

  padding: 8px 8px 8px 15px;

}


textarea {

  flex: 1;

  resize: none;

  border: none;

  outline: none;

  font-family: inherit;

  font-size: 14px;

  padding: 8px 0;

}


.send-button {

  width: 38px;

  height: 38px;

  border: none;

  border-radius: 9px;

  background: #111;

  color: white;

  cursor: pointer;

}


.send-button:disabled {

  opacity: 0.3;

  cursor: default;

}


.input-hint {

  max-width: 850px;

  margin: 8px auto 0;

  color: #aaa;

  font-size: 11px;

}

</style>