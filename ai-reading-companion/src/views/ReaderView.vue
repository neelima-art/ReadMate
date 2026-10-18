<template>
  <div class="reader-page">

    <!-- TOP BAR -->
    <header class="reader-header"
    v-show="!controlsHidden">

      <button class="back-button" @click="goBack">
        ←
      </button>

      <div class="book-title">

        <strong>
          {{ book?.title || 'ReadMate' }}
        </strong>

        <!--<span v-if="currentChapterData">
          Chapter {{ currentChapterData.chapter_number }}
        </span>-->

      </div>

<!-- PREDICTIVE AI READING DIFFICULTY -->
<div class="difficulty-indicator">
  <span v-if="difficultyLoading">
    🧠 Analyzing...
  </span>

  <span v-else-if="readingDifficulty">
    🧠 Difficulty:
    <strong>
      {{ readingDifficulty.difficulty }}
    </strong>
  </span>

  <span v-else-if="difficultyError"
        class="difficulty-error">
    {{ difficultyError }}
  </span>
</div>
      
<div class="reader-actions">
  <button
    class="theme-button"
    type="button"
    title="Reading theme"
    aria-label="Reading theme"
  >
    ☀
  </button>

  <button
    class="ai-mode-button"
    type="button"
    @click="toggleChat"
  >
    <span class="ai-sparkle">✦</span>
    <span>AI Companion</span>
  </button>
</div>


    </header>


    <!-- READER WORKSPACE -->

    <main class="workspace">


      <!-- BOOK -->

      <section
        ref="bookPanelRef"
        class="book-panel"
        @scroll="handleReaderScroll"
         @click="toggleReadingControls"
        :style="{
          width: chatOpen
            ? `${100 - chatWidth}%`
            : '100%'
        }"
      >

        <!-- LOADING -->

        <div
          v-if="loading"
          class="loading-message"
        >
          Loading book...
        </div>


        <!-- ERROR -->

        <div
          v-else-if="error"
          class="error-message"
        >
          {{ error }}
        </div>


        <!-- BOOK CONTENT -->

        <div class="reading-area">

          <div class="pdf-reader">

            <div
              v-for="pageNumber in renderedPages"
              :key="pageNumber"
              :ref="el => setPageWrapperRef(el,pageNumber)"
              class="pdf-page-wrapper"
              :data-page="pageNumber"
            >
          
              <div class="page-number">
                Page {{ pageNumber }}
              </div>
          
              <!-- Keep the canvas for visual rendering, with a selectable PDF text layer above it. -->
              <div class="pdf-page-content" :ref="el => setPageContentRef(el, pageNumber)">
                <canvas
                  :ref="el => setCanvasRef(el, pageNumber)"
                  class="pdf-page"
                ></canvas>
                <div
                  :ref="el => setTextLayerRef(el, pageNumber)"
                  class="textLayer pdf-text-layer"
                  aria-label="Selectable PDF text"
                ></div>
              </div>
          
            </div>
          
          </div>
        
        </div>

        <!-- NO CHAPTERS -->

        

      </section>


      <!-- DIVIDER -->

      <div
        v-if="chatOpen"
        class="divider"
        @mousedown="startDragging"
      >

        <div class="divider-handle"></div>

      </div>


      <!-- AI PANEL -->

      <aside
        v-if="chatOpen"
        class="ai-panel"
        :style="{ width: `${chatWidth}%` }"
      >

        <!-- AI HEADER -->

        <div class="ai-header">

          <div>

            <span class="ai-icon">
              🤖
            </span>

            <div>

              <strong>
                ReadMate
              </strong>

              <small>
                Your reading companion
              </small>

            </div>

          </div>


          <button @click="toggleChat">
            ×
          </button>

        </div>

        <!-- SAVED CHATS -->
       <!-- <div class="chat-toolbar">
          <select
            :value="chatId ?? ''"
            aria-label="Saved conversations"
            @change="switchChat(Number($event.target.value))"
          >
            <option
              v-for="chat in chats"
              :key="chat.id"
              :value="chat.id"
            >
              {{ chat.title || 'New chat' }}
            </option>
          </select>

          <button
            class="new-chat-button"
            type="button"
            @click="createNewChat"
            :disabled="chatLoading || sendingMessage"
          >
            + New chat
          </button>
        </div>-->

        <p v-if="chatError" class="chat-error" role="alert">
          {{ chatError }}
        </p>

        <!-- CHAT MESSAGES -->

        <div class="messages" ref="messagesContainerRef">

          <div
            v-for="message in messages"
            :key="message.id"
            class="message"
            :class="
              message.role === 'user'
                ? 'user-message'
                : 'ai-message'
            "
          >

            <div
              v-if="message.role !== 'user'"
              class="message-avatar"
            >
              🤖
            </div>


            <div class="message-content">

              <p>
                {{ message.text }}
              </p>

            </div>

          </div>

        </div>


        <!-- CHAT INPUT -->

        <div class="chat-input">

          <textarea
            v-model="userMessage"
            placeholder="Ask about what you've read..."
            rows="2"
            @keydown.enter.exact.prevent="sendMessage"
          ></textarea>


          <button
            @click="sendMessage"
            :disabled="!userMessage.trim() || sendingMessage || !chatId"
            :title="sendingMessage ? 'ReadMate is thinking…' : 'Send message'"
          >
            {{ sendingMessage ? '…' : '↑' }}
          </button>

        </div>

      </aside>

    </main>

    
<!-- SELECTED TEXT MENU -->
<div
  v-if="selectionMenu.visible"
  class="selection-menu"
  :style="{
    left: `${selectionMenu.x}px`,
    top: `${selectionMenu.y}px`
  }"
  @mousedown.prevent
>
  <button
    type="button"
    @click="explainMeaning"
    :disabled="!selectedText || sendingMessage"
  >
    📖 Meaning
  </button>

  <button
    type="button"
    @click="askAIAboutSelection"
    :disabled="!selectedText"
  >
    🤖 AI
  </button>
</div>


    <!-- BOTTOM READING BAR -->

   
