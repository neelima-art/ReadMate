<template>



  <div class="app">

    <input
    ref="fileInput"
    type="file"
    accept=".pdf,.epub,application/pdf,application/epub+zip"
    style="display: none"
    @change="handleFileUpload"
    />

    <!-- Sidebar -->
    

    <!-- Main Content -->
    <main class="main">

      
<!-- Header -->
<header class="header">
  <div class="header-brand">
    
<span class="logo-icon" aria-label="ReadMate logo">
  <svg
    viewBox="0 0 24 24"
    width="27"
    height="27"
    fill="none"
    stroke="currentColor"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path d="M12 7.5C9.5 5.5 6.5 5 3 5.8v12c3.5-.8 6.5-.3 9 1.7" />
    <path d="M12 7.5C14.5 5.5 17.5 5 21 5.8v12c-3.5-.8-6.5-.3-9 1.7" />
    <path d="M12 7.5v12" />
  </svg>
</span>

    <span class="brand-name">ReadMate</span>
  </div>

  

  <div class="header-actions">
    <button
      class="profile-button"
      aria-label="Open profile options"
      :aria-expanded="profileMenuOpen"
      @click="profileMenuOpen = !profileMenuOpen"
    >
      <span>♙</span>
    </button>

    <div v-if="profileMenuOpen" class="profile-menu">
      <strong>Your profile</strong>
      <p>Login and account settings will be available soon.</p>
    </div>
  </div>
</header>


      <!-- Continue Reading --> 
<section class="section">
  <div class="section-header">
    <div>
     <h2>Where You Left Off</h2>
<p>Return to the story whenever you're ready.</p>
    </div>
  </div>

  <div v-if="recentBook" class="continue-card">
    <div class="book-cover large-cover">
      <img
        v-if="recentBook.cover_top || recentBook.cover_url"
        :src="getCoverUrl(recentBook)"
        :alt="recentBook.title + ' cover'"
        class="book-cover-image"
      />
      <span v-else>📖</span>
    </div>

    <div class="continue-info">
      <span class="book-label">YOUR READING JOURNEY</span>

      <h3>{{ recentBook.title }}</h3>
      <p class="author">
        {{ recentBook.author || 'Unknown author' }}
      </p>

      <p class="description">
  Your next chapter is waiting.
</p>

      <button
  class="continue-button"
  @click="openBook(recentBook.book_id)"
>
  <svg
    width="22"
    height="22"
    viewBox="0 0 24 24"
    fill="none"
    stroke="white"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path d="M12 7v14" />
    <path d="M12 7C9 4 5 4 2 5v14c4-1 7-1 10 2" />
    <path d="M12 7c3-3 7-3 10-2v14c-4-1-7-1-10 2" />
  </svg>
  Continue Reading
</button>
    </div>
  </div>

  <p v-else-if="!loading">
    No books found. Upload a book to get started.
  </p>
</section>

      <section class="section">

      <div class="section-header library-header">
  <div class="library-heading">
    <h2>My Library</h2>
<p>Your collection of stories, ideas, and discoveries.</p>
  </div>

  <input
    v-model="searchQuery"
    class="search-input library-search"
    type="search"
   placeholder="Find a book or author..."
    aria-label="Search books"
  />

  <button
    class="upload-button"
    @click="openFilePicker"
    :disabled="uploading"
  >
    {{ uploading ? 'Uploading...' : '+ Upload Book' }}
  </button>
</div>
        <div class="books-grid">

<article
  v-for="book in filteredBooks"
  :key="book.id"
  class="book-card"
  @click="openBook(book.book_id)"
>
  <div class="book-cover">
  <template v-if="book.cover_top || book.cover_url">
    <img
      :src="book.cover_url || `${book.cover_top}`"
      :alt="book.title + ' cover'"
      class="book-cover-image"
    />
    </template>

    <template v-else>
      <span>📖</span>
    </template>
  </div>

  <div class="book-details">
    <h3>{{ book.title }}</h3>
    <p>{{ book.author || 'Unknown author' }}</p>
  </div>
</article>
                  <!-- Upload card -->
                  <article class="upload-card">
        
          <div class="upload-icon">
            +
          </div>
        
          <h3>Begin a New Chapter</h3>

