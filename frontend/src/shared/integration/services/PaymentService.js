/**
 * PaymentService.js
 * خدمة إدارة عمليات الدفع الإلكتروني (SATIM, Edahabia, CIB)
 * تتولى هذه الخدمة الربط مع بوابات الدفع الجزائرية ومحاكاة عملية الدفع
 * بالإضافة إلى إدارة طرق الدفع المحفوظة للمستخدمين
 */

class PaymentService {
  constructor() {
    this.apiEndpoint = import.meta.env.VITE_PAYMENT_API_URL || 'https://api.vinylart.dz/payments';
    this.cache = new Map();
    this.cacheTTL = 5 * 60 * 1000; // 5 دقائق
  }

  /**
   * بدء عملية دفع جديدة
   * @param {Object} paymentData - بيانات الدفع (المبلغ، العملة، معلومات الطلب)
   * @returns {Promise} - نتيجة عملية البدء (رابط التحويل أو معرف المعاملة)
   */
  async initiatePayment(paymentData) {
    console.log('💳 البدء في عملية الدفع:', paymentData);
    
    // محاكاة تأخير الشبكة
    await new Promise(resolve => setTimeout(resolve, 2000));

    // في البيئة الحقيقية، هنا يتم إرسال طلب لـ SATIM للحصول على رابط التحويل (Redirect URL)
    // لمحاكاة النظام، سنفترض النجاح دائماً في هذه المرحلة
    return {
      success: true,
      transactionId: 'TXN-' + Math.random().toString(36).substr(2, 9).toUpperCase(),
      redirectUrl: this.generateMockGatewayUrl(paymentData.method, paymentData.amount),
      message: 'تم تجهيز بوابة الدفع بنجاح'
    };
  }

  /**
   * التحقق من حالة المعاملة بعد عودة المستخدم من البوابة
   * @param {string} transactionId - معرف المعاملة
   * @returns {Promise} - حالة المعاملة (نجاح/فشل)
   */
  async verifyPayment(transactionId) {
    console.log('🔍 التحقق من حالة المعاملة:', transactionId);
    
    await new Promise(resolve => setTimeout(resolve, 1500));

    // محاكاة التحقق من الخادم
    return {
      success: true,
      status: 'PAID',
      paymentDate: new Date().toISOString(),
      receiptNumber: 'RCP-' + Math.floor(Math.random() * 1000000)
    };
  }

  /**
   * توليد رابط محاكاة لبوابة الدفع
   */
  generateMockGatewayUrl(method, amount) {
    const baseUrl = 'https://gateway.satim.dz/simulator';
    return `${baseUrl}?method=${method}&amount=${amount}&callback=${encodeURIComponent(window.location.origin + '/order-success')}`;
  }

  /**
   * معالجة الدفع بالبطاقة البنكية (CIB / Edahabia)
   */
  async processCardPayment(orderData) {
    try {
      const response = await this.initiatePayment({
        amount: orderData.total,
        currency: 'DZD',
        method: orderData.paymentMethod, // 'edahabia' or 'cib'
        orderId: orderData.id,
        customerEmail: orderData.email
      });

      if (response.success) {
        // في التطبيق الحقيقي سنقوم بـ window.location.href = response.redirectUrl;
        // هنا سنحاكي النجاح مباشرة للمستخدم
        console.log('🚀 تحويل المستخدم إلى:', response.redirectUrl);
        return response;
      }
      throw new Error('فشل في بدء عملية الدفع');
    } catch (error) {
      console.error('❌ خطأ في الدفع:', error);
      throw error;
    }
  }

  // ========== وظائف إدارة طرق الدفع المحفوظة ==========