<footer class="reader-footer"
v-show="!controlsHidden">
  <span class="reading-label">
    {{ currentChapterData
      ? `Chapter ${currentChapterData.chapter_number}`
      : 'Reading' }}
  </span>

  <button
    class="chapter-nav-button previous-button"
    type="button"
    :disabled="currentChapter <= 0"
    @click="previousChapter"
  >
    ← Previous
  </button>

  <button
    class="chapter-nav-button next-button"
    type="button"
    :disabled="currentChapter >= chapters.length - 1 || !chapters.length"
    @click="nextChapter"
  >
    Next →
  </button>

  <span class="progress-label">Reading Progress</span>

  <div
    class="footer-progress"
    role="progressbar"
    :aria-valuenow="readingProgress"
    aria-valuemin="0"
    aria-valuemax="100"
  >
    <div
      class="footer-progress-fill"
      :style="{ width: `${readingProgress}%` }"
    ></div>
  </div>

  <span class="progress-percentage">
    {{ readingProgress }}%
  </span>
</footer>


  </div>
</template>


<script setup>

import * as pdfjsLib from 'pdfjs-dist'
import 'pdfjs-dist/web/pdf_viewer.css'
import pdfWorker from 'pdfjs-dist/build/pdf.worker.min.js?url'
pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker

import {
  computed,
  ref,
  shallowRef,
  onMounted,
  onUnmounted,
  nextTick
} from 'vue'

import {
  useRoute,
  useRouter
} from 'vue-router'

import {
  getBook,
  getChapters,
  getReadingProgress,
  saveReadingProgress,
  createChat,
  getBookChats,
  getChatMessages,
  sendChatMessage,
  analyzeBookPage,
  predictDifficulty
} from '../services/api'

const route = useRoute()

const router = useRouter()

const pdfUrl = computed(() => {
  return `/api/books/${route.params.id}/file`
})

const renderedPages = ref([])

const canvasRefs = {}
const textLayerRefs = {}
const pageContentRefs = {}

const pdfDocument = shallowRef(null)

// Predictive AI state
const readingDifficulty = ref(null)
const difficultyLoading = ref(false)
const difficultyError = ref('')
const predictedPages = new Map()
let difficultyRequestId = 0

const pageTextCache = new Map()

async function predictCurrentPage(pageNumber) {
  const requestId = ++difficultyRequestId

  readingDifficulty.value = null
  difficultyError.value = ''

  if (predictedPages.has(pageNumber)) {
    readingDifficulty.value = predictedPages.get(pageNumber)
    difficultyLoading.value = false
    return
  }

  if (!pdfDocument.value) return

  difficultyLoading.value = true

  try {
    let text = pageTextCache.get(pageNumber)

    if (text === undefined) {
      const page = await pdfDocument.value.getPage(pageNumber)
      const content = await page.getTextContent()

      text = content.items
        .map(item => item.str || '')
        .join(' ')
        .trim()

      pageTextCache.set(pageNumber, text)
    }

    if (requestId !== difficultyRequestId) return

    if (!text || text.length < 30) {
      difficultyError.value = 'Not enough text to predict difficulty'
      return
    }

    const result = await predictDifficulty(text)

    predictedPages.set(pageNumber, result)

    if (requestId === difficultyRequestId) {
      readingDifficulty.value = result
    }
  } catch (error) {
    if (requestId === difficultyRequestId) {
      difficultyError.value = error.message
      console.warn('Difficulty prediction failed:', error)
    }
  } finally {
    if (requestId === difficultyRequestId) {
      difficultyLoading.value = false
    }
  }
}

async function analyzeReadingDifficulty(pageNumber, text) {
  const cleanText = text.trim()
  if (!cleanText) return

  const requestId = ++difficultyRequestId

  if (predictedPages.has(pageNumber)) {
    readingDifficulty.value = predictedPages.get(pageNumber)
    difficultyLoading.value = false
    difficultyError.value = ''
    return
  }

  difficultyLoading.value = true
  difficultyError.value = ''

  try {
    const result = await predictDifficulty(cleanText)

    predictedPages.set(pageNumber, result)

    if (requestId === difficultyRequestId) {
      readingDifficulty.value = result
    }
  } catch (error) {
    if (requestId === difficultyRequestId) {
      difficultyError.value = error.message
      console.warn('Difficulty prediction failed:', error)
    }
  } finally {
    if (requestId === difficultyRequestId) {
      difficultyLoading.value = false
    }
  }
}
/* =========================
   BOOK
========================= */

const book = ref(null)

const bookPanelRef = ref(null)

const pageWrapperRefs = {}
const renderedPageSet = new Set()
const renderingPages = new Map()

let pageObserver = null
let progressSaveTimer = null
// Analyze only pages the reader has reached; avoid parallel AI requests.

const analysisQueue = []
const queuedAnalysisPages = new Set()

let analysisRunning = false
let readerActive = true

// Capture the book ID when the reader is opened.
const readerBookId = String(route.params.id || '')

async function queueCharacterAnalysis(pageNumber) {
  const n = Number(pageNumber)

  if (!readerActive || !readerBookId) return

  if (
    !Number.isInteger(n) ||
    n < 1 ||
    (totalPages.value && n > totalPages.value)
  ) {
    return
  }

  if (queuedAnalysisPages.has(n)) return

  queuedAnalysisPages.add(n)
  analysisQueue.push(n)

  if (analysisRunning) return

  analysisRunning = true

  try {
    while (analysisQueue.length && readerActive) {
      const page = analysisQueue.shift()

      if (!readerActive) break

      try {
        await analyzeBookPage(readerBookId, page)
      } catch (error) {
        if (readerActive) {
          console.warn(
            `Character analysis failed on page ${page}:`,
            error
          )
        }
      }
    }
  } finally {
    analysisRunning = false
  }
}


const currentPage = ref(1)
const totalPages = ref(0)
/* =========================
   CHAPTERS
========================= */

const chapters = ref([])

const currentChapter = ref(0)

const loading = ref(true)

const error = ref('')


const currentChapterData = computed(() => {

  return chapters.value[
    currentChapter.value
  ] || null

})


/* =========================
   PARAGRAPHS
========================= */

const paragraphs = computed(() => {

  if (!currentChapterData.value) {
    return []
  }

  return currentChapterData.value.content
    .split(/\n\s*\n/)
    .map(paragraph => paragraph.trim())
    .filter(paragraph => paragraph.length > 0)

})


/* =========================
   READING PROGRESS
========================= */




const furthestPage = ref(1)

