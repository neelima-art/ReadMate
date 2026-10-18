<template>

<div v-if="loading" class="status-message">
  Loading book...
</div>

<div v-else-if="error" class="status-message">
  {{ error }}
</div>

<div v-else-if="book" class="book-page">
  <!-- <div class="book-page"> -->

    <!-- ReadMate Header -->
<header class="page-header">
  <div class="brand">
    <div class="brand-icon">
      <svg viewBox="0 0 24 24" fill="none"
           stroke="currentColor" stroke-width="2"
           stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 7v14" />
        <path d="M12 7C9 4 5 4 2 5v14c4-1 7-1 10 2" />
        <path d="M12 7c3-3 7-3 10-2v14c-4-1-7-1-10 2" />
      </svg>
    </div>
    <span>ReadMate</span>
  </div>

  <button class="library-btn" @click="goHome">
    <span>←</span> My Library
  </button>
</header>

    <!-- Book -->
    <section class="book-header">

   <div class="cover">
  <img
    v-if="book.cover_url || book.cover_image || book.coverImage || book.cover_top"
    :src="getCoverUrl(book)"
    :alt="`${book.title} cover`"
    class="cover-image"
    @error="coverImageFailed = true"
    v-show="!coverImageFailed"
  />

  <div v-if="!(book.cover_url || book.cover_image || book.coverImage || book.cover_top) || coverImageFailed"
       class="cover-fallback">
    <span>{{ book.coverTop || 'BOOK' }}</span>
    <strong>{{ book.coverTitle || book.title }}</strong>
    <small>{{ book.author }}</small>
  </div>
</div>

      <div class="book-info">

      <p class="label">YOUR NEXT ADVENTURE</p>

        <h1>{{ book.title }}</h1>

        <p class="author">
          {{ book.author }}
        </p>

        <p class="description">
          {{ book.description }}
        </p>

        <!-- Progress -->
        <div class="progress-section">

<div class="progress-header">
  <span>Reading Progress</span>
  <span>{{ readingProgress.progress }}%</span>
</div>

<div class="progress-bar">
  <div
    class="progress"
    :style="{
      width: Math.min(
        100,
        Math.max(0, readingProgress.progress)
      ) + '%'
    }"
  ></div>
</div>

<p class="chapter">
  Currently reading:
  <strong>
    Chapter {{ readingProgress.current_chapter }}
  </strong>
</p>
</div>

        <!-- Continue -->
       <button
  class="continue-btn"
  @click="continueReading"
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
  <span>Continue Reading</span>
</button>
<button class="continue-btn" style="margin-top:12px" @click="openFullChat">💬 Open AI Chat</button>

      </div>

    </section>

    <!-- Details -->
    <section class="details-grid">

      

<!-- About -->
<div class="detail-card">
  <h2>About this book</h2>

  <div class="about-details">
    <p>
      <strong>Title:</strong>
      {{ book.title }}
    </p>

    <p>
      <strong>Author:</strong>
      {{ book.author || "Unknown" }}
    </p>

    <p>
      <strong>Published:</strong>
      {{ about?.publication_date || "Not available" }}
    </p>

    <p>
      <strong>Genre:</strong>
      {{ book.genre || "Not available" }}
    </p>

    <p>
      <strong>Pages:</strong>
      {{ about?.total_pages ?? "Not available" }}
    </p>

    <p>
      <strong>Chapters:</strong>
      {{ about?.total_chapters ?? "Not available" }}
    </p>
  </div>
</div>

      <!-- Characters -->
      <div class="detail-card">

        <div class="card-header">
          <h2>Characters</h2>

          <button @click="openCharacters">
            View All →
          </button>
        </div>

        <div class="characters">

          <div
            v-for="character in book.characters"
            :key="character"
            class="character"
          >
            <div class="avatar">
              {{ character.charAt(0) }}
            </div>

            <span>{{ character }}</span>
          </div>

        </div>

      </div>

      

    </section>

  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getBook,
  getReadingProgress
} from '../services/api'

const route = useRoute()
const router = useRouter()

const book = ref(null)
const loading = ref(true)
const error = ref('')
const readingProgress = ref({
  progress: 0,
  current_chapter: 1,
  current_position: 0
})
const coverImageFailed = ref(false)

onMounted(async () => {
  try {
    book.value = await getBook(route.params.id)
   loadBookAbout(route.params.id)

    try {
      const progressData = await getReadingProgress(
        route.params.id
      )

      readingProgress.value = {
        progress: Number(progressData.progress) || 0,
        current_chapter:
          Number(progressData.current_chapter) || 1,
        current_position:
          Number(progressData.current_position) || 0
      }

      console.log(
        'READING PROGRESS FROM BACKEND:',
        readingProgress.value
      )
    } catch (progressError) {
      console.error(
        'Could not load reading progress:',
        progressError
      )
    }

    console.log('BOOK FROM BACKEND:', book.value)
  } catch (err) {
    console.error(err)
    error.value = 'Could not load this book.'
  } finally {
    loading.value = false
  }
})


