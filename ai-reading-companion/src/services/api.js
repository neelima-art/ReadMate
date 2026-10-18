
const API_URL = ''

export async function getBooks() {
  const response = await fetch(`${API_URL}/api/books`)

  if (!response.ok) {
    throw new Error('Failed to fetch books')
  }

  return await response.json()
}

export async function getBook(bookId) {
  const response = await fetch(
    `${API_URL}/api/books/${bookId}`
  )

  if (!response.ok) {
    throw new Error('Failed to fetch book')
  }

  return await response.json()
}

export async function getReadingProgress(bookId) {
  const response = await fetch(
    `${API_URL}/api/books/${bookId}/progress`
  )

  if (!response.ok) {
    throw new Error('Failed to fetch reading progress')
  }

  return await response.json()
}

export async function saveReadingProgress(
  bookId,
  currentChapter,
  currentPosition,
  progress
) {
  const response = await fetch(
    `${API_URL}/api/books/${bookId}/progress?current_chapter=${currentChapter}&current_position=${currentPosition}&progress_value=${progress}`,
    {
      method: 'POST'
    }
  )

  if (!response.ok) {
    throw new Error('Failed to save reading progress')
  }

  return await response.json()
}

export async function getCharacters(
  bookId,
  currentChapter = 999
) {
  const response = await fetch(
    `${API_URL}/api/books/${bookId}/characters?current_chapter=${currentChapter}`
  )

  if (!response.ok) {
    throw new Error('Failed to fetch characters')
  }

  return await response.json()
}

export async function getRelationships(
  bookId,
  currentChapter = 999
) {
  const response = await fetch(
    `${API_URL}/api/books/${bookId}/relationships?current_chapter=${currentChapter}`
  )

  if (!response.ok) {
    throw new Error('Failed to fetch relationships')
  }

  return await response.json()
}

export async function getChapters(bookId) {
  const response = await fetch(
    `${API_URL}/api/books/${bookId}/chapters`
  )

  if (!response.ok) {
    throw new Error('Failed to fetch chapters')
  }

  return await response.json()
}

export async function createChat(bookId) {
  const response = await fetch(
    `${API_URL}/api/books/${bookId}/chats`,
    {
      method: 'POST'
    }
  )

  if (!response.ok) {
    throw new Error('Failed to create chat')
  }

  return await response.json()
}

// Get all chat sessions for a book
export async function getBookChats(bookId) {
  const response = await fetch(
    `${API_URL}/api/books/${bookId}/chats`
  )

  if (!response.ok) {
    throw new Error('Failed to fetch chat history')
  }

  return await response.json()
}

// Get messages from one chat session
export async function getChatMessages(chatId) {
  const response = await fetch(
    `${API_URL}/api/chats/${chatId}/messages`
  )

  if (!response.ok) {
    throw new Error('Failed to fetch chat messages')
  }

  return await response.json()
}

// Send a message to ReadMate AI
export async function sendChatMessage(
  chatId,
  content,
  currentChapter = 1
) {
  const response = await fetch(
    `${API_URL}/api/chats/${chatId}/messages`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content,
        current_chapter: currentChapter
      })
    }
  )

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))

    throw new Error(
      errorData.detail || 'Failed to send message'
    )
  }

  return await response.json()
}

// NEW: Automatically analyze a book page
// to extract characters and relationships.
export async function analyzeBookPage(bookId, pageNumber) {
  const response = await fetch(
    `${API_URL}/api/books/${encodeURIComponent(bookId)}/analyze-page`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        page_number: pageNumber
      })
    }
  )

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))

    throw new Error(
      error.detail || `Page analysis failed (${response.status})`
    )
  }

  return response.json()
}


export async function getBookAbout(bookId) {
  const response = await fetch(
    `/api/books/${encodeURIComponent(bookId)}/about`
  );

  if (!response.ok) {
    throw new Error("Failed to load book information");
  }

  return await response.json();
}

// Predict reading difficulty using the trained LinuxONE model
export async function predictDifficulty(text) {
  const response = await fetch('/api/predict-difficulty', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ text })
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))

    throw new Error(
      error.detail || `Difficulty prediction failed (${response.status})`
    )
  }

  return response.json()
}