const readingProgress = computed(() => {
  if (!totalPages.value) return 0

  return Math.min(
    100,
    Math.round(
      (Math.min(totalPages.value, Math.max(1, furthestPage.value)) / totalPages.value) * 100
    )
  )
})





let pdfResizeObserver = null
let resizeTimer = null

function setupPdfResizeObserver() {
  pdfResizeObserver?.disconnect()

  const panel = bookPanelRef.value
  if (!panel) return

  pdfResizeObserver = new ResizeObserver(() => {
    clearTimeout(resizeTimer)

    resizeTimer = setTimeout(async () => {
      if (!pdfDocument.value) return

      // Wait until any existing page renders finish.
      await Promise.allSettled(
        [...renderingPages.values()]
      )

      renderedPageSet.clear()

      await nextTick()

      // Re-render pages at the new available width.
      for (const pageNumber of renderedPages.value) {
        const wrapper = pageWrapperRefs[pageNumber]

        if (!wrapper) continue

        const rect = wrapper.getBoundingClientRect()
        const panelRect = panel.getBoundingClientRect()

        // Render visible pages and nearby pages.
        if (
          rect.bottom >= panelRect.top - 800 &&
          rect.top <= panelRect.bottom + 800
        ) {
          await renderPage(pageNumber, true)
        }
      }
    }, 180)
  })

  pdfResizeObserver.observe(panel)
}


/* =========================
   AI PANEL
========================= */

const chatOpen = ref(true)

const chatWidth = ref(50)

const dragging = ref(false)


/* =========================
   CHAT
========================= */

const userMessage = ref('')
const chatId = ref(null)
const chats = ref([])
const chatLoading = ref(false)
const sendingMessage = ref(false)
const chatError = ref('')
const messagesContainerRef = ref(null)


/* =========================
   PDF TEXT SELECTION
========================= */

const selectionMenu = ref({
  visible: false,
  x: 0,
  y: 0
})

const selectedText = ref('')

function handleTextSelection() {
  const selection = window.getSelection()

  if (!selection || selection.isCollapsed) {
    selectionMenu.value.visible = false
    return
  }

  const text = selection.toString().trim()
  if (!text) {
    selectionMenu.value.visible = false
    return
  }

  // Only respond to selections inside the PDF text layer.
  const range = selection.getRangeAt(0)
  const startNode = range.startContainer
  const endNode = range.endContainer

  const startElement =
    startNode.nodeType === Node.ELEMENT_NODE
      ? startNode
      : startNode.parentElement

  const endElement =
    endNode.nodeType === Node.ELEMENT_NODE
      ? endNode
      : endNode.parentElement

  const startLayer = startElement?.closest('.pdf-text-layer')
  const endLayer = endElement?.closest('.pdf-text-layer')

  if (
    !startLayer ||
    !endLayer ||
    startLayer !== endLayer
  ) {
    selectionMenu.value.visible = false
    return
  }

  selectedText.value = text

  const rect = range.getBoundingClientRect()
  const menuWidth = 190
  const menuHeight = 48

  selectionMenu.value = {
    visible: true,
    x: Math.max(
      8,
      Math.min(
        rect.left + rect.width / 2 - menuWidth / 2,
        window.innerWidth - menuWidth - 8
      )
    ),
    y: Math.max(
      8,
      rect.top - menuHeight - 8
    )
  }
}

function hideSelectionMenu(event) {
  if (event?.target?.closest?.('.selection-menu')) {
    return
  }

  selectionMenu.value.visible = false
}

async function explainMeaning() {
  const text = selectedText.value
  if (!text) return

  selectionMenu.value.visible = false

  if (!chatId.value) {
    await createNewChat()
  }

  if (!chatId.value) {
    chatError.value = 'Unable to open a chat to explain this text.'
    return
  }

  // Ask ReadMate to explain the selected text in context.
  userMessage.value =
    `Explain the meaning of this selected text in the context of what I have read so far. Avoid spoilers.\n\nSelected text: "${text}"`

  await sendMessage()
}

function askAIAboutSelection() {
  const text = selectedText.value
  if (!text) return

  selectionMenu.value.visible = false
  chatOpen.value = true

  // Keep the selected passage in the existing chat input
  // so the reader can type their own question.
  userMessage.value =
    `Regarding this selected text: "${text}"\n\nMy question: `

  nextTick(() => {
    const textarea = document.querySelector('.chat-input textarea')
    textarea?.focus()
  })
}


const welcomeMessage = {
  id: 'readmate-welcome',
  role: 'ai',
  text: "Hey! I'm reading along with you. Ask me anything about what you've discovered so far. 📖"
}

const messages = ref([{ ...welcomeMessage }])

function normalizeMessages(items) {
  if (!items.length) {
    return [{ ...welcomeMessage }]
  }

  return items.map(message => ({
    id: message.id,
    role: message.role === 'user' ? 'user' : 'assistant',
    text: message.content
  }))
}

async function scrollMessagesToBottom() {
  await nextTick()
  const container = messagesContainerRef.value
  if (container) {
    container.scrollTop = container.scrollHeight
  }
}

async function loadChatHistory() {
  chatLoading.value = true
  chatError.value = ''

  try {
    chats.value = await getBookChats(route.params.id)

    if (chats.value.length) {
      await openChatSession(chats.value[0].id)
    } else {
      await createNewChat()
    }
  } catch (err) {
    console.error('Failed to load chat history:', err)
    chatError.value = err.message || 'Unable to load chat history.'
  } finally {
    chatLoading.value = false
  }
}

async function createNewChat() {
  chatLoading.value = true
  chatError.value = ''

  try {
    const chat = await createChat(route.params.id)
    chats.value = [chat, ...chats.value.filter(item => item.id !== chat.id)]
    chatId.value = chat.id
    messages.value = [{ ...welcomeMessage }]
    await scrollMessagesToBottom()
  } catch (err) {
    console.error('Failed to create chat:', err)
    chatError.value = err.message || 'Unable to create a new chat.'
  } finally {
    chatLoading.value = false
  }
}

async function openChatSession(id) {
  if (!id) return

  chatLoading.value = true
  chatError.value = ''

  try {
    const savedMessages = await getChatMessages(id)
    chatId.value = id
    messages.value = normalizeMessages(savedMessages)
    await scrollMessagesToBottom()
  } catch (err) {
    console.error('Failed to open chat:', err)
    chatError.value = err.message || 'Unable to open this conversation.'
  } finally {
    chatLoading.value = false
  }
}

