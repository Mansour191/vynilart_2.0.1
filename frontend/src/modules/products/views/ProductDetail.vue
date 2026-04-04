<template>
  <div class="product-detail">
    <v-container v-if="loading" class="py-16">
      <v-row justify="center">
        <v-col cols="12" md="8">
          <v-card>
            <v-card-text class="pa-8">
              <div class="text-center">
                <v-progress-circular
                  indeterminate
                  color="warning"
                  size="64"
                ></v-progress-circular>
                <div class="mt-4">
                  <h3 class="text-h5">{{ $t('loading') }}</h3>
                  <p class="text-body-1">{{ $t('loadingProduct') }}</p>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-alert
      v-else-if="error"
      type="error"
      prominent
      class="ma-4"
    >
      <v-alert-title>{{ $t('error') }}</v-alert-title>
      {{ error }}
    </v-alert>

    <!-- Product Content -->
    <v-container v-else-if="product">
      <v-row>
        <v-col cols="12" md="6">
          <v-card elevation="2" class="rounded-3xl pa-4">
            <v-img
              :src="mainProductImage?.imageUrl || '/placeholder-product.jpg'"
              :alt="mainProductImage?.altText || product?.nameAr || 'Product Image'"
              height="420"
              class="rounded-2xl"
              cover
            >
              <template #placeholder>
                <v-skeleton-loader type="image"></v-skeleton-loader>
              </template>
              
              <!-- Stock Status Badge -->
              <div class="position-absolute top-2 left-2">
                <v-chip
                  :color="stockStatus === 'in_stock' ? 'success' : stockStatus === 'low_stock' ? 'warning' : 'error'"
                  variant="elevated"
                  size="small"
                >
                  {{ stockStatusText }}
                </v-chip>
              </div>
              
              <!-- Discount Badge -->
              <div v-if="discountPercentage > 0" class="position-absolute top-2 right-2">
                <v-chip
                  color="error"
                  variant="elevated"
                  size="small"
                >
                  {{ discountLabel }}
                </v-chip>
              </div>
            </v-img>
          </v-card>
        </v-col>

        <v-col cols="12" md="6">
          <v-card elevation="4" class="rounded-3xl pa-6 pa-md-8 sticky top-24">
            <v-card-text>
              <!-- Product Title and Price -->
              <div class="mb-6">
                <h1 class="text-h3 font-weight-bold mb-2">{{ product.nameAr || product.nameEn }}</h1>
                <p class="text-body-1 text-medium-emphasis mb-4">{{ product.descriptionAr || product.descriptionEn }}</p>
                
                <!-- Price with Discount -->
                <div class="mb-4">
                  <div v-if="discountPercentage > 0" class="d-flex align-center gap-2 mb-2">
                    <span class="text-h3 font-weight-black text-warning">
                      {{ formatPrice(priceBreakdown.finalPrice) }}
                    </span>
                    <span class="text-body-2 text-medium-emphasis text-decoration-line-through">
                      {{ formatPrice(priceBreakdown.basePrice) }}
                    </span>
                    <v-chip color="error" variant="elevated" size="small">
                      -{{ discountPercentage }}%
                    </v-chip>
                  </div>
                  <div v-else class="text-h3 font-weight-black text-warning">
                    {{ formatPrice(priceBreakdown.basePrice) }}
                  </div>
                </div>
              </div>

              <!-- Product Tags -->
              <div class="d-flex flex-wrap gap-2 mb-4">
                <v-chip
                  v-for="tag in product.tags"
                  :key="tag"
                  variant="outlined"
                  color="grey-lighten-2"
                  size="small"
                  class="text-none"
                >
                  {{ tag }}
                </v-chip>
              </div>

              <!-- Product Actions -->
              <div class="d-flex gap-3 mb-6">
                <v-btn
                  color="warning"
                  size="large"
                  prepend-icon="mdi-cart-plus"
                  :disabled="!canAddToCartComputed"
                  :loading="loading"
                  @click="addToCart"
                  block
                >
                  {{ canAddToCartComputed ? ($t('addToCart') || 'أضف للسلة') : (stockStatus === 'out_of_stock' ? ($t('outOfStock') || 'نفد المخزون') : ($t('insufficientStock') || 'مخزون غير كافي')) }}
                </v-btn>
                
                <v-btn
                  color="success"
                  size="large"
                  prepend-icon="mdi-whatsapp"
                  :href="`https://wa.me/213663140341?text=${encodeURIComponent(($t('productInquiry') || 'استفسار عن المنتج') + ': ' + (product.nameAr || product.nameEn))}`"
                  target="_blank"
                  rel="noopener noreferrer"
                  variant="outlined"
                >
                  {{ $t('inquire') || 'استفسار' }}
                </v-btn>
              </div>
              
              <!-- Quantity Selector -->
              <div class="mb-6">
                <h3 class="text-subtitle-1 font-weight-bold mb-3">{{ $t('quantity') || 'الكمية' }}</h3>
                <div class="d-flex align-center gap-2">
                  <v-btn
                    icon="mdi-minus"
                    variant="outlined"
                    :disabled="quantity <= 1"
                    @click="decrementQuantity"
                  />
                  <v-text-field
                    v-model="quantity"
                    type="number"
                    min="1"
                    :max="currentStock"
                    variant="outlined"
                    density="compact"
                    class="flex-grow-0"
                    style="width: 80px"
                    hide-details
                  />
                  <v-btn
                    icon="mdi-plus"
                    variant="outlined"
                    :disabled="quantity >= currentStock"
                    @click="incrementQuantity"
                  />
                </div>
                <div class="text-caption text-medium-emphasis mt-1">
                  {{ $t('availableStock') || 'المخزون المتاح' }}: {{ currentStock }}
                  <span v-if="selectedVariant" class="ms-2">
                    ({{ $t('variant') || 'تنوع' }}: {{ selectedVariant.name }})
                  </span>
                </div>
              </div>

              <!-- Product Details -->
              <div class="product-details mb-6">
                <h3 class="text-h6 font-weight-bold mb-3">{{ $t('productDetails') }}</h3>
                <v-row>
                  <v-col cols="6" class="mb-3">
                    <div class="text-caption text-medium-emphasis">{{ $t('category') }}</div>
                    <div class="text-body-2">{{ product.category }}</div>
                  </v-col>
                  <v-col cols="6" class="mb-3">
                    <div class="text-caption text-medium-emphasis">{{ $t('material') }}</div>
                    <div class="text-body-2">
                      <v-chip
                        v-if="selectedMaterial"
                        :color="selectedMaterial.isPremium ? 'warning' : 'primary'"
                        variant="elevated"
                        size="small"
                      >
                        {{ getMaterialName(selectedMaterial) }}
                      </v-chip>
                      <span v-else>{{ $t('selectMaterial') || 'اختر المادة' }}</span>
                    </div>
                  </v-col>
                  <v-col cols="6" class="mb-3">
                    <div class="text-caption text-medium-emphasis">{{ $t('dimensions') }}</div>
                    <div class="text-body-2">{{ product.dimensions }}</div>
                  </v-col>
                  <v-col cols="6" class="mb-3">
                    <div class="text-caption text-medium-emphasis">{{ $t('weight') }}</div>
                    <div class="text-body-2">{{ product.weight }}</div>
                  </v-col>
                </v-row>
              </div>

              <!-- AI Smart Measurement -->
              <div class="ai-measurement mb-6">
                <h3 class="text-h6 font-weight-bold mb-3">{{ $t('aiSmartMeasurement') }}</h3>
                <v-text-field
                  v-model="referenceDimension"
                  type="number"
                  :label="$t('referenceDimension')"
                  variant="outlined"
                  color="warning"
                  min="10"
                  class="mb-3"
                ></v-text-field>
                <v-file-input
                  accept="image/*"
                  :label="$t('uploadImage')"
                  variant="outlined"
                  color="warning"
                  prepend-icon="mdi-camera"
                  @change="onImageChange"
                  class="mb-3"
                ></v-file-input>
                <v-btn
                  @click="runSmartMeasurement"
                  color="warning"
                  variant="tonal"
                  prepend-icon="mdi-brain"
                  :loading="aiLoading"
                  :disabled="!aiImageFile"
                  block
                >
                  {{ aiLoading ? $t('calculating') : $t('calculateWithAI') }}
                </v-btn>
              </div>

              <!-- AI Results -->
              <div v-if="aiResults" class="ai-results mb-6">
                <h3 class="text-h6 font-weight-bold mb-3">{{ $t('measurementResults') }}</h3>
                <v-alert type="success" variant="tonal">
                  <div class="mb-2">
                    <strong>{{ $t('estimatedArea') }}:</strong> {{ aiResults.area }} m²
                  </div>
                  <div>
                    <strong>{{ $t('estimatedPrice') }}:</strong> {{ formatPrice(aiResults.price) }}
                  </div>
                </v-alert>
              </div>

              <!-- Material Selection -->
              <div class="material-selection mb-6">
                <ProductMaterialSelector
                  v-if="currentProduct && hasAvailableMaterials(currentProduct)"
                  :product="currentProduct"
                  :dimensions="productDimensions"
                  :quantity="quantity"
                  @material-selected="onProductMaterialSelected"
                  @price-change="onProductMaterialPriceChange"
                />
                <MaterialSelector
                  v-else
                  v-model="selectedMaterial"
                  :dimensions="productDimensions"
                  :quantity="quantity"
                  @price-update="onPriceUpdate"
                />
              </div>

              <!-- Variant Selection -->
              <div v-if="currentProduct?.variants?.length > 0" class="variant-selection mb-6">
                <VariantSelector
                  :product="currentProduct"
                  :show-price-comparison="true"
                  @variant-selected="onVariantSelected"
                  @price-change="onVariantPriceChange"
                />
              </div>

              <!-- Shipping Info -->
              <div class="shipping-info mb-6">
                <h3 class="text-h6 font-weight-bold mb-3">{{ $t('shippingInfo') }}</h3>
                <v-row>
                  <v-col cols="6" class="mb-3">
                    <div class="text-caption text-medium-emphasis">{{ $t('deliveryTime') }}</div>
                    <div class="text-body-2">{{ product.deliveryTime }}</div>
                  </v-col>
                  <v-col cols="6" class="mb-3">
                    <div class="text-caption text-medium-emphasis">{{ $t('shippingCost') }}</div>
                    <div class="text-body-2">{{ formatPrice(product.shippingCost) }}</div>
                  </v-col>
                </v-row>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useStore } from 'vuex';