<p>
  Add a book to your collection and let a new story unfold.
</p>
        
          <button
            @click="openFilePicker"
            :disabled="uploading"
          >
            {{ uploading ? 'Uploading...' : 'Upload Book' }}
          </button>
        
          <p
            v-if="uploadMessage"
            class="upload-message"
          >
            {{ uploadMessage }}
          </p>
        
        </article>

        </div> 

      </section>

    </main>

  </div>
</template>

<script setup>

import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getBooks
} from '../services/api'

const router = useRouter()

const books = ref([])
const demoBookIds = [
  'harry-potter',
  'hobbit',
  'gatsby',
  '1984'
]

const libraryBooks = computed(() =>
  books.value.filter(book =>
    !demoBookIds.includes(book.book_id)
  )
)





const searchQuery = ref('')

const filteredBooks = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()

  const availableBooks = books.value.filter(
    book => !demoBookIds.includes(book.book_id)
  )

  if (!query) return availableBooks

  return availableBooks.filter(book =>
    (book.title || '').toLowerCase().includes(query) ||
    (book.author || '').toLowerCase().includes(query)
  )
})

const loading = ref(true)

const error = ref('')

const uploading = ref(false)

const uploadMessage = ref('')

const fileInput = ref(null)
const profileMenuOpen = ref(false)
const recentBook = computed(() => {
  const recentBookId = localStorage.getItem('readmate-recent-book')

  return (
    books.value.find(book => book.book_id === recentBookId) ||
    books.value.find(book => !demoBookIds.includes(book.book_id)) ||
    null
  )
})
onMounted(async () => {
  await loadBooks()
})


async function loadBooks() {

  try {

    loading.value = true

    books.value = await getBooks()

    console.log(
      'BOOKS FROM API:',
      books.value
    )

  } catch (err) {

    console.error(err)

    error.value =
      'Could not load your books.'

  } finally {

    loading.value = false

  }
}

function getCoverUrl(book) {
  const cover = book.cover_url || book.cover_top

  if (!cover) return ''

  if (cover.startsWith('http://') || cover.startsWith('https://')) {
    return cover
  }

  return `${cover}`
}

function openBook(bookId) {
  localStorage.setItem('readmate-recent-book', bookId)
  router.push(`/book/${bookId}`)
}


function getProgress(bookId) {

  const progressMap = {

    'harry-potter': 43,

    'hobbit': 75,

    'gatsby': 50,

    '1984': 30

  }

  return progressMap[bookId] || 0

}


/* OPEN FILE PICKER */

function openFilePicker() {

  fileInput.value?.click()

}


/* HANDLE FILE */

async function handleFileUpload(event) {

  const file = event.target.files[0]

  if (!file) {
    return
  }


  /* CHECK FILE TYPE */

  const allowedTypes = [
    'application/pdf',
    'application/epub+zip'
  ]

  const isPdf =
    file.type === 'application/pdf'

  const isEpub =
    file.name.toLowerCase().endsWith('.epub')


  if (!isPdf && !isEpub) {

    uploadMessage.value =
      'Please select a PDF  file.'

    event.target.value = ''

    return

  }


  uploading.value = true

  uploadMessage.value =
    'Uploading your book...'


  try {

    const formData = new FormData()

    formData.append(
      'file',
      file
    )


    const response = await fetch(
      '/api/books/upload',
      {
        method: 'POST',
        body: formData
      }
    )


    const data =
      await response.json()


    if (!response.ok) {

      throw new Error(
        data.detail ||
        'Upload failed'
      )

    }


    console.log(
      'UPLOAD RESPONSE:',
      data
    )


    uploadMessage.value =
      'Book uploaded successfully!'


    /*
      Refresh the library.

      At this stage the backend only
      stores the file, so the book
      may not appear as a database
      book yet.
    */

    await loadBooks()


  } catch (err) {

    console.error(err)

    uploadMessage.value =
      err.message ||
      'Could not upload the book.'

  } finally {

    uploading.value = false

    /*
      Clear the input so the same
      file can be selected again.
    */

    event.target.value = ''

  }

}

</script>

<style scoped>

* {
  box-sizing: border-box;
}