async function switchChat(id) {
  if (!id || id === chatId.value) return
  await openChatSession(id)
}


function handleReaderScroll() {
  const panel = bookPanelRef.value
  if (!panel) return

  const panelTop = panel.getBoundingClientRect().top + 80

  let visiblePage = currentPage.value

  const pageNumbers = Object.keys(pageWrapperRefs)
    .map(Number)
    .sort((a, b) => a - b)

  for (const pageNumber of pageNumbers) {
    const wrapper = pageWrapperRefs[pageNumber]
    if (!wrapper) continue

    const rect = wrapper.getBoundingClientRect()

    if (rect.bottom > panelTop) {
      visiblePage = pageNumber
      break
    }
  }

  if (visiblePage === currentPage.value) return

  currentPage.value = visiblePage
  queueCharacterAnalysis(visiblePage)
  predictCurrentPage(visiblePage)
  // Update the visible chapter, even when reading backward.
  const chapterIndex = chapters.value.findIndex(chapter => {
    const start = Number(chapter.start_page)
    const end = Number(chapter.end_page)

    return (
      Number.isFinite(start) &&
      Number.isFinite(end) &&
      visiblePage >= start &&
      visiblePage <= end
    )
  })

  if (chapterIndex >= 0) {
    currentChapter.value = chapterIndex
  }

  // Only advance the saved progress position.
  if (visiblePage > furthestPage.value) {
    furthestPage.value = visiblePage

    clearTimeout(progressSaveTimer)

    progressSaveTimer = setTimeout(() => {
      saveProgress()
    }, 800)
  }
}

function setCanvasRef(element, pageNumber) {
  if (element) {
    canvasRefs[pageNumber] = element
  } else {
    delete canvasRefs[pageNumber]
  }
}

function setTextLayerRef(element, pageNumber) {
  if (element) {
    textLayerRefs[pageNumber] = element
  } else {
    delete textLayerRefs[pageNumber]
  }
}

function setPageContentRef(element, pageNumber) {
  if (element) {
    pageContentRefs[pageNumber] = element
  } else {
    delete pageContentRefs[pageNumber]
  }
}

function setPageWrapperRef(element, pageNumber) {
  if (element) {
    pageWrapperRefs[pageNumber] = element
  } else {
    delete pageWrapperRefs[pageNumber]
  }

  // Observe newly mounted page wrappers.
  if (element && pageObserver) {
    pageObserver.observe(element)
  }
}

async function sendMessage() {
  const text = userMessage.value.trim()

  if (!text || sendingMessage.value || !chatId.value) return

  chatError.value = ''
  userMessage.value = ''
  messages.value.push({
    id: `pending-${Date.now()}`,
    role: 'user',
    text
  })
  sendingMessage.value = true
  await scrollMessagesToBottom()

  try {
    const result = await sendChatMessage(
      chatId.value,
      text,
      currentChapter.value + 1
    )

    // Replace the temporary user bubble with the database message,
    // then append ReadMate's saved response.
    const pendingIndex = messages.value.findIndex(
      message => String(message.id).startsWith('pending-')
        && message.text === text
    )

    const savedUserMessage = {
      id: result.user_message.id,
      role: 'user',
      text: result.user_message.content
    }

    if (pendingIndex >= 0) {
      messages.value.splice(pendingIndex, 1, savedUserMessage)
    }

    messages.value.push({
      id: result.assistant_message.id,
      role: 'assistant',
      text: result.assistant_message.content
    })

    const activeChat = chats.value.find(chat => chat.id === chatId.value)
    if (activeChat && activeChat.title === 'New chat') {
      activeChat.title = text.slice(0, 60)
    }

    chats.value.sort(
      (a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at)
    )

    await scrollMessagesToBottom()
  } catch (err) {
    console.error('Failed to send chat message:', err)
    chatError.value = err.message || 'Unable to send your message.'

    // The backend saves the user message before calling the AI.
    // Reload the thread so the UI matches what is in the database.
    try {
      messages.value = normalizeMessages(
        await getChatMessages(chatId.value)
      )
      await scrollMessagesToBottom()
    } catch (reloadError) {
      console.error('Failed to reload messages:', reloadError)
    }
  } finally {
    sendingMessage.value = false
  }
}


/* =========================
   LOAD BOOK
========================= */

async function loadBook() {

  try {

    const bookId = route.params.id

    book.value = await getBook(bookId)

  }

  catch (err) {

    console.error(
      'Failed to load book:',
      err
    )

  }

}


/* =========================
   LOAD CHAPTERS
========================= */

async function loadChapters() {

  try {

    // loading.value = true

    error.value = ''


    const bookId = route.params.id

    const data =
      await getChapters(bookId)


    chapters.value = [...data].sort(
  (a, b) => a.chapter_number - b.chapter_number
)


    console.log(
      'Loaded chapters:',
      chapters.value.length
    )

  }

  catch (err) {

    console.error(
      'Failed to load chapters:',
      err
    )

    error.value =
      'Unable to load chapters.'

  }

  finally {

    // loading.value = false

  }

}


/* =========================
   LOAD SAVED PROGRESS
========================= */


async function loadProgress() {
  try {
    const bookId = route.params.id
    const progress = await getReadingProgress(bookId)

    if (!progress) return

    const savedChapter = Number(progress.current_chapter) - 1

    const savedPage = Number(
      progress.current_position ??
      progress.current_page ??
      1
    )

    const validSavedPage =
      Number.isFinite(savedPage) &&
      savedPage >= 1 &&
      savedPage <= totalPages.value

    if (validSavedPage) {
      currentPage.value = savedPage
      furthestPage.value = savedPage
      queueCharacterAnalysis(savedPage)

      // Find the chapter containing the saved page.
      const chapterIndex = chapters.value.findIndex(chapter => {
        const start = Number(chapter.start_page)
        const end = Number(chapter.end_page)

        return (
          Number.isFinite(start) &&
          Number.isFinite(end) &&
          savedPage >= start &&
          savedPage <= end
        )
      })

      if (chapterIndex >= 0) {
        currentChapter.value = chapterIndex
      } else if (
        Number.isInteger(savedChapter) &&
        savedChapter >= 0 &&
        savedChapter < chapters.value.length
      ) {
        currentChapter.value = savedChapter
      }

      await nextTick()

      const wrapper = pageWrapperRefs[savedPage]

      if (wrapper) {
        wrapper.scrollIntoView({
          behavior: 'auto',
          block: 'start'
        })
      }
    } else if (
      Number.isInteger(savedChapter) &&
      savedChapter >= 0 &&
      savedChapter < chapters.value.length
    ) {
      currentChapter.value = savedChapter
    }
  } catch (err) {
    console.log('Unable to load saved reading progress.', err)
  }
}

