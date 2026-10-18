<template>
  <div class="book-card">
    <div class="book-cover">
      <img :src="book.cover" :alt="book.title" />
    </div>

    <div class="book-info">
      <h3>{{ book.title }}</h3>
      <p>{{ book.author }}</p>

      <div class="progress-container">
        <div
          class="progress-bar"
          :style="{ width: book.progress + '%' }"
        ></div>
      </div>

      <span>{{ book.progress }}% completed</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  book: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.book-card {
  width: 180px;
  cursor: pointer;
}

.book-cover {
  width: 180px;
  height: 260px;
  overflow: hidden;
  border-radius: 10px;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-info h3 {
  margin-top: 10px;
  margin-bottom: 4px;
}

.book-info p {
  margin: 0 0 10px;
  color: #888;
}

.progress-container {
  width: 100%;
  height: 5px;
  background: #ddd;
  border-radius: 5px;
}

.progress-bar {
  height: 100%;
  border-radius: 5px;
  background: #000;
}

.book-info span {
  font-size: 12px;
  color: #777;
}
</style>