import { useI18n } from 'vue-i18n';
import { useProductDetails } from '@/composables/useProductDetails';
import { useMaterials } from '@/composables/useMaterials';
import MaterialSelector from '@/shared/components/MaterialSelector.vue';
import ProductMaterialSelector from '@/shared/components/ProductMaterialSelector.vue';
import VariantSelector from '@/shared/components/VariantSelector.vue';

const route = useRoute();
const router = useRouter();
const store = useStore();
const { t } = useI18n();

// Composables
const { 
  getProductBySlug, 
  selectProduct, 
  isInStock, 
  getStockStatus, 
  getStockStatusText,
  canAddToCart,
  updateQuantity,
  incrementQuantity,
  decrementQuantity,
  getMainImage,
  getAllImages,
  formatPrice,
  formatDimensions,
  getDiscountPercentage,
  getDiscountLabel,
  loadRelatedProducts,
  // Product Materials
  getAvailableMaterials,
  hasAvailableMaterials,
  calculateProductMaterialPrice,
  formatMaterialName,
  currentProduct,
  selectedVariant,
  selectedImage,
  quantity,
  priceBreakdown,
  loading: productLoading,
  error: productError
} = useProductDetails();

const { getMaterialName, calculateTotalPrice } = useMaterials();

// Reactive data
const loading = ref(true);
const error = ref(null);
const product = ref(null);
const selectedMaterial = ref(null);
const productDimensions = ref({ width: 100, height: 100 });
const calculatedPrice = ref(0);
const referenceDimension = ref(null);
const aiImageFile = ref(null);
const aiLoading = ref(false);
const aiResults = ref(null);

// Computed
const productId = computed(() => route.params.id);
const productSlug = computed(() => route.params.slug || route.params.id);
const finalPrice = computed(() => {
  if (currentProduct.value) {
    return priceBreakdown.value.totalCost;
  }
  return 0;
});

const stockStatus = computed(() => {
  if (currentProduct.value) {
    // Use variant stock if variant is selected, otherwise use product stock
    return getStockStatus(currentProduct.value, selectedVariant.value);
  }
  return 'out_of_stock';
});

const stockStatusText = computed(() => {
  return getStockStatusText(stockStatus.value);
});

const currentStock = computed(() => {
  if (selectedVariant.value) {
    return selectedVariant.value.stock || 0;
  }
  return currentProduct.value?.stock || 0;
});

const canAddToCartComputed = computed(() => {
  return canAddToCart(currentProduct.value, selectedVariant.value, quantity.value);
});

const discountPercentage = computed(() => {
  if (currentProduct.value) {
    return getDiscountPercentage(currentProduct.value);
  }
  return 0;
});

const discountLabel = computed(() => {
  if (currentProduct.value) {
    return getDiscountLabel(currentProduct.value);
  }
  return '';
});

const productImages = computed(() => {
  if (currentProduct.value) {
    return getAllImages(currentProduct.value);
  }
  return [];
});

const mainProductImage = computed(() => {
  if (selectedImage.value) {
    return selectedImage.value;
  }
  if (currentProduct.value) {
    return getMainImage(currentProduct.value);
  }
  return null;
});

// Methods
const fetchProduct = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    // Use GraphQL composable instead of REST API
    const { result, loading: queryLoading, error: queryError } = getProductBySlug(productSlug.value);
    
    // Wait for the query to complete
    if (queryLoading.value) {
      return;
    }
    
    if (queryError.value) {
      throw new Error(queryError.value.message);
    }
    
    const productsData = result.value?.products?.edges;
    if (productsData && productsData.length > 0) {
      const productData = productsData[0].node;
      
      // Select the product using the composable
      selectProduct(productData);
      product.value = productData;
      
      // Load related products
      if (productData.category?.id) {
        await loadRelatedProducts(productData.category.id, productData.id);
      }
      
      console.log('✅ Product loaded via GraphQL:', product.value);
    } else {
      throw new Error('Product not found');
    }
  } catch (err) {
    console.error('❌ Error fetching product:', err);
    error.value = t('productNotFound') || 'المنتج غير موجود';
  } finally {
    loading.value = false;
  }
};

