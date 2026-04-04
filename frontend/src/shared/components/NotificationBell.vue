<template>
  <v-menu v-model="menu" :close-on-content-click="false" max-width="400">
    <template v-slot:activator="{ props }">
      <v-btn
        icon="mdi-bell"
        variant="text"
        v-bind="props"
        class="notification-bell"
        :class="{ 'has-notifications': unreadCount > 0 }"
      >
        <v-badge
          v-if="unreadCount > 0"
          :content="unreadCount > 99 ? '99+' : unreadCount.toString()"
          :color="getBadgeColor()"
          overlap
          :dot="unreadCount <= 3"
        >
          <v-icon>mdi-bell</v-icon>
        </v-badge>
        <v-icon v-else>mdi-bell-outline</v-icon>
      </v-btn>
    </template>

    <v-card class="notification-dropdown" elevation="8">
      <v-card-title class="d-flex align-center justify-space-between pa-4">
        <div class="d-flex align-center">
          <v-icon class="me-2">mdi-bell-ring</v-icon>
          <span class="text-h6">{{ $t('notifications') || 'الإشعارات' }}</span>
          <v-chip
            v-if="unreadCount > 0"
            size="small"
            :color="getBadgeColor()"
            class="ms-2"
          >
            {{ unreadCount }} جديد
          </v-chip>
        </div>
        <div class="d-flex ga-1">
          <v-btn
            v-if="unreadCount > 0"
            size="small"
            variant="text"
            @click="markAllAsRead"
            :loading="isMarkingAllRead"
          >
            <v-icon size="small">mdi-check-all</v-icon>
          </v-btn>
          <v-btn
            size="small"
            variant="text"
            @click="refreshNotifications"
            :loading="isLoading"
          >
            <v-icon size="small">mdi-refresh</v-icon>
          </v-btn>
        </div>
      </v-card-title>

      <v-divider></v-divider>

      <!-- Filters -->
      <v-card-text class="pa-2 pb-0">
        <div class="d-flex gap-1 mb-2">
          <v-chip
            v-for="category in categoryFilters"
            :key="category.value"
            :value="category.value"
            :color="filters.category === category.value ? 'primary' : 'default'"
            size="small"
            variant="outlined"
            clickable
            @click="toggleCategoryFilter(category.value)"
          >
            <v-icon size="small" start>{{ category.icon }}</v-icon>
            {{ category.label }}
          </v-chip>
        </div>
      </v-card-text>

      <v-divider></v-divider>

      <!-- Notification List -->
      <div class="notification-list" style="max-height: 350px; overflow-y: auto;">
        <v-list density="compact">
          <template v-if="filteredNotifications.length > 0">
            <v-list-item
              v-for="notification in filteredNotifications.slice(0, 10)"
              :key="notification.id"
              :class="{ 
                'unread': !notification.is_read,
                'priority-high': notification.priority === 'high',
                'priority-critical': notification.priority === 'critical'
              }"
              @click="handleNotificationClick(notification)"
              class="notification-item"
            >
              <template v-slot:prepend>
                <v-avatar
                  :color="getNotificationColor(notification.category)"
                  size="32"
                  class="me-3"
                >
                  <v-icon size="16" color="white">
                    {{ getNotificationIcon(notification.type) }}
                  </v-icon>
                </v-avatar>
              </template>

              <v-list-item-content>
                <v-list-item-title class="text-body-2 font-weight-medium">
                  {{ notification.title }}
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption mt-1">
                  {{ notification.message }}
                </v-list-item-subtitle>
                <div class="d-flex align-center mt-1">
                  <v-chip
                    :color="getPriorityColor(notification.priority)"
                    size="x-small"
                    variant="flat"
                    class="me-1"
                  >
                    {{ getPriorityLabel(notification.priority) }}
                  </v-chip>
                  <span class="text-caption text-medium-emphasis">
                    {{ formatTime(notification.created_at) }}
                  </span>
                </div>
              </v-list-item-content>

              <template v-slot:append>
                <div class="d-flex flex-column align-end">
                  <v-btn
                    v-if="!notification.is_read"
                    icon="mdi-circle"
                    size="x-small"
                    color="primary"
                    variant="text"
                    class="unread-indicator"
                  ></v-btn>
                  <v-btn
                    icon="mdi-close"
                    size="x-small"
                    variant="text"
                    @click.stop="deleteNotification(notification.id)"
                    class="delete-btn"
                  ></v-btn>
                </div>
              </template>
            </v-list-item>
          </template>

          <v-list-item v-else class="text-center pa-6">
            <v-icon size="48" color="grey-lighten-1" class="mb-2">
              mdi-bell-off-outline
            </v-icon>
            <div class="text-body-2 text-medium-emphasis mb-2">
              {{ $t('noNotifications') || 'لا توجد إشعارات' }}
            </div>
            <v-btn
              size="small"
              variant="outlined"
              @click="refreshNotifications"
              :loading="isLoading"
            >
              <v-icon size="small" start>mdi-refresh</v-icon>
              تحديث
            </v-btn>
          </v-list-item>
        </v-list>
      </div>

      <v-divider></v-divider>

      <v-card-actions v-if="filteredNotifications.length > 0" class="pa-2">
        <v-btn
          block
          variant="text"
          @click="viewAllNotifications"
          prepend-icon="mdi-view-list"
        >
          {{ $t('viewAllNotifications') || 'عرض جميع الإشعارات' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore, NOTIFICATION_CATEGORIES, NOTIFICATION_PRIORITIES } from '@/stores/notifications'

const router = useRouter()
const notificationsStore = useNotificationsStore()

// Reactive state
const menu = ref(false)
const isMarkingAllRead = ref(false)

// Computed properties from store
const notifications = computed(() => notificationsStore.notifications)
const unreadCount = computed(() => notificationsStore.unreadCount)
const isLoading = computed(() => notificationsStore.isLoading)
const filteredNotifications = computed(() => notificationsStore.filteredNotifications)
const filters = computed(() => notificationsStore.filters)

// Category filters
const categoryFilters = ref([
  { value: null, label: 'الكل', icon: 'mdi-dots-horizontal' },
  { value: NOTIFICATION_CATEGORIES.ORDER, label: 'الطلبات', icon: 'mdi-shopping' },
  { value: NOTIFICATION_CATEGORIES.FINANCE, label: 'المالية', icon: 'mdi-cash' },
  { value: NOTIFICATION_CATEGORIES.SECURITY, label: 'الأمان', icon: 'mdi-shield-account' },
  { value: NOTIFICATION_CATEGORIES.MARKETING, label: 'التسويق', icon: 'mdi-bullhorn' },
])

// Methods
const getNotificationIcon = (type) => {
  const icons = {
    // Finance
    'payment_success': 'mdi-credit-card-check',
    'payment_failed': 'mdi-credit-card-remove',
    'refund_processed': 'mdi-cash-refund',
    'ccp_received': 'mdi-bank-transfer-in',
    'coupon_applied': 'mdi-ticket-percent',
    'coupon_expired': 'mdi-clock-alert',
    
    // Orders
    'order_created': 'mdi-shopping-plus',
    'order_confirmed': 'mdi-check-circle',
    'order_cancelled': 'mdi-cancel',
    'order_shipped': 'mdi-truck',
    'order_delivered': 'mdi-home',
    'order_returned': 'mdi-package-variant-closed',
    'order_modified': 'mdi-pencil',
    
    // Inventory
    'stock_low': 'mdi-alert',
    'stock_out': 'mdi-alert-octagon',
    'product_added': 'mdi-package-variant-plus',
    'product_updated': 'mdi-package-variant-closed',
    
    // Security
    'login_new_device': 'mdi-devices',
    'password_changed': 'mdi-lock-reset',
    'login_failed': 'mdi-lock-alert',
    'account_locked': 'mdi-account-lock',
    
    // Logistics
    'shipping_confirmed': 'mdi-truck-check',
    'shipping_delayed': 'mdi-truck-alert',
    'delivery_failed': 'mdi-truck-remove',
    'package_received': 'mdi-warehouse',
    
    // System
    'system_maintenance': 'mdi-wrench',
    'system_update': 'mdi-update',
    'database_backup': 'mdi-database',
    
    // Marketing
    'promotion_launched': 'mdi-megaphone',
    'newsletter_sent': 'mdi-email-newsletter',
    'campaign_completed': 'mdi-chart-line',
    
    // Customer Service
    'support_ticket_created': 'mdi-headset',
    'support_ticket_resolved': 'mdi-check-all',
    'feedback_received': 'mdi-comment-quote',
  }
  return icons[type] || 'mdi-bell'
}

const getNotificationColor = (category) => {
  const colors = {
    [NOTIFICATION_CATEGORIES.FINANCE]: 'success',
    [NOTIFICATION_CATEGORIES.INVENTORY]: 'warning',
    [NOTIFICATION_CATEGORIES.ORDER]: 'info',
    [NOTIFICATION_CATEGORIES.SECURITY]: 'error',
    [NOTIFICATION_CATEGORIES.MARKETING]: 'purple',
    [NOTIFICATION_CATEGORIES.SYSTEM]: 'grey',
    [NOTIFICATION_CATEGORIES.LOGISTICS]: 'teal',
    [NOTIFICATION_CATEGORIES.CUSTOMER_SERVICE]: 'indigo',
  }
  return colors[category] || 'primary'
}

const getPriorityColor = (priority) => {
  const colors = {
    [NOTIFICATION_PRIORITIES.LOW]: 'grey',
    [NOTIFICATION_PRIORITIES.MEDIUM]: 'blue',
    [NOTIFICATION_PRIORITIES.HIGH]: 'orange',
    [NOTIFICATION_PRIORITIES.CRITICAL]: 'red',
  }
  return colors[priority] || 'grey'
}

const getPriorityLabel = (priority) => {
  const labels = {
    [NOTIFICATION_PRIORITIES.LOW]: 'منخفض',
    [NOTIFICATION_PRIORITIES.MEDIUM]: 'متوسط',
    [NOTIFICATION_PRIORITIES.HIGH]: 'عالي',
    [NOTIFICATION_PRIORITIES.CRITICAL]: 'حرج',
  }
  return labels[priority] || 'متوسط'
}

const getBadgeColor = () => {
  if (unreadCount.value > 10) return 'error'
  if (unreadCount.value > 5) return 'warning'
  return 'primary'
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'الآن'
  if (diffMins < 60) return `منذ ${diffMins} دقيقة`
  if (diffHours < 24) return `منذ ${diffHours} ساعة`
  if (diffDays < 7) return `منذ ${diffDays} يوم`
  
  return date.toLocaleDateString('ar-DZ')
}

const handleNotificationClick = async (notification) => {
  // Mark as read
  if (!notification.is_read) {
    await notificationsStore.markAsRead(notification.id)
  }

  // Navigate to action URL if available
  if (notification.action_url) {
    window.location.href = notification.action_url
  }

  menu.value = false
}

const markAllAsRead = async () => {
  isMarkingAllRead.value = true
  try {
    await notificationsStore.markAllAsRead()
  } finally {
    isMarkingAllRead.value = false
  }
}

const deleteNotification = async (notificationId) => {
  await notificationsStore.deleteNotification(notificationId)
}

const refreshNotifications = async () => {
  await notificationsStore.fetchNotifications(true)
}

const viewAllNotifications = () => {
  router.push('/notifications')
  menu.value = false
}

const toggleCategoryFilter = (category) => {
  const newCategory = filters.value.category === category ? null : category
  notificationsStore.setFilters({ category: newCategory })
}

// Lifecycle
onMounted(() => {
  // Initialize the notifications store
  notificationsStore.initialize()
  
  // Listen for custom notification events
  window.addEventListener('notification', handleNewNotification)
})

onUnmounted(() => {
  window.removeEventListener('notification', handleNewNotification)
  notificationsStore.cleanup()
})

const handleNewNotification = (event) => {
  const notification = event.detail
  
  // Show browser notification if page is not visible
  if (document.hidden && 'Notification' in window && Notification.permission === 'granted') {
    new Notification(notification.title, {
      body: notification.message,
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      tag: notification.id,
      requireInteraction: notification.priority === 'critical'
    })
  }
}
</script>

<style scoped>
.notification-bell {
  position: relative;
  transition: all 0.3s ease;
}

.notification-bell.has-notifications {
  animation: bell-ring 2s ease-in-out infinite;
}

@keyframes bell-ring {
  0%, 100% { transform: rotate(0deg); }
  10%, 30%, 50%, 70%, 90% { transform: rotate(-10deg); }
  20%, 40%, 60%, 80% { transform: rotate(10deg); }
}

.notification-dropdown {
  border-radius: 12px;
  overflow: hidden;
}

.notification-item {
  transition: all 0.2s ease;
  cursor: pointer;
}

.notification-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.04);
}

.notification-item.unread {
  background-color: rgba(var(--v-theme-primary), 0.08);
  border-left: 3px solid var(--v-theme-primary);
}

.notification-item.priority-high {
  border-left-color: #ff9800;
}

.notification-item.priority-critical {
  border-left-color: #f44336;
  background-color: rgba(244, 67, 54, 0.08);
}

.unread-indicator {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.notification-item:hover .delete-btn {
  opacity: 1;
}

.v-list-item {
  min-height: 72px;
}
</style>