/* =========================
   SAVE PROGRESS
========================= */



async function saveProgress() {
  try {
    if (!totalPages.value) {
      return
    }

    // Persist the furthest page reached, even after navigating backwards.
    const pageToSave = Math.min(totalPages.value, Math.max(1, furthestPage.value, currentPage.value))
    furthestPage.value = pageToSave

    // Find the chapter containing the current page, if chapters exist.
    let chapterIndex = chapters.value.findIndex(chapter => {
      const start = Number(chapter.start_page)
      const end = Number(chapter.end_page)

      return (
        Number.isFinite(start) &&
        Number.isFinite(end) &&
        pageToSave >= start &&
        pageToSave <= end
      )
    })

    // Fall back safely for books without extracted chapters.
    const chapterToSave =
      chapterIndex >= 0
        ? chapters.value[chapterIndex].chapter_number
        : Math.max(1, Number(currentChapter.value) || 1)

    await saveReadingProgress(
      route.params.id,
      chapterToSave,
      pageToSave,
      readingProgress.value
    )

    console.log(
      'Furthest reading progress saved:',
      `Page ${pageToSave}/${totalPages.value}`,
      `(${readingProgress.value}%)`
    )
  } catch (err) {
    console.error('Failed to save reading progress:', err)
  }
}



async function goToChapter(index) {
  if (index < 0 || index >= chapters.value.length) return

  const chapter = chapters.value[index]
  const startPage = Number(chapter.start_page)

  currentChapter.value = index

  if (Number.isFinite(startPage) && startPage >= 1) {
    currentPage.value = startPage
    furthestPage.value = Math.max(furthestPage.value, Math.min(totalPages.value, startPage))

    // Wait for the page wrappers to exist.
    await nextTick()

    const wrapper = pageWrapperRefs[startPage]

    if (wrapper) {
      wrapper.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })
    } else {
      console.warn('Chapter start page not found:', startPage)
    }
  }

  await saveProgress()
}

async function nextChapter() {
  if (currentChapter.value < chapters.value.length - 1) {
    await goToChapter(currentChapter.value + 1)
  }
}

async function previousChapter() {
  if (currentChapter.value > 0) {
    await goToChapter(currentChapter.value - 1)
  }
}


/* =========================
   BACK
========================= */

function goBack() {

  router.push(
    `/book/${route.params.id}`
  )

}


/* =========================
   AI TOGGLE
========================= */

function toggleChat() {

  chatOpen.value =
    !chatOpen.value

}


/* =========================
   START DRAGGING
========================= */

function startDragging() {

  dragging.value = true


  document.addEventListener(
    'mousemove',
    handleDragging
  )


  document.addEventListener(
    'mouseup',
    stopDragging
  )

}


/* =========================
   HANDLE DRAGGING
========================= */

function handleDragging(event) {

  if (!dragging.value) {
    return
  }


  const width =
    100 -
    (
      event.clientX /
      window.innerWidth
    ) * 100


  if (
    width >= 25 &&
    width <= 75
  ) {

    chatWidth.value =
      width

  }

}


/* =========================
   STOP DRAGGING
========================= */

function stopDragging() {

  dragging.value = false


  document.removeEventListener(
    'mousemove',
    handleDragging
  )


  document.removeEventListener(
    'mouseup',
    stopDragging
  )

}


/* =========================
   INITIALIZE
========================= */

async function initializeReader() {
  loading.value = true
  error.value = ''

  try {
    await Promise.all([
      loadBook(),
      loadChapters(),
      loadPdf()
    ])

    if (totalPages.value > 0) {
      await loadProgress()
    }

    if (totalPages.value > 0) {
       predictCurrentPage(currentPage.value)
    }
    // Chat history loads independently of PDF rendering.
    await loadChatHistory()
  } catch (err) {
    console.error('Reader initialization failed:', err)
    error.value = 'Unable to initialize the Reader.'
  } finally {
    loading.value = false
  }
}



async function renderPage(pageNumber, force = false) {
  if (!pdfDocument.value) return

  // Avoid duplicate renders.
  if (renderingPages.has(pageNumber)) {
    await renderingPages.get(pageNumber)
    if (!force) return
  }

  if (renderedPageSet.has(pageNumber) && !force) return

  const renderTask = (async () => {
    const pdf = pdfDocument.value
    if (!pdf) return

    const page = await pdf.getPage(pageNumber)

    const canvas = canvasRefs[pageNumber]
    const wrapper = pageWrapperRefs[pageNumber]
    const pageContent = pageContentRefs[pageNumber]
    const textLayerContainer = textLayerRefs[pageNumber]

    if (!canvas || !wrapper || !pageContent || !textLayerContainer) {
      return
    }

    // Match the actual available page width.
    const baseViewport = page.getViewport({ scale: 1 })
    const availableWidth = Math.max(
      200,
      wrapper.clientWidth
    )

    const scale = availableWidth / baseViewport.width
    const viewport = page.getViewport({ scale })

    // Clear the old text layer before rebuilding it.
    textLayerContainer.replaceChildren()

    // Set the exact same CSS dimensions for both layers.
    const width = viewport.width
    const height = viewport.height

    pageContent.style.width = `${width}px`
    pageContent.style.height = `${height}px`

    canvas.width = Math.ceil(width)
    canvas.height = Math.ceil(height)
    canvas.style.width = `${width}px`
    canvas.style.height = `${height}px`

    textLayerContainer.style.width = `${width}px`
    textLayerContainer.style.height = `${height}px`

    textLayerContainer.style.setProperty(
      '--scale-factor',
      String(viewport.scale)
    )

    textLayerContainer.style.setProperty(
      '--total-scale-factor',
      String(viewport.scale)
    )

    // Render the original PDF page.
    const context = canvas.getContext('2d')
    if (!context) return

    await page.render({
      canvasContext: context,
      viewport
    }).promise

    // Add the selectable text layer using PDF.js.
    const textContent = await page.getTextContent()

    const extractedText = textContent.items
      .map(item => item.str || '')
      .join(' ')
      .trim()

    pageTextCache.set(pageNumber, extractedText)

    if (typeof pdfjsLib.TextLayer === 'function') {
      const textLayer = new pdfjsLib.TextLayer({
        textContentSource: textContent,
        container: textLayerContainer,
        viewport
      })

      await textLayer.render()
    } else if (
      typeof pdfjsLib.renderTextLayer === 'function'
    ) {
      const task = pdfjsLib.renderTextLayer({
        textContent,
        container: textLayerContainer,
        viewport,
        textDivs: []
      })

      if (task?.promise) {
        await task.promise
      }
    } else {
      throw new Error(
        'The installed PDF.js version has no supported text-layer API.'
      )
    }

    renderedPageSet.add(pageNumber)
  })()

  renderingPages.set(pageNumber, renderTask)

  try {
    await renderTask
  } catch (err) {
    console.error(
      `Failed to render page ${pageNumber}:`,
      err
    )
  } finally {
    renderingPages.delete(pageNumber)
  }
}