.app {
  min-height: 100vh;
  display: flex;
  background: #f7f4ef;
  color: #2d2926;
  font-family: Georgia, "Times New Roman", serif;
}

/* SIDEBAR */

.sidebar {
  width: 240px;
  min-height: 100vh;
  padding: 30px 20px;
  background: #eee9e1;
  border-right: 1px solid #ddd5ca;
  display: flex;
  flex-direction: column;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 23px;
  font-weight: bold;
  margin-bottom: 45px;
}


.logo-icon {
  width: 48px;
  height: 48px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: #174C3C;
  color: #FFFFFF;
  border-radius: 14px;
  box-shadow: 0 4px 10px rgba(23, 76, 60, 0.16);
}



nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 12px 14px;
  border-radius: 10px;
  color: #68605a;
  text-decoration: none;
  font-family: Arial, sans-serif;
  font-size: 14px;
}

.nav-item:hover {
  background: #e2dbd1;
}

.nav-item.active {
  background: #ddd4c8;
  color: #2d2926;
  font-weight: 600;
}

.sidebar-bottom {
  margin-top: auto;
}

.profile {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 5px 0;
  border-top: 1px solid #d8d0c5;
  margin-top: 15px;
}

.avatar,
.profile-button {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #655548;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: Arial, sans-serif;
  font-weight: bold;
}

.profile strong,
.profile small {
  display: block;
}

.profile strong {
  font-size: 13px;
}

.profile small {
  color: #837a72;
  font-family: Arial, sans-serif;
  font-size: 11px;
  margin-top: 3px;
}

/* MAIN */

.main {
  flex: 1;
  padding: 38px 55px 60px;
  max-width: 1500px;
}

/* HEADER */

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 48px;
}

.greeting {
  color: #8b7d70;
  font-family: Arial, sans-serif;
  font-size: 13px;
  margin: 0 0 8px;
}

.header h1 {
  font-size: 31px;
  font-weight: 500;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-button {
  border: 1px solid #ded7ce;
  background: #fbf9f6;
  border-radius: 10px;
  padding: 11px 16px;
  color: #837a72;
  display: flex;
  gap: 10px;
  align-items: center;
  font-family: Arial, sans-serif;
}

.profile-button {
  border: none;
}

/* SECTIONS */

.section {
  margin-bottom: 50px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0 0 5px;
  font-size: 22px;
  font-weight: 500;
}

.section-header p {
  margin: 0;
  color: #91867c;
  font-family: Arial, sans-serif;
  font-size: 13px;
}

.view-all {
  background: none;
  border: none;
  color: #756457;
  cursor: pointer;
}

/* CONTINUE */

.continue-card {
  display: flex;
  gap: 30px;
  padding: 28px;
  background: #ebe3d9;
  border: 1px solid #ded5ca;
  border-radius: 16px;
  max-width: 900px;
}

.book-cover {
  height: 220px;
  width: 145px;
  flex-shrink: 0;
  border-radius: 5px;
  background: #756456;
  color: #f8f3eb;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 15px;
  box-shadow: 6px 8px 15px rgba(70, 55, 40, 0.12);
}

.book-cover span {
  font-size: 14px;
}

.book-cover strong {
  font-size: 23px;
  margin-top: 5px;
}

.large-cover {
  height: 245px;
  width: 165px;
}

.continue-info {
  max-width: 530px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.book-label {
  font-family: Arial, sans-serif;
  font-size: 10px;
  letter-spacing: 1.5px;
  color: #927f6d;
}

.continue-info h3 {
  font-size: 25px;
  line-height: 1.25;
  font-weight: 500;
  margin: 8px 0;
}

.author {
  color: #766c64;
  margin: 0 0 12px;
}

.description {
  color: #716961;
  line-height: 1.6;
  margin: 0 0 20px;
  font-family: Arial, sans-serif;
  font-size: 13px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-family: Arial, sans-serif;
  font-size: 11px;
  color: #756c65;
  margin-bottom: 6px;
}

.progress-bar {
  height: 5px;
  background: #d7cec3;
  border-radius: 10px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background: #756456;
}

.continue-button {
  align-self: flex-start;
  margin-top: 18px;
  padding: 11px 18px;
  border: none;
  border-radius: 8px;
  background: #594b40;
  color: white;
  cursor: pointer;
  font-family: Arial, sans-serif;
}

/* BOOK GRID */

.books-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 22px;
}

.book-card {
  background: #fbf9f6;
  border: 1px solid #e3ddd5;
  border-radius: 13px;
  overflow: hidden;
  transition: transform 0.2s ease;
}

.book-card:hover {
  transform: translateY(-4px);
}

.book-card .book-cover {
  width: 100%;
  height: 240px;
  border-radius: 0;
  box-shadow: none;
}

.book-details {
  padding: 15px;
}

.book-details h3 {
  margin: 0 0 5px;
  font-size: 16px;
  font-weight: 500;
}

.book-details p {
  margin: 0 0 13px;
  color: #8a8077;
  font-family: Arial, sans-serif;
  font-size: 12px;
}

.book-details span {
  color: #91877e;
  font-family: Arial, sans-serif;
  font-size: 10px;
}

.small-progress {
  height: 4px;
  background: #e2dbd2;
  border-radius: 5px;
  margin-bottom: 7px;
}

.small-progress div {
  height: 100%;
  background: #756456;
  border-radius: 5px;
}

/* UPLOAD */

.upload-card {
  min-height: 310px;
  border: 1.5px dashed #cfc5b9;
  border-radius: 13px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 25px;
}

.upload-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #ebe4db;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 25px;
  color: #76675a;
  margin-bottom: 15px;
}