function goHome() {
  router.push('/')
}

function continueReading() {
  router.push(`/reader/${route.params.id}`)
}

function openFullChat() {
  router.push(`/chat/${route.params.id}`)
}

function openCharacters() {
  router.push(`/characters/${route.params.id}`)
}


function getCoverUrl(book) {
  const cover =
    book.cover_url ||
    book.cover_image ||
    book.coverImage ||
    book.cover_top

  if (!cover) return ''

  if (/^https?:\/\//i.test(cover)) {
    return cover
  }

  return `/${cover.replace(/^\/+/, '')}`
}


import { getBookAbout } from "../services/api";

const about = ref(null);
const aboutLoading = ref(false);

async function loadBookAbout(bookId) {
  aboutLoading.value = true;

  try {
    about.value = await getBookAbout(bookId);
  } catch (error) {
    console.error("About book error:", error);
  } finally {
    aboutLoading.value = false;
  }
}


</script>

<style scoped>
.book-page {
  min-height: 100vh;
  background: #f8f5f0;
  color: #2d2926;
  padding: 40px 7%;
  font-family: Georgia, "Times New Roman", serif;
}

.back-btn {
  border: none;
  background: transparent;
  color: #6d6258;
  font-size: 15px;
  cursor: pointer;
  padding: 0;
  margin-bottom: 35px;
}

.back-btn:hover {
  color: #3d352f;
}

.book-header {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 55px;
  max-width: 1000px;
  margin: auto;
}