function setupPageObserver() {
  pageObserver?.disconnect()

  pageObserver = new IntersectionObserver(
    entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue

        const pageNumber = Number(
          entry.target.dataset.page
        )

        if (pageNumber) {
          renderPage(pageNumber)
        }
      }
    },
    {
      root: bookPanelRef.value,
      rootMargin: '1000px 0px',
      threshold: 0
    }
  )

  for (const wrapper of Object.values(pageWrapperRefs)) {
    pageObserver.observe(wrapper)
  }
}


async function loadPdf() {
  try {
    error.value = ''

    console.log('PDF URL:', pdfUrl.value)

    const loadingTask = pdfjsLib.getDocument({
      url: pdfUrl.value
    })

    const pdf = await loadingTask.promise

    pdfDocument.value = pdf
    totalPages.value = pdf.numPages

    // IMPORTANT: create an entry for every page, not just page 1.
    renderedPages.value = Array.from(
      { length: pdf.numPages },
      (_, index) => index + 1
    )

    console.log('PDF loaded:', pdf.numPages, 'pages')

    await nextTick()

    setupPageObserver()

    setupPdfResizeObserver()

    // Render the first page immediately.
    await renderPage(1)
  } catch (err) {
    console.error('Failed to load PDF:', err)
    console.error('PDF URL that failed:', pdfUrl.value)

    if (err instanceof Error) {
      error.value = `PDF loading failed: ${err.message}`
    } else {
      error.value = 'PDF loading failed. Check the browser console.'
    }
  }
}

async function renderAllPages() {
  for (const pageNumber of renderedPages.value) {
    await renderPage(pageNumber)
  }
}


onMounted(() => {
  readerActive = false
  analysisQueue.length = 0
  queuedAnalysisPages.clear()
  document.addEventListener('mouseup', stopDragging)
  document.addEventListener('mouseup', handleTextSelection)
  document.addEventListener('mousedown', hideSelectionMenu)

  initializeReader()
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleDragging)
  document.removeEventListener('mouseup', stopDragging)
  document.removeEventListener('mouseup', handleTextSelection)
  document.removeEventListener('mousedown', hideSelectionMenu)

  pageObserver?.disconnect()
  clearTimeout(progressSaveTimer)

  pdfResizeObserver?.disconnect()
  clearTimeout(resizeTimer)

  if (pdfDocument.value) {
    pdfDocument.value.destroy()
    pdfDocument.value = null
  }
})
const controlsHidden = ref(false)

function toggleReadingControls() {
  controlsHidden.value = !controlsHidden.value
}

</script>


<style scoped>

* {
  box-sizing: border-box;
}


.reader-page {

  height: 100vh;

  background: #f8f5f0;

  color: #2d2926;

  display: flex;

  flex-direction: column;

  font-family: Georgia, "Times New Roman", serif;

}


/* HEADER */

.reader-header {

  height: 68px;

  flex-shrink: 0;

  display: flex;

  align-items: center;

  justify-content: space-between;

  padding: 0 25px;

  background: #fffdf9;

  border-bottom: 1px solid #e5ded6;

}


.back-button {

  width: 38px;

  height: 38px;

  border: none;

  background: transparent;

  font-size: 22px;

  cursor: pointer;

  color: #65574b;

}


.book-title {

  display: flex;

  flex-direction: column;

  align-items: center;

  gap: 3px;

}


.book-title strong {

  font-size: 15px;

  font-weight: 500;

}


.book-title span {

  font-family: Arial, sans-serif;

  font-size: 11px;

  color: #8b8179;

}


.reader-actions {

  display: flex;

  gap: 8px;

}


.reader-actions button {

  border: 1px solid #e1dad2;

  background: #faf8f4;

  border-radius: 8px;

  padding: 9px 12px;

  cursor: pointer;

  color: #5e5249;

}


.reader-actions button span {

  font-family: Arial, sans-serif;

  font-size: 12px;

}


/* WORKSPACE */

.workspace {

  flex: 1;

  min-height: 0;

  display: flex;

  overflow: hidden;

}


/* BOOK */

.book-panel {

  height: 100%;

  overflow-y: auto;

  transition: width 0.15s ease;

}


.reading-area {
  width: 100%;
  height: 100%;
  padding: 0;
}


.chapter-label {

  color: #9a8777;

  letter-spacing: 2px;

  font-family: Arial, sans-serif;

  font-size: 10px;

  margin-bottom: 14px;

}


.reading-area h1 {

  font-size: 38px;

  font-weight: 500;

  margin: 0 0 35px;

  line-height: 1.2;

}


.book-text {

  font-size: 18px;

  line-height: 1.9;

  color: #4c443e;

}


.book-text p {

  margin-bottom: 28px;

}


/* DIVIDER */

.divider {

  width: 7px;

  background: #e2dbd3;

  cursor: col-resize;

  flex-shrink: 0;

  display: flex;

  align-items: center;

  justify-content: center;

}


.divider:hover {

  background: #cfc4b8;

}


.divider-handle {

  width: 3px;

  height: 55px;

  border-radius: 5px;

  background: #8d7b6c;

}


/* AI PANEL */

.ai-panel {

  height: 100%;

  background: #fffdf9;

  display: flex;

  flex-direction: column;

  min-width: 0;

}