.upload-card h3 {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 500;
}

.upload-card p {
  margin: 0 0 17px;
  color: #93887e;
  font-family: Arial, sans-serif;
  font-size: 12px;
  line-height: 1.5;
}

.upload-card button,
.upload-button {
  background: #594b40;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 15px;
  cursor: pointer;
  font-family: Arial, sans-serif;
}

/* RESPONSIVE */

@media (max-width: 1000px) {

  .sidebar {
    width: 190px;
  }

  .main {
    padding: 30px;
  }

  .books-grid {
    grid-template-columns: repeat(2, 1fr);
  }

}

@media (max-width: 700px) {

  .sidebar {
    display: none;
  }

  .main {
    padding: 25px 18px;
  }

  .header {
    align-items: flex-start;
    gap: 20px;
  }

  .header h1 {
    font-size: 24px;
  }

  .search-button span {
    display: none;
  }

  .continue-card {
    flex-direction: column;
  }

  .large-cover {
    width: 150px;
  }

  .books-grid {
    grid-template-columns: 1fr;
  }

}

.book-card {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(60, 45, 35, 0.12);
}
.upload-message {
  margin-top: 12px !important;
  margin-bottom: 0 !important;
  color: #756456 !important;
  font-size: 11px !important;
}

.upload-card button:disabled,
.upload-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.search-input {
  width: 220px;
  padding: 12px 16px;
  border: 1px solid #ded7ce;
  border-radius: 10px;
  background: #fbf9f6;
  color: #2d2926;
  font: 14px Arial, sans-serif;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-input:focus {
  border-color: #9b7558;
  box-shadow: 0 0 0 3px rgba(155, 117, 88, 0.12);
}

.search-input::placeholder {
  color: #837a72;
}

@media (max-width: 700px) {
  .search-input {
    width: 160px;
    max-width: 100%;
  }
}
.book-cover {
  height: 290px;
  overflow: hidden;
  background: #776456;
  display: flex;
  align-items: center;
  justify-content: center;
}

.book-cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.book-details {
  padding: 16px 18px;
}
/* My Books: clean book covers */
.book-card .book-cover {
  width: 100%;
  height: 290px;
  padding: 0;
  border-radius: 0;
  background: #fbf9f6;
  box-shadow: none;
  overflow: hidden;
}

.book-cover-image {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #fbf9f6;
}

/* Continue Reading cover */
.large-cover {
  width: 165px;
  height: 245px;
  padding: 0;
  background: transparent;
  box-shadow: none;
  overflow: hidden;
}

.large-cover .book-cover-image {
  object-fit: contain;
}

/* My Books header layout */
.library-header {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) minmax(200px, 300px) auto;
  gap: 20px;
  align-items: center;
}

