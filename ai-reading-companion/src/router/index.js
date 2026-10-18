
import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'
import BookView from '../views/BookView.vue'
import ReaderView from '../views/ReaderView.vue'
import CharactersView from '../views/CharactersView.vue'
import ChatView from '../views/ChatView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),

  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/book/:id',
      name: 'book',
      component: BookView
    },
    {
      path: '/reader/:id',
      name: 'reader',
      component: ReaderView
    },
    {
      path: '/characters/:id',
      name: 'characters',
      component: CharactersView
    },
    {
      path: '/chat/:id',
      name: 'chat',
      component: ChatView
    }
  ]
})

export default router
