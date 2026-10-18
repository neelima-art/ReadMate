<template>
  <div class="characters-page">

    <!-- HEADER -->
    <header class="characters-header">

      <button
        class="back-button"
        @click="goBack"
      >
        ← Back
      </button>

      <div class="header-content">

        <span class="page-label">
          READMATE
        </span>

        <h1>
          Characters
        </h1>

        <p v-if="book">
          Characters you've discovered in
          {{ book.title }}
        </p>

      </div>

    </header>


    <!-- LOADING -->
    <div
      v-if="loading"
      class="state"
    >
      Loading characters...
    </div>


    <!-- ERROR -->
    <div
      v-else-if="error"
      class="state error"
    >
      {{ error }}
    </div>


    <!-- EMPTY -->
    <div
      v-else-if="characters.length === 0"
      class="state"
    >

      <div class="empty-icon">
        📖
      </div>

      <h2>
        No characters discovered yet
      </h2>

      <p>
        Characters will appear here as you discover
        them while reading.
      </p>

    </div>


    <!-- CHARACTERS -->
    <main
      v-else
      class="characters-content"
    >

      <div class="characters-grid">

        <article
          v-for="character in characters"
          :key="character.id"
          class="character-card"
        >

          <!-- AVATAR -->

          <div class="character-avatar">

            {{ character.name.charAt(0) }}

          </div>


          <!-- CHARACTER INFORMATION -->

          <div class="character-info">

            <div class="character-heading">

              <h2>
                {{ character.name }}
              </h2>

              <span
                v-if="character.role"
                class="character-role"
              >
                {{ character.role }}
              </span>

            </div>


            <!-- DESCRIPTION -->

            <p
              v-if="character.description"
              class="character-description"
            >
              {{ character.description }}
            </p>


            <!-- RELATIONSHIP -->

            <div
              v-if="character.relationship_to_main"
              class="relationship-box"
            >

              <span class="relationship-label">
                Relationship
              </span>

              <div class="relationship-value">

                <span class="relationship-icon">
                  🤝
                </span>

                <strong>
                  {{ character.relationship_to_main }}
                </strong>

              </div>

            </div>


            <!-- ALIASES -->

            <div
              v-if="character.aliases"
              class="character-detail"
            >

              <span>
                Also known as
              </span>

              <strong>
                {{ character.aliases }}
              </strong>

            </div>


            <!-- FIRST APPEARANCE -->

            <div
              v-if="character.first_appearance"
              class="character-detail"
            >

              <span>
                First appeared
              </span>

              <strong>
                Chapter {{ character.first_appearance }}
              </strong>

            </div>

          </div>

        </article>

      </div>

    </main>

  </div>
</template>


<script setup>

import { ref, onMounted } from 'vue'

import {
  useRoute,
  useRouter
} from 'vue-router'

import {
  getBook,
  getCharacters,
  getReadingProgress
} from '../services/api'


const route = useRoute()

const router = useRouter()


const book = ref(null)

const characters = ref([])

const loading = ref(true)

const error = ref('')


async function loadCharacters() {

  try {

    const bookId = route.params.id

    book.value =
      await getBook(bookId)

    const progress = await getReadingProgress(bookId)
    const unlockedChapter = Math.max(1, Number(progress?.current_chapter) || 1)
    const unlockedPage = Math.max(0, Number(progress?.current_position) || 0)
    const found = await getCharacters(bookId, unlockedChapter)
    // Never display a character whose first appearance is after the furthest read page.
    characters.value = found.filter(character =>
      unlockedPage > 0 &&
      Number(character.first_appearance || 1) <= unlockedPage
    )

  } catch (err) {

    console.error(err)

    error.value =
      'Could not load characters.'

  } finally {

    loading.value = false

  }

}


function goBack() {

  router.push(
    `/book/${route.params.id}`
  )

}


onMounted(() => {

  loadCharacters()

})

</script>


<style scoped>

* {
  box-sizing: border-box;
}


.characters-page {

  min-height: 100vh;

  background: #f8f5f0;

  color: #40372f;

}


/* HEADER */

.characters-header {

  display: flex;

  align-items: flex-start;

  gap: 30px;

  padding: 35px 7%;

  border-bottom: 1px solid #e4ddd5;

  background: #fffdf9;

}


.back-button {

  border: none;

  background: transparent;

  color: #6c5c50;

  font-size: 15px;

  cursor: pointer;

  padding: 8px 0;

}