.library-search {
  width: 100%;
  justify-self: center;
}

/* Clean book covers */
.book-card .book-cover {
  width: 100%;
  height: 290px;
  padding: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  overflow: hidden;
}

.book-cover-image {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: transparent;
}

/* Recently opened book cover */
.large-cover {
  width: 165px;
  height: 245px;
  padding: 0;
  background: transparent;
  box-shadow: none;
  overflow: hidden;
}

.large-cover .book-cover-image {
  object-fit: contain;
}

/* My Books header */
.library-header {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) minmax(200px, 300px) auto;
  gap: 20px;
  align-items: center;
}

.library-search {
  width: 100%;
}

@media (max-width: 700px) {
  .library-header {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .library-search {
    max-width: none;
  }

  .library-header .upload-button {
    justify-self: start;
  }
}

/* ReadMate: full-width dashboard without a sidebar */

.app {
  display: block;
  width: 100%;
  min-height: 100vh;
  background: #f8f5f0;
}

.main {
  width: 100%;
  max-width: none;
  min-width: 0;
  padding: 30px clamp(20px, 4vw, 64px) 60px;
  margin: 0;
}

.header {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 32px;
  margin-bottom: 48px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e9e0d6;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
}

.brand-name {
  font-size: 25px;
  font-weight: 600;
  color: #493b31;
}

.header-welcome h1 {
  margin: 0;
  font-size: clamp(24px, 2.5vw, 34px);
  font-weight: 500;
  line-height: 1.25;
}

.greeting {
  margin: 0 0 8px;
  color: #8b7969;
  font: 13px Arial, sans-serif;
}

.header-actions {
  position: relative;
  display: flex;
  justify-content: flex-end;
}

.profile-button {
  width: 44px;
  height: 44px;
  border: 1px solid #ded2c4;
  border-radius: 50%;
  background: #eae0d4;
  color: #59483a;
  cursor: pointer;
  font-size: 23px;
}

.profile-button:hover {
  background: #ded0c0;
}

.profile-menu {
  position: absolute;
  z-index: 10;
  top: 54px;
  right: 0;
  width: 250px;
  padding: 18px;
  border: 1px solid #e5dbd0;
  border-radius: 14px;
  background: #fffdf9;
  box-shadow: 0 12px 32px rgba(65, 48, 35, 0.12);
  font-family: Arial, sans-serif;
}

.profile-menu strong {
  color: #493b31;
}

.profile-menu p {
  margin: 8px 0 0;
  color: #817366;
  font-size: 13px;
  line-height: 1.5;
}

/* More balanced reading card */
.continue-card {
  max-width: 100%;
  background: #efe7dd;
  border-color: #e5dbd0;
}

/* Responsive header */
@media (max-width: 850px) {
  .header {
    grid-template-columns: 1fr auto;
    gap: 18px;
  }

  .header-brand {
    grid-column: 1;
    grid-row: 1;
  }

  .header-actions {
    grid-column: 2;
    grid-row: 1;
  }

  .header-welcome {
    grid-column: 1 / -1;
    grid-row: 2;
  }
}

@media (max-width: 600px) {
  .main {
    padding: 22px 16px 40px;
  }

  .header {
    margin-bottom: 32px;
    padding-bottom: 20px;
  }

  .library-header {
    grid-template-columns: 1fr;
  }

  .library-search {
    width: 100%;
  }

  .continue-card {
    padding: 20px;
    gap: 20px;
  }
}


/* ========================================
   READMATE — PEARL & EMERALD THEME
   ======================================== */

.app {
  --page-bg: #F5F7F2;
  --emerald: #174C3C;
  --emerald-dark: #123D30;
  --gold: #D5B779;
  --sage: #E8EEE8;
  --text-main: #203C30;
  --text-muted: #657368;
  --border: #E0E6DC;
  --card-bg: #FFFFFF;

  display: block;
  width: 100%;
  min-height: 100vh;
  background: var(--page-bg);
  color: var(--text-main);
  font-family: Georgia, "Times New Roman", serif;
}

.main {
  width: 100%;
  max-width: 1600px;
  min-width: 0;
  margin: 0 auto;
  padding: 30px clamp(18px, 4vw, 64px) 60px;
}

/* TOP HEADER: LOGO, WELCOME, PROFILE */

.header {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 30px;
  margin-bottom: 42px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border);
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
}

