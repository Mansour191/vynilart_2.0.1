<template>
  <v-card class="shipping-selector" elevation="2">
    <v-card-title class="d-flex align-center pa-4">
      <v-icon color="primary" class="me-2">mdi-truck</v-icon>
      {{ $t('selectShipping') || 'اختر الشحن' }}
    </v-card-title>

    <v-card-text class="pa-4">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-4">
        <v-progress-circular indeterminate color="primary" size="32" />
        <p class="text-body-2 mt-2">{{ $t('loadingShipping') || 'جاري تحميل الشحن...' }}</p>
      </div>

      <!-- Shipping Selection -->
      <div v-else>
        <!-- Wilaya Selection -->
        <v-select
          v-model="selectedWilaya"
          :items="activeZones"
          :label="$t('selectWilaya') || 'اختر الولاية'"
          item-title="nameAr"
          item-value="wilayaId"
          variant="outlined"
          density="compact"
          hide-details
          class="mb-4"
          @update:model-value="onWilayaChange"
        >
          <template v-slot:item="{ props, item }">
            <v-list-item v-bind="props">
              <v-list-item-title>{{ item.raw.nameAr }}</v-list-item-title>
              <v-list-item-subtitle>
                {{ $t('homeDelivery') }}: {{ formatPrice(item.raw.homeDeliveryPrice) }} | 
                {{ $t('stopDesk') }}: {{ formatPrice(item.raw.stopDeskPrice) }}
              </v-list-item-subtitle>
            </v-list-item>
          </template>
        </v-select>

        <!-- Delivery Type Selection -->
        <v-radio-group
          v-if="selectedZone"
          v-model="deliveryType"
          class="delivery-type-group"
          @update:model-value="onDeliveryTypeChange"
        >
          <v-card
            v-for="option in deliveryOptions"
            :key="option.type"
            :class="{ 'delivery-card--selected': deliveryType === option.type }"
            class="delivery-card cursor-pointer mb-2"
            elevation="1"
            @click="deliveryType = option.type"
          >
            <v-card-text class="pa-3">
              <div class="d-flex align-center justify-space-between">
                <div class="d-flex align-center">
                  <v-radio :value="option.type" class="me-3" />
                  <div>
                    <h4 class="text-subtitle-1 font-weight-medium mb-1">
                      {{ option.title }}
                    </h4>
                    <p class="text-caption text-medium-emphasis mb-0">
                      {{ option.description }}
                    </p>
                  </div>
                </div>
                <div class="text-end">
                  <div class="text-primary font-weight-bold">
                    {{ formatPrice(option.price) }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ option.estimatedDays }}
                  </div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-radio-group>

        <!-- Shipping Summary -->
        <v-expand-transition>
          <div v-if="selectedZone && deliveryType" class="shipping-summary mt-4">
            <v-divider class="mb-3" />
            <h4 class="text-subtitle-1 font-weight-bold mb-3">
              {{ $t('shippingSummary') || 'ملخص الشحن' }}
            </h4>
            
            <v-row>
              <v-col cols="12" md="6">
                <div class="mb-2">
                  <span class="text-caption text-medium-emphasis">{{ $t('wilaya') }}:</span>
                  <span class="text-body-2 ms-2">{{ selectedZone.nameAr }}</span>
                </div>
                <div class="mb-2">
                  <span class="text-caption text-medium-emphasis">{{ $t('deliveryType') }}:</span>
                  <span class="text-body-2 ms-2">{{ getDeliveryTypeTitle() }}</span>
                </div>
              </v-col>
              <v-col cols="12" md="6">
                <div class="mb-2">
                  <span class="text-caption text-medium-emphasis">{{ $t('shippingCost') }}:</span>
                  <span class="text-body-2 ms-2 text-primary font-weight-bold">
                    {{ formatPrice(getShippingCost()) }}
                  </span>
                </div>
                <div class="mb-2">
                  <span class="text-caption text-medium-emphasis">{{ $t('estimatedDelivery') }}:</span>
                  <span class="text-body-2 ms-2">{{ getEstimatedDays() }}</span>
                </div>
              </v-col>
            </v-row>
          </div>
        </v-expand-transition>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useShipping } from '@/composables/useShipping';

// Props
const props = defineProps({
  orderTotal: {
    type: Number,
    default: 0
  }
});

// Emits
const emit = defineEmits(['shipping-selected', 'price-change']);

// Composables
const { t } = useI18n();
const {
  activeZones,
  selectedZone,
  deliveryType,
  loading,
  selectShippingZone,
  setDeliveryType,
  calculateTotalWithShipping,
  formatShippingPrice
} = useShipping();

// State
const selectedWilaya = ref(null);

// Computed
const deliveryOptions = computed(() => {
  if (!selectedZone.value) return [];

  return [
    {
      type: 'home_delivery',
      title: t('homeDelivery') || 'توصيل للمنزل',
      description: t('homeDeliveryDesc') || 'التوصيل مباشرة إلى عنوانك',
      price: selectedZone.value.homeDeliveryPrice,
      estimatedDays: '2-3 أيام'
    },
    {
      type: 'stop_desk',
      title: t('stopDesk') || 'نقطة التوقف',
      description: t('stopDeskDesc') || 'الاستلام من نقطة التوقف',
      price: selectedZone.value.stopDeskPrice,
      estimatedDays: '1-2 أيام'
    }
  ];
});

// Methods
const formatPrice = (price) => {
  return formatShippingPrice(price);
};

const getDeliveryTypeTitle = () => {
  const option = deliveryOptions.value.find(opt => opt.type === deliveryType.value);
  return option ? option.title : '';
};

const getShippingCost = () => {
  const option = deliveryOptions.value.find(opt => opt.type === deliveryType.value);
  return option ? option.price : 0;
};

const getEstimatedDays = () => {
  const option = deliveryOptions.value.find(opt => opt.type === deliveryType.value);
  return option ? option.estimatedDays : '';
};

const onWilayaChange = async (wilayaId) => {
  const zone = activeZones.value.find(z => z.wilayaId === wilayaId);
  if (zone) {
    await selectShippingZone(zone);
    emitShippingInfo();
  }
};

const onDeliveryTypeChange = (type) => {
  setDeliveryType(type);
  emitShippingInfo();
};

const emitShippingInfo = () => {
  if (selectedZone.value && deliveryType.value) {
    const shippingInfo = calculateTotalWithShipping(props.orderTotal, selectedZone.value, deliveryType.value);
    emit('shipping-selected', {
      zone: selectedZone.value,
      deliveryType: deliveryType.value,
      ...shippingInfo
    });
    emit('price-change', shippingInfo.total);
  }
};

// Watchers
watch(() => props.orderTotal, () => {
  if (selectedZone.value && deliveryType.value) {
    emitShippingInfo();
  }
});
</script>

<style scoped>
.shipping-selector {
  border-radius: 12px;
}

.delivery-card {
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.delivery-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--v-theme-primary), 0.15);
}

.delivery-card--selected {
  border-color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.05);
}

.delivery-type-group :deep(.v-radio-group) {
  .v-radio {
    display: none;
  }
}

.shipping-summary {
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 8px;
  padding: 16px;
}
</style>