const onPriceUpdate = (newPrice) => {
  calculatedPrice.value = newPrice;
  console.log('💰 Material price updated:', newPrice);
};

const onImageChange = (event) => {
  aiImageFile.value = event.target.files[0];
  aiResults.value = null;
};

const runSmartMeasurement = async () => {
  if (!aiImageFile.value || !referenceDimension.value) return;
  
  aiLoading.value = true;
  aiResults.value = null;
  
  try {
    // Mock AI measurement calculation
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const area = (productDimensions.value.width * productDimensions.value.height) / 10000; // Convert to m²
    const basePrice = currentProduct.value?.basePrice || 0;
    const materialPrice = selectedMaterial.value ? 
      calculateTotalPrice(selectedMaterial.value, productDimensions.value, quantity.value) : 0;
    
    aiResults.value = {
      area: area.toFixed(2),
      price: basePrice + materialPrice
    };
    
    console.log('✅ AI measurement completed:', aiResults.value);
  } catch (error) {
    console.error('❌ AI measurement error:', error);
  } finally {
    aiLoading.value = false;
  }
};

const addToCart = () => {
  if (!canAddToCartComputed.value) {
    console.warn('⚠️ Cannot add to cart: Product not available or insufficient stock');
    return;
  }
  
  const cartItem = {
    product: currentProduct.value,
    variant: selectedVariant.value,
    material: selectedMaterial.value,
    quantity: quantity.value,
    dimensions: productDimensions.value,
    price: finalPrice.value,
    // Include variant information for proper order preparation
    variantId: selectedVariant.value?.id || null,
    sku: selectedVariant.value?.sku || currentProduct.value.sku || 'N/A',
    variantName: selectedVariant.value?.name || null,
    totalPrice: finalPrice.value
  };
  
  // Dispatch to store
  store.dispatch('cart/addItem', cartItem);
  
  console.log('✅ Added to cart:', cartItem);
  
  // Show success notification
  store.dispatch('notifications/add', {
    type: 'success',
    title: t('addedToCart') || 'تمت الإضافة للسلة',
    message: `${currentProduct.value.nameAr || currentProduct.value.nameEn} ${selectedVariant.value ? `(${selectedVariant.value.name})` : ''} × ${quantity.value}`,
    icon: 'mdi-cart',
    timeout: 3000
  });
};

const selectProductImage = (image) => {
  if (image) {
    selectedImage.value = image;
    console.log('✅ Product image selected:', image);
  }
};

const onVariantSelected = (variant) => {
  console.log('✅ Variant selected in ProductDetail:', variant);
  // Variant selection is handled by useProductDetails composable
};

const onVariantPriceChange = (newPrice) => {
  console.log('💰 Variant price changed:', newPrice);
  // Price breakdown is automatically updated by useProductDetails composable
};

const onProductMaterialSelected = (material) => {
  console.log('✅ Product material selected:', material);
  selectedMaterial.value = material;
  
  // Update price breakdown with material cost
  const materialCost = calculateProductMaterialPrice(
    currentProduct.value,
    material,
    productDimensions.value,
    quantity.value
  );
  updatePriceBreakdown(materialCost);
};

const onProductMaterialPriceChange = (materialCost) => {
  console.log('💰 Product material price changed:', materialCost);
  updatePriceBreakdown(materialCost);
};

// Watchers
watch(() => currentProduct.value, (newProduct) => {
  if (newProduct) {
    product.value = newProduct;
  }
});

watch(() => productDimensions.value, () => {
  if (selectedMaterial.value) {
    onPriceUpdate(calculateTotalPrice(selectedMaterial.value, productDimensions.value, quantity.value));
  }
}, { deep: true });

watch(() => quantity.value, () => {
  if (selectedMaterial.value) {
    onPriceUpdate(calculateTotalPrice(selectedMaterial.value, productDimensions.value, quantity.value));
  }
});

// Initialize
onMounted(() => {
  fetchProduct();
});
</script>

<style scoped>
.product-detail {
  background: var(--bg-surface);
  min-height: 100vh;
}

.sticky {
  position: sticky;
  top: 24px;
}

.ai-measurement,
.ai-results,
.shipping-info {
  background: var(--bg-deep);
  border-radius: 12px;
  padding: 1.5rem;
}

.ai-results .v-alert {
  border-radius: 8px;
}

/* Responsive */
@media (max-width: 960px) {
  .sticky {
    position: static;
    top: 0;
  }
}
</style>