.header-brand .logo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 30px;
  line-height: 1;
}

.brand-name {
  display: inline-block;
  color: var(--emerald);
  font-size: 27px;
  font-weight: 700;
}

.header-welcome {
  min-width: 0;
}

.header-welcome .greeting {
  margin: 0 0 8px;
  color: var(--text-muted);
  font: 13px Arial, sans-serif;
}

.header-welcome h1 {
  margin: 0;
  color: var(--emerald);
  font-size: clamp(25px, 2.5vw, 35px);
  font-weight: 500;
  line-height: 1.25;
}

.header-actions {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.header-actions .profile-button {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 46px;
  height: 46px;
  padding: 0;
  border: 1px solid var(--border);
  border-radius: 50%;
  background: var(--sage);
  color: var(--emerald);
  cursor: pointer;
  font-size: 24px;
  line-height: 1;
}

.header-actions .profile-button:hover {
  background: #DCE7DC;
}

.profile-menu {
  position: absolute;
  z-index: 100;
  top: 56px;
  right: 0;
  width: 250px;
  padding: 18px;
  border: 1px solid var(--border);
  border-radius: 14px;
  background: var(--card-bg);
  color: var(--text-main);
  box-shadow: 0 12px 32px rgba(23, 76, 60, 0.12);
  font-family: Arial, sans-serif;
}

.profile-menu strong {
  color: var(--emerald);
}

.profile-menu p {
  margin: 8px 0 0;
  color: var(--text-muted);
  font-size: 13px;
  line-height: 1.5;
}

/* SECTION HEADINGS */

.section {
  margin-bottom: 48px;
}

.section-header {
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0 0 6px;
  color: var(--emerald);
  font-size: 25px;
  font-weight: 500;
}

.section-header p {
  margin: 0;
  color: var(--text-muted);
  font: 13px/1.6 Arial, sans-serif;
}

/* CONTINUE READING */

.continue-card {
  display: flex;
  align-items: center;
  gap: 30px;
  width: 100%;
  max-width: none;
  padding: 28px;
  border: 1px solid var(--border);
  border-radius: 18px;
  background: var(--card-bg);
  box-shadow: 0 5px 20px rgba(23, 76, 60, 0.045);
}

.large-cover {
  flex-shrink: 0;
  width: 165px;
  height: 245px;
  padding: 0;
  overflow: hidden;
  border-radius: 8px;
  background: var(--sage);
  box-shadow: 0 5px 15px rgba(23, 76, 60, 0.12);
}

.large-cover .book-cover-image {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.continue-info {
  min-width: 0;
  max-width: 650px;
}

.book-label {
  color: #927844;
  font: 10px Arial, sans-serif;
  letter-spacing: 1.6px;
}

.continue-info h3 {
  margin: 8px 0;
  color: var(--emerald);
  font-size: 27px;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.author,
.description {
  color: var(--text-muted);
}

.description {
  font: 13px/1.6 Arial, sans-serif;
}

.continue-button,
.upload-button,
.upload-card button {
  border: 1px solid var(--emerald);
  border-radius: 9px;
  background: var(--emerald);
  color: #FFFFFF;
  font: 600 13px Arial, sans-serif;
  cursor: pointer;
}

.continue-button {
  padding: 12px 18px;
}

.continue-button:hover,
.upload-button:hover,
.upload-card button:hover {
  background: var(--emerald-dark);
}

/* MY LIBRARY: HEADING, SEARCH, UPLOAD */

.library-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(220px, 360px) auto;
  align-items: center;
  gap: 18px;
}

.library-heading {
  min-width: 0;
}

.library-heading h2 {
  margin: 0 0 6px;
}

.library-heading p {
  margin: 0;
}

.library-search {
  width: 100%;
  min-width: 0;
  height: 44px;
  padding: 0 15px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--card-bg);
  color: var(--text-main);
  font: 14px Arial, sans-serif;
  outline: none;
}

.library-search:focus {
  border-color: var(--emerald);
  box-shadow: 0 0 0 3px rgba(23, 76, 60, 0.10);
}

.library-search::placeholder {
  color: #879187;
}

.upload-button {
  min-height: 44px;
  padding: 0 17px;
  white-space: nowrap;
}

/* BOOK CARDS */

.books-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  align-items: stretch;
  gap: 24px;
}