.back-button:hover {

  color: #3f342c;

}


.header-content {

  min-width: 0;

}


.page-label {

  font-family: Arial, sans-serif;

  font-size: 11px;

  letter-spacing: 2px;

  color: #9a897a;

}


.characters-header h1 {

  margin: 6px 0;

  font-family: Georgia, serif;

  font-size: 38px;

  font-weight: 500;

}


.characters-header p {

  margin: 0;

  color: #8b7d71;

  font-family: Arial, sans-serif;

  font-size: 14px;

}


/* CONTENT */

.characters-content {

  width: min(1100px, 86%);

  margin: 45px auto;

}


.characters-grid {

  display: grid;

  grid-template-columns:
    repeat(
      auto-fit,
      minmax(330px, 1fr)
    );

  gap: 24px;

}


/* CHARACTER CARD */

.character-card {

  display: flex;

  gap: 20px;

  padding: 26px;

  background: #fffdf9;

  border: 1px solid #e5ddd4;

  border-radius: 16px;

  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;

}


.character-card:hover {

  transform: translateY(-3px);

  box-shadow:
    0 10px 28px
    rgba(80, 65, 50, 0.09);

}


/* AVATAR */

.character-avatar {

  flex-shrink: 0;

  width: 62px;

  height: 62px;

  border-radius: 50%;

  display: flex;

  align-items: center;

  justify-content: center;

  background: #e9dfd4;

  color: #6b5848;

  font-family: Georgia, serif;

  font-size: 26px;

}


/* INFORMATION */

.character-info {

  min-width: 0;

  flex: 1;

}


.character-heading h2 {

  margin: 0 0 6px;

  font-family: Georgia, serif;

  font-size: 22px;

  font-weight: 500;

  color: #453a32;

}


.character-role {

  display: inline-block;

  margin-bottom: 12px;

  font-family: Arial, sans-serif;

  font-size: 10px;

  letter-spacing: 1.2px;

  text-transform: uppercase;

  color: #9b8878;

}


.character-description {

  margin: 0 0 18px;

  font-family: Arial, sans-serif;

  font-size: 14px;

  line-height: 1.65;

  color: #75685d;

}


/* RELATIONSHIP */

.relationship-box {

  padding: 13px 14px;

  margin-bottom: 16px;

  background: #f5efe8;

  border: 1px solid #e7ddd3;

  border-radius: 10px;

}


.relationship-label {

  display: block;

  margin-bottom: 7px;

  font-family: Arial, sans-serif;

  font-size: 10px;

  letter-spacing: 1px;

  text-transform: uppercase;

  color: #9a897a;

}


.relationship-value {

  display: flex;

  align-items: center;

  gap: 7px;

  color: #5d4d40;

}


.relationship-icon {

  font-size: 16px;

}


.relationship-value strong {

  font-family: Georgia, serif;

  font-size: 15px;

  font-weight: 500;

}


/* DETAILS */

.character-detail {

  display: flex;

  justify-content: space-between;

  gap: 15px;

  padding-top: 9px;

  margin-top: 9px;

  border-top: 1px solid #eee8e1;

  font-family: Arial, sans-serif;

  font-size: 11px;

  color: #978a80;

}


.character-detail strong {

  color: #66584e;

  font-weight: 500;

  text-align: right;

}


/* STATES */

.state {

  text-align: center;

  padding: 100px 20px;

  font-family: Arial, sans-serif;

  color: #82766b;

}


.state h2 {

  font-family: Georgia, serif;

  color: #55483e;

}


.state p {

  font-size: 14px;

}


.empty-icon {

  font-size: 42px;

  margin-bottom: 15px;

}


.error {

  color: #a15d5d;

}


/* MOBILE */

@media (max-width: 650px) {

  .characters-header {

    padding: 25px;

    gap: 15px;

  }


  .characters-header h1 {

    font-size: 30px;

  }


  .characters-content {

    width: 90%;

    margin: 30px auto;

  }


  .characters-grid {

    grid-template-columns: 1fr;

  }


  .character-card {

    padding: 20px;

  }


  .character-avatar {

    width: 52px;

    height: 52px;

    font-size: 22px;

  }


  .character-detail {

    flex-direction: column;

    gap: 3px;

  }


  .character-detail strong {

    text-align: left;

  }

}

</style>