  /**
   * جلب طرق الدفع المحفوظة للمستخدم
   * @returns {Promise<Array>} - قائمة طرق الدفع
   */
  async getPaymentMethods() {
    const cacheKey = 'payment_methods';
    
    if (this._isCacheValid(cacheKey)) {
      return this.cache.get(cacheKey).data;
    }

    try {
      const url = `${this.apiEndpoint}/methods/`;
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this._getAuthToken()}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      const methods = this._transformPaymentMethods(data);
      
      this._setCache(cacheKey, methods);
      return methods;
    } catch (error) {
      console.error('❌ Error fetching payment methods:', error);
      return this.getFallbackPaymentMethods();
    }
  }

  /**
   * إنشاء طريقة دفع جديدة
   * @param {Object} methodData - بيانات طريقة الدفع
   * @returns {Promise<Object>} - طريقة الدفع المحفوظة
   */
  async createPaymentMethod(methodData) {
    try {
      const url = `${this.apiEndpoint}/methods/`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this._getAuthToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(this._preparePaymentMethodData(methodData))
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      const method = this._transformPaymentMethod(data);
      
      // Clear cache to force refresh
      this.cache.delete('payment_methods');
      
      return method;
    } catch (error) {
      console.error('❌ Error creating payment method:', error);
      throw error;
    }
  }

  /**
   * تحديث طريقة دفع موجودة
   * @param {number} id - معرف طريقة الدفع
   * @param {Object} methodData - بيانات التحديث
   * @returns {Promise<Object>} - طريقة الدفع المحدثة
   */
  async updatePaymentMethod(id, methodData) {
    try {
      const url = `${this.apiEndpoint}/methods/${id}/`;
      const response = await fetch(url, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${this._getAuthToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(this._preparePaymentMethodData(methodData))
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      const method = this._transformPaymentMethod(data);
      
      // Clear cache to force refresh
      this.cache.delete('payment_methods');
      
      return method;
    } catch (error) {
      console.error('❌ Error updating payment method:', error);
      throw error;
    }
  }

  /**
   * حذف طريقة دفع
   * @param {number} id - معرف طريقة الدفع
   * @returns {Promise<boolean>} - نجاح العملية
   */
  async deletePaymentMethod(id) {
    try {
      const url = `${this.apiEndpoint}/methods/${id}/`;
      const response = await fetch(url, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this._getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      // Clear cache to force refresh
      this.cache.delete('payment_methods');
      
      return true;
    } catch (error) {
      console.error('❌ Error deleting payment method:', error);
      throw error;
    }
  }

  /**
   * تعيين طريقة الدفع الافتراضية
   * @param {number} id - معرف طريقة الدفع
   * @returns {Promise<boolean>} - نجاح العملية
   */
  async setDefaultPaymentMethod(id) {
    try {
      const url = `${this.apiEndpoint}/methods/${id}/set-default/`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this._getAuthToken()}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      // Clear cache to force refresh
      this.cache.delete('payment_methods');
      
      return true;
    } catch (error) {
      console.error('❌ Error setting default payment method:', error);
      throw error;
    }
  }

  // ========== دوال مساعدة ==========

  /**
   * تحويل بيانات طرق الدفع من الـ API
   */
  _transformPaymentMethods(data) {
    return data.map(method => this._transformPaymentMethod(method));
  }

  /**
   * تحويل طريقة دفع واحدة
   */
  _transformPaymentMethod(method) {
    return {
      id: method.id,
      type: method.type, // 'card', 'bank', 'wallet'
      title: method.title,
      isDefault: method.is_default,
      // Card fields
      cardholderName: method.cardholder_name,
      last4: method.last4,
      expiryMonth: method.expiry_month,
      expiryYear: method.expiry_year,
      // Bank fields
      bankName: method.bank_name,
      accountName: method.account_name,
      accountNumber: method.account_number,
      iban: method.iban,
      // Wallet fields
      walletProvider: method.wallet_provider,
      phoneNumber: method.phone_number,
      createdAt: method.created_at
    };
  }

  /**
   * تجهيز بيانات طريقة الدفع للإرسال إلى الـ API
   */
  _preparePaymentMethodData(methodData) {
    const data = {
      type: methodData.type,
      title: methodData.title,
      is_default: methodData.isDefault || false
    };

    // Add type-specific fields
    if (methodData.type === 'card') {
      data.cardholder_name = methodData.cardholderName;
      data.card_number = methodData.cardNumber;
      data.expiry_month = methodData.expiryMonth;
      data.expiry_year = methodData.expiryYear;
      data.cvv = methodData.cvv;
    } else if (methodData.type === 'bank') {
      data.bank_name = methodData.bankName;
      data.account_name = methodData.accountName;
      data.account_number = methodData.accountNumber;
      data.iban = methodData.iban;
    } else if (methodData.type === 'wallet') {
      data.wallet_provider = methodData.walletProvider;
      data.phone_number = methodData.phoneNumber;
    }

    return data;
  }

  /**
   * بيانات احتياطية لطرق الدفع
   */
  getFallbackPaymentMethods() {
    return [
      {
        id: 1,
        type: 'card',
        title: 'البطاقة الشخصية',
        cardholderName: 'أحمد محمد',
        last4: '1234',
        expiryMonth: '12',
        expiryYear: '25',
        isDefault: true
      },
      {
        id: 2,
        type: 'bank',
        title: 'حساب البنك الوطني',
        bankName: 'البنك الوطني الجزائري',
        accountName: 'أحمد محمد',
        accountNumber: '00789123456789',
        iban: 'DZ86000010000789123456789',
        isDefault: false
      }
    ];
  }

  /**
   * الحصول على توكن المصادقة
   */
  _getAuthToken() {
    // في التطبيق الحقيقي، يتم جلب التوكن من localStorage أو Vuex store
    return localStorage.getItem('authToken') || 'mock-token';
  }

  /**
   * التحقق من صلاحية الكاش
   */
  _isCacheValid(key) {
    const cached = this.cache.get(key);
    return cached && (Date.now() - cached.timestamp < this.cacheTTL);
  }

  /**
   * حفظ البيانات في الكاش
   */
  _setCache(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  /**
   * مسح الكاش
   */
  clearCache() {
    this.cache.clear();
  }
}

export default new PaymentService();