.ai-header {

  height: 70px;

  padding: 0 18px;

  border-bottom: 1px solid #e7e0d8;

  display: flex;

  align-items: center;

  justify-content: space-between;

}


.ai-header > div {

  display: flex;

  align-items: center;

  gap: 10px;

}


.ai-icon {

  width: 35px;

  height: 35px;

  background: #ebe2d8;

  border-radius: 50%;

  display: flex;

  align-items: center;

  justify-content: center;

}


.ai-header strong,

.ai-header small {

  display: block;

}


.ai-header strong {

  font-size: 14px;

}


.ai-header small {

  font-family: Arial, sans-serif;

  font-size: 10px;

  color: #8c827a;

  margin-top: 3px;

}


.ai-header button {

  border: none;

  background: transparent;

  font-size: 23px;

  cursor: pointer;

  color: #776b62;

}


/* MESSAGES */

.messages {

  flex: 1;

  overflow-y: auto;

  padding: 25px 18px;

}


.message {

  display: flex;

  gap: 9px;

  margin-bottom: 20px;

}


.ai-message {

  align-items: flex-start;

}


.user-message {

  justify-content: flex-end;

}


.message-avatar {

  width: 28px;

  height: 28px;

  border-radius: 50%;

  background: #e9e0d6;

  display: flex;

  align-items: center;

  justify-content: center;

  flex-shrink: 0;

  font-size: 13px;

}


.message-content {

  max-width: 82%;

  padding: 11px 13px;

  border-radius: 11px;

  background: #f0ebe5;

}


.user-message .message-content {

  background: #675649;

  color: white;

}


.message-content p {

  margin: 0;

  font-family: Arial, sans-serif;

  font-size: 13px;

  line-height: 1.55;

}


/* INPUT */

.chat-input {

  padding: 14px;

  border-top: 1px solid #e7e0d8;

  display: flex;

  gap: 8px;

}


.chat-input textarea {

  flex: 1;

  resize: none;

  border: 1px solid #ddd4ca;

  border-radius: 9px;

  padding: 10px;

  font-family: Arial, sans-serif;

  outline: none;

  background: #faf8f5;

}


.chat-input textarea:focus {

  border-color: #a69484;

}


.chat-input button {

  width: 38px;

  height: 38px;

  align-self: flex-end;

  border: none;

  border-radius: 8px;

  background: #594b40;

  color: white;

  cursor: pointer;

}


/* FOOTER */

.reader-footer {

  height: 42px;

  flex-shrink: 0;

  padding: 0 25px;

  display: flex;

  align-items: center;

  gap: 12px;

  background: #fffdf9;

  border-top: 1px solid #e5ded6;

  font-family: Arial, sans-serif;

  font-size: 11px;

  color: #81766e;

}


.footer-progress {

  flex: 1;

  max-width: 400px;

  height: 4px;

  background: #e0d8cf;

  border-radius: 5px;

  overflow: hidden;

}


.footer-progress-fill {

  height: 100%;

  background: #756456;

}


/* RESPONSIVE */

@media (max-width: 750px) {

  .reader-actions button span {

    display: none;

  }


  .reading-area {

    padding: 40px 25px;

  }


  .reading-area h1 {

    font-size: 30px;

  }


  .book-text {

    font-size: 16px;

  }

}


.chat-input button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.chat-input button:not(:disabled):hover {
  background: #463a31;
}

.chapter-navigation {
  margin-top: 50px;

  display: flex;

  align-items: center;

  justify-content: space-between;

  gap: 20px;

  font-family: Arial, sans-serif;

  font-size: 12px;

  color: #81766e;
}

.chapter-navigation button {
  padding: 10px 16px;

  border: 1px solid #d8cec3;

  border-radius: 8px;

  background: #fffdf9;

  color: #5d4c3e;

  cursor: pointer;
}

.chapter-navigation button:hover:not(:disabled) {
  background: #f1ebe4;
}

.chapter-navigation button:disabled {
  opacity: 0.4;

  cursor: not-allowed;
}