.cover {
  height: 350px;
  width: 250px;
  box-sizing: border-box;
  border-radius: 8px;
  background: #eee7df;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 15px 35px rgba(60, 45, 35, 0.18);
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.cover-fallback {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  padding: 24px;
  background: #6f5745;
  color: #f8f5f0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.cover-fallback span {
  font-size: 16px;
  letter-spacing: 2px;
}

.cover-fallback strong {
  font-size: 25px;
  line-height: 1.2;
  margin-top: 10px;
  overflow-wrap: anywhere;
}

.cover-fallback small {
  margin-top: 12px;
  font-size: 13px;
}

.label {
  font-size: 12px;
  letter-spacing: 2px;
  color: #92745d;
  margin-bottom: 10px;
}

.book-info {
  padding-top: 20px;
}

.book-info h1 {
  font-size: 48px;
  font-weight: 500;
  margin: 0;
}

.author {
  color: #75695f;
  font-size: 18px;
  margin-top: 10px;
}

.description {
  max-width: 650px;
  line-height: 1.7;
  color: #625951;
  margin: 30px 0;
}

.progress-section {
  max-width: 600px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.progress-bar {
  height: 7px;
  background: #e4ded6;
  border-radius: 10px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background: #8b6b53;
  border-radius: 10px;
}

.chapter {
  font-size: 13px;
  color: #766b63;
}

.continue-btn {
  margin-top: 20px;
  padding: 13px 22px;
  border: none;
  border-radius: 8px;
  background: #59483b;
  color: white;
  font-size: 15px;
  cursor: pointer;
  
}

.continue-btn:hover {
  background: #46372d;
}

.details-grid {
  max-width: 1000px;
  margin: 70px auto 0;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 22px;
}

.detail-card {
  background: #fffdf9;
  border: 1px solid #e8e1d9;
  border-radius: 12px;
  padding: 25px;
}

.detail-card h2 {
  font-size: 21px;
  font-weight: 500;
  margin-top: 0;
}

.detail-card p {
  color: #6d635b;
  line-height: 1.6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header button {
  border: none;
  background: transparent;
  color: #80654f;
  cursor: pointer;
}

.characters {
  display: flex;
  gap: 25px;
  margin-top: 20px;
}

.character {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #e8ded3;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #5e4c3d;
}

@media (max-width: 750px) {
  .book-header {
    grid-template-columns: 1fr;
    gap: 30px;
  }

  .cover {
    width: 220px;
    margin: auto;
  }

  .book-info h1 {
    font-size: 38px;
  }

  .details-grid {
    grid-template-columns: 1fr;
  }

  .chat-card {
    grid-column: span 1;
  }
}

/* ===== ReadMate Pearl & Emerald Redesign ===== */

.book-page {
  min-height: 100vh;
  padding: 0 5% 48px;
  background: #f5f7f2;
  color: #203c30;
  font-family: Georgia, "Times New Roman", serif;
}

/* Header */
.page-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 18px;
  padding: 18px 0;
  margin-bottom: 48px;
  border-bottom: 1px solid #e1e8df;
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  color: #174c3c;
  font-size: 29px;
  font-weight: 700;
}

.brand-icon {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  border-radius: 15px;
  background: #174c3c;
  color: white;
}

.brand-icon svg {
  width: 32px;
  height: 32px;
}

.library-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 22px;
  border: 1px solid #d6dfd3;
  border-radius: 30px;
  background: #fbfcf8;
  color: #174c3c;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
}

.library-btn:hover {
  background: #e8eee8;
  transform: translateY(-1px);
}

.library-btn span {
  font-size: 21px;
}

/* Book hero */
.book-header {
  grid-template-columns: minmax(200px, 315px) minmax(0, 1fr);
  gap: clamp(28px, 5vw, 55px);
  max-width: 1120px;
  align-items: center;
}

.cover {
  width: 100%;
  max-width: 315px;
  height: 440px;
  margin: auto;
  border-radius: 13px;
  background: #e8eee8;
  box-shadow: 0 20px 40px rgba(23, 76, 60, 0.16);
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.cover-fallback {
  background: #174c3c;
  color: #f5f7f2;
}

.label {
  display: inline-block;
  padding: 8px 13px;
  border-radius: 8px;
  background: #e8eee0;
  color: #174c3c;
  font-weight: 700;
  letter-spacing: 1px;
}

.book-info {
  padding-top: 0;
}

.book-info h1 {
  color: #183d31;
  font-size: clamp(34px, 4vw, 54px);
  line-height: 1.12;
  overflow-wrap: anywhere;
}

.author {
  color: #718276;
  font-size: 20px;
}

.description {
  color: #505b53;
  font-family: Arial, sans-serif;
  font-size: 16px;
  line-height: 1.8;
  margin: 24px 0;
}

/* Progress */
.progress-section {
  max-width: 650px;
  padding: 20px 24px 15px;
  border: 1px solid #dce4d8;
  border-radius: 16px;
  background: rgba(255, 255, 251, 0.8);
}

.progress-header {
  color: #174c3c;
  font-weight: 700;
  font-size: 16px;
}

.progress-bar {
  height: 10px;
  margin: 14px 0;
  background: #e3e8df;
  border-radius: 20px;
}

.progress {
  background: #17634c;
  transition: width 0.3s ease;
}

.chapter {
  margin-bottom: 0;
  color: #66766a;
  font-family: Arial, sans-serif;
  font-size: 14px;
}

/* Continue reading */
.continue-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-width: 260px;
  padding: 16px 26px;
  border-radius: 35px;
  background: #174c3c;
  color: white;
  font-weight: 700;
  font-size: 16px;
  box-shadow: 0 8px 18px rgba(23, 76, 60, 0.12);
  transition: background 0.2s, transform 0.2s;
  display: inline-flex;
align-items: center;
justify-content: center;
flex-direction: row;
gap: 10px;
}

.continue-btn:hover {
  background: #103b2e;
  transform: translateY(-2px);
}

/* Bottom cards */
.details-grid {
  max-width: 1120px;
  margin: 55px auto 0;
  gap: 24px;
  align-items: stretch;
}

.detail-card {
  min-width: 0;
  padding: 28px;
  border: 1px solid #dfe5da;
  border-radius: 18px;
  background: #fbfcf8;
  box-shadow: 0 8px 24px rgba(32, 60, 48, 0.04);
}

.detail-card h2 {
  color: #174c3c;
  font-size: 25px;
}

.detail-card p {
  color: #515d54;
  line-height: 1.85;
}

.card-header button {
  color: #174c3c;
  font-weight: 700;
  font-size: 14px;
}

.card-header button:hover {
  color: #b18b3d;
}

.characters {
  display: flex;
  flex-wrap: wrap;
  gap: 22px;
}

.character {
  min-width: 65px;
  color: #344d3d;
  text-align: center;
}

.avatar {
  width: 54px;
  height: 54px;
  background: #e8eee8;
  color: #174c3c;
  font-weight: 700;
}

/* Responsive layout */
@media (max-width: 750px) {
  .book-page {
    padding: 0 5% 32px;
  }

  .page-header {
    margin-bottom: 30px;
  }

  .brand {
    gap: 9px;
    font-size: 23px;
  }

  .brand-icon {
    width: 44px;
    height: 44px;
  }

  .library-btn {
    padding: 10px 13px;
    font-size: 13px;
  }

  .book-header {
    grid-template-columns: 1fr;
    gap: 30px;
  }

  .cover {
    width: 220px;
    height: 320px;
  }

  .book-info h1 {
    font-size: 38px;
  }

  .progress-section {
    padding: 17px;
  }

  .continue-btn {
    width: 100%;
    min-width: 0;
  }

  .details-grid {
    grid-template-columns: 1fr;
    margin-top: 35px;
  }

  .detail-card {
    padding: 22px;
  }
}


</style>