.book-card {
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 14px;
  background: var(--card-bg);
  cursor: pointer;
  box-shadow: 0 3px 12px rgba(23, 76, 60, 0.035);
  transition: transform 0.2s, box-shadow 0.2s;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 24px rgba(23, 76, 60, 0.10);
}

.book-card .book-cover {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 270px;
  padding: 0;
  overflow: hidden;
  border-radius: 0;
  background: var(--sage);
  box-shadow: none;
}

.book-card .book-cover-image {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: var(--sage);
}

.book-details {
  padding: 16px;
}

.book-details h3 {
  margin: 0 0 7px;
  color: var(--text-main);
  font-size: 16px;
  font-weight: 600;
  line-height: 1.45;
  overflow-wrap: anywhere;
}

.book-details p {
  margin: 0;
  color: var(--text-muted);
  font: 12px/1.5 Arial, sans-serif;
}

/* FINAL ADD-BOOK CARD */

.upload-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 0;
  min-height: 340px;
  height: 100%;
  padding: 22px;
  border: 1.5px dashed #B9C8B9;
  border-radius: 14px;
  background: rgba(232, 238, 232, 0.55);
  text-align: center;
}

.upload-card:hover {
  border-color: var(--gold);
  background: #EEF2EB;
}

.upload-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  margin-bottom: 17px;
  border-radius: 50%;
  background: var(--emerald);
  color: #FFFFFF;
  font-size: 27px;
}

.upload-card h3 {
  margin: 0 0 8px;
  color: var(--emerald);
  font-size: 17px;
  line-height: 1.4;
}

.upload-card p {
  color: var(--text-muted);
  font: 12px/1.6 Arial, sans-serif;
}

.upload-card button {
  padding: 11px 16px;
}

.upload-message {
  overflow-wrap: anywhere;
}

.upload-card button:disabled,
.upload-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* RESPONSIVE */

@media (max-width: 1100px) {
  .books-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px;
  }

  .book-card .book-cover {
    height: 250px;
  }

  .library-header {
    grid-template-columns: minmax(0, 1fr) minmax(180px, 280px) auto;
    gap: 12px;
  }
}

@media (max-width: 800px) {
  .header {
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 16px;
  }

  .header-brand {
    grid-column: 1;
    grid-row: 1;
  }

  .header-actions {
    grid-column: 2;
    grid-row: 1;
  }

  .header-welcome {
    grid-column: 1 / -1;
    grid-row: 2;
  }

  .library-header {
    grid-template-columns: minmax(0, 1fr) auto;
  }

  .library-heading {
    grid-column: 1 / -1;
  }

  .library-search {
    grid-column: 1;
  }

  .library-header .upload-button {
    grid-column: 2;
  }

  .books-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .main {
    padding: 22px 15px 36px;
  }

  .header {
    margin-bottom: 30px;
    padding-bottom: 19px;
  }

  .logo-icon {
    font-size: 26px;
  }

  .brand-name {
    font-size: 23px;
  }

  .header-welcome h1 {
    font-size: 27px;
  }

  .section {
    margin-bottom: 36px;
  }

  .continue-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
    padding: 20px;
  }

  .large-cover {
    width: 135px;
    height: 205px;
  }

  .continue-info h3 {
    font-size: 23px;
  }

  .library-header {
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 12px;
  }

  .library-search {
    font-size: 13px;
    padding: 0 10px;
  }

  .upload-button {
    padding: 0 11px;
    font-size: 12px;
  }

  .books-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }

  .book-card .book-cover {
    height: 205px;
  }

  .book-details {
    padding: 12px;
  }

  .book-details h3 {
    font-size: 14px;
  }

  .book-details p {
    font-size: 11px;
  }

  .upload-card {
    min-height: 260px;
    padding: 14px;
  }
}
.continue-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-direction: row;
  gap: 10px;
}
</style>