.pdf-reader {
  width: 100%;
  min-height: 100%;
  padding: 24px 12px 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.pdf-page-wrapper {
  width: 100%;
  max-width: 900px;
  display: flex;
  flex-direction: column;
  align-items: center;
  scroll-margin-top: 16px;
}

.page-number {
  width: 100%;
  text-align: center;
  margin-bottom: 8px;
  font-family: Arial, sans-serif;
  font-size: 11px;
  color: #9a8e84;
}

.pdf-page-content {
  position: relative;
  flex: 0 0 auto;
  max-width: 100%;
  line-height: 0;
  background: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.pdf-page {
  position: absolute;
  inset: 0;
  z-index: 0;
  display: block;
  max-width: none;
  margin: 0;
  padding: 0;
}

.pdf-text-layer {
  position: absolute;
  inset: 0;
  z-index: 1;
  overflow: hidden;
  user-select: text;
  -webkit-user-select: text;
  cursor: text;
}

.reading-area {
  width: 100%;
  height: 100%;
  padding: 0;
}

.chapter-nav-button {
  flex-shrink: 0;
  padding: 8px 12px;
  border: 1px solid #d8cec3;
  border-radius: 8px;
  background: #fffdf9;
  color: #5d4c3e;
  font-family: Arial, sans-serif;
  font-size: 11px;
  cursor: pointer;
}

.chapter-nav-button:hover:not(:disabled) {
  background: #f1ebe4;
}

.chapter-nav-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pdf-page-wrapper {
  scroll-margin-top: 16px;
}

@media (max-width: 750px) {
  .reader-footer {
    gap: 6px;
    padding: 0 8px;
  }

  .chapter-nav-button {
    padding: 7px;
    font-size: 10px;
  }
}


.chat-toolbar {
  display: flex;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid #e7e0d8;
  background: #fffdf9;
}

.chat-toolbar select {
  flex: 1;
  min-width: 0;
  padding: 8px;
  border: 1px solid #ddd4ca;
  border-radius: 8px;
  background: #faf8f5;
  color: #5e5249;
  font-family: Arial, sans-serif;
  font-size: 12px;
}

.new-chat-button {
  flex-shrink: 0;
  padding: 8px 10px;
  border: 1px solid #d8cec3;
  border-radius: 8px;
  background: #f5f0e9;
  color: #594b40;
  font-family: Arial, sans-serif;
  font-size: 12px;
  cursor: pointer;
}

.new-chat-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chat-error {
  margin: 0;
  padding: 8px 12px;
  background: #fff0ed;
  color: #9b3022;
  font-family: Arial, sans-serif;
  font-size: 12px;
  line-height: 1.4;
}

.messages {
  scroll-behavior: auto;
}


.pdf-text-layer {
  position: absolute;
  inset: 0;
  overflow: hidden;
  opacity: 1;
  line-height: 1;
  text-align: initial;
  transform-origin: 0 0;
  user-select: text;
  -webkit-user-select: text;
  cursor: text;
}

.pdf-text-layer :deep(span),
.pdf-text-layer :deep(br) {
  position: absolute;
  color: transparent;
  white-space: pre;
  cursor: text;
  transform-origin: 0 0;
}

.pdf-text-layer :deep(span)::selection {
  background: rgba(0, 100, 255, 0.3);
}


/* SELECTED TEXT ACTION MENU */

.selection-menu {
  position: fixed;
  z-index: 10000;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px;
  background: #fffdf9;
  border: 1px solid #e1d6ca;
  border-radius: 10px;
  box-shadow: 0 5px 20px rgba(45, 35, 25, 0.18);
  font-family: Arial, sans-serif;
  white-space: nowrap;
}

.selection-menu button {
  border: none;
  border-radius: 7px;
  padding: 9px 11px;
  background: #f3ede6;
  color: #594b40;
  font-size: 12px;
  cursor: pointer;
}

.selection-menu button:hover:not(:disabled) {
  background: #e7dbce;
}

.selection-menu button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}


/* =================================
   READMATE — PEARL & EMERALD HEADER
   ================================= */

.reader-page {
  background: #f5f7f2;
  color: #203c30;
}

.reader-header {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #fbfcf8;
  border-bottom: 1px solid #dfe7dc;
}

.back-button {
  flex-shrink: 0;
  width: 42px;
  height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #d6dfd3;
  border-radius: 12px;
  background: #e8eee8;
  color: #174c3c;
  font-size: 24px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
}

.back-button:hover {
  background: #d6e4d8;
  transform: translateX(-2px);
}

.book-title strong {
  color: #174c3c;
  font-weight: 700;
}

.book-title span {
  color: #718276;
}

.reader-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
}

.reader-actions .theme-button {
  width: 42px;
  height: 42px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #d6dfd3;
  border-radius: 12px;
  background: #e8eee8;
  color: #174c3c;
  font-size: 20px;
  cursor: pointer;
}

.reader-actions .theme-button:hover {
  background: #d6e4d8;
}

.reader-actions .ai-mode-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 42px;
  padding: 10px 17px;
  border: 1px solid #174c3c;
  border-radius: 12px;
  background: #174c3c;
  color: #ffffff;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
}

.reader-actions .ai-sparkle {
  color: #e7d39b;
  font-size: 18px;
}

.reader-actions .ai-mode-button:hover {
  background: #103b2e;
  transform: translateY(-1px);
}

/* =================================
   ONE-LINE READING FOOTER
   ================================= */

.reader-footer {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  align-items: center;
  gap: 12px;
  width: 100%;
  height: 66px;
  min-height: 66px;
  padding: 10px 20px;
  box-sizing: border-box;
  overflow-x: auto;
  background: #fbfcf8;
  border-top: 1px solid #dfe7dc;
  color: #203c30;
}

.reading-label,
.progress-label,
.progress-percentage {
  flex-shrink: 0;
  white-space: nowrap;
}

.reading-label {
  color: #174c3c;
  font-size: 12px;
  font-weight: 700;
}

.chapter-nav-button {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  padding: 9px 14px;
  border-radius: 11px;
  font-family: Arial, sans-serif;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
}

.chapter-nav-button.previous-button {
  border: 1px solid #d1dfd2;
  background: #e8eee8;
  color: #174c3c;
}

.chapter-nav-button.next-button {
  border: 1px solid #174c3c;
  background: #174c3c;
  color: #ffffff;
}

.chapter-nav-button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.chapter-nav-button.previous-button:hover:not(:disabled) {
  background: #d8e5d9;
}

.chapter-nav-button.next-button:hover:not(:disabled) {
  background: #103b2e;
}

.chapter-nav-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none;
}

.progress-label {
   margin-left: auto;
  flex-shrink: 0;
  color: #52665a;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.footer-progress {
  flex: 1 1 320px;
  min-width: 180px;
  max-width: 420px;
  height: 10px;
  margin: 0;
  border-radius: 20px;
  background: #e2e9df;
  overflow: hidden;
}

.footer-progress-fill {
  height: 100%;
  border-radius: 20px;
  background: linear-gradient(90deg, #70a887, #174c3c);
  transition: width 0.25s ease;
}

.progress-percentage {
   flex-shrink: 0;
  min-width: 42px;
  color: #174c3c;
  font-size: 12px;
  font-weight: 700;
  text-align: right;
}

/* =================================
   RESPONSIVE LAYOUT
   ================================= */

@media (max-width: 750px) {
  .reader-header {
    gap: 8px;
    padding-left: 10px;
    padding-right: 10px;
  }

  .book-title {
    min-width: 0;
    flex: 1;
    overflow: hidden;
  }

  .book-title strong {
    display: block;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .reader-actions {
    gap: 6px;
  }

  .reader-actions .theme-button {
    width: 36px;
    height: 36px;
  }

  .reader-actions .ai-mode-button {
    min-height: 36px;
    padding: 8px 10px;
    font-size: 11px;
  }

  .reader-footer {
    gap: 8px;
    padding: 8px 10px;
  }

  .chapter-nav-button {
    min-height: 34px;
    padding: 7px 9px;
    font-size: 10px;
  }

  .reading-label,
  .progress-label,
  .progress-percentage {
    font-size: 10px;
  }

  .footer-progress {
    flex-basis: 70px;
    min-width: 45px;
    max-width: 100px;
  }
}


.difficulty-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  border-radius: 8px;
  background: rgba(128, 128, 128, 0.1);
  font-size: 13px;
  white-space: nowrap;
}

.difficulty-indicator strong {
  font-weight: 700;
}

.difficulty-error {
  font-size: 12px;
  color: #d97706;
}

</style>
