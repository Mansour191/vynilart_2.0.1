-- =====================================================
-- Shipping System Database Schema for MySQL
-- =====================================================

-- Create shipping methods table
CREATE TABLE IF NOT EXISTS `api_shipping_method` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL COMMENT 'Provider Name',
    `provider` VARCHAR(20) NOT NULL COMMENT 'Provider type',
    `service_type` VARCHAR(20) NOT NULL COMMENT 'Service type (home/desk/express/economy)',
    `expected_delivery_time` INT NOT NULL COMMENT 'Expected delivery time in days',
    `logo` VARCHAR(255) NULL COMMENT 'Logo file path',
    `description` TEXT NULL COMMENT 'Description',
    `tracking_url_template` VARCHAR(500) NULL COMMENT 'Tracking URL template with {tracking_number} placeholder',
    `api_endpoint` VARCHAR(500) NULL COMMENT 'API endpoint for integration',
    `api_key` VARCHAR(100) NULL COMMENT 'API key for external services',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT 'Is the method active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX `idx_provider_service` (`provider`, `service_type`),
    INDEX `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Shipping providers and methods table';

-- Create shipping prices table
CREATE TABLE IF NOT EXISTS `api_shipping_price` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `wilaya_id` INT NOT NULL COMMENT 'Foreign key to shipping table',
    `shipping_method_id` INT NOT NULL COMMENT 'Foreign key to shipping method table',
    `home_delivery_price` DECIMAL(10,2) NOT NULL COMMENT 'Home delivery price',
    `stop_desk_price` DECIMAL(10,2) NOT NULL COMMENT 'Stop desk delivery price',
    `express_price` DECIMAL(10,2) NULL COMMENT 'Express delivery price',
    `free_shipping_minimum` DECIMAL(10,2) NULL COMMENT 'Minimum order for free shipping',
    `weight_surcharge` DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Weight surcharge per kg',
    `volume_surcharge` DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Volume surcharge per cubic meter',
    `cod_available` BOOLEAN DEFAULT TRUE COMMENT 'Cash on delivery available',
    `insurance_available` BOOLEAN DEFAULT FALSE COMMENT 'Insurance available',
    `tracking_available` BOOLEAN DEFAULT TRUE COMMENT 'Tracking available',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT 'Is this price active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY `unique_wilaya_method` (`wilaya_id`, `shipping_method_id`),
    INDEX `idx_wilaya_method` (`wilaya_id`, `shipping_method_id`),
    INDEX `idx_is_active` (`is_active`),
    INDEX `idx_home_price` (`home_delivery_price`),
    INDEX `idx_stop_desk_price` (`stop_desk_price`),
    
    FOREIGN KEY (`wilaya_id`) REFERENCES `core_shipping`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`shipping_method_id`) REFERENCES `api_shipping_method`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Shipping prices linking wilayas with methods';

-- Update existing shipping table to remove old price fields
ALTER TABLE `core_shipping` 
DROP COLUMN `home_delivery_price`,
DROP COLUMN `stop_desk_price`,
DROP COLUMN `express_delivery_price`,
DROP COLUMN `free_shipping_minimum`,
DROP COLUMN `delivery_time_days`;

-- Add organization foreign key to shipping table if not exists
ALTER TABLE `core_shipping` 
ADD COLUMN `base_city_id` INT NULL COMMENT 'Base city organization reference',
ADD INDEX `idx_base_city` (`base_city_id`);

-- Add foreign key constraint for organization (assuming api_organization table exists)
-- ALTER TABLE `core_shipping` 
-- ADD CONSTRAINT `fk_shipping_base_city` 
-- FOREIGN KEY (`base_city_id`) REFERENCES `api_organization`(`id`) 
-- ON DELETE SET NULL;

-- =====================================================
-- Sample Data Insertion
-- =====================================================

-- Insert sample shipping methods
INSERT IGNORE INTO `api_shipping_method` 
(`name`, `provider`, `service_type`, `expected_delivery_time`, `description`, `is_active`) VALUES
('Yalidine Home Delivery', 'yalidine', 'home', 3, 'Yalidine home delivery service', TRUE),
('Yalidine Stop Desk', 'yalidine', 'desk', 2, 'Yalidine stop desk pickup points', TRUE),
('ZR Express Home', 'zr_express', 'home', 2, 'ZR Express home delivery', TRUE),
('ZR Express Desk', 'zr_express', 'desk', 1, 'ZR Express pickup points', TRUE),
('FedEx Standard', 'fedex', 'home', 4, 'FedEx standard delivery', TRUE),
('DHL Express', 'dhl', 'express', 2, 'DHL express delivery', TRUE),
('Local Post', 'local_post', 'economy', 7, 'Local postal service economy delivery', TRUE);

-- Insert sample shipping prices for first few wilayas
INSERT IGNORE INTO `api_shipping_price` 
(`wilaya_id`, `shipping_method_id`, `home_delivery_price`, `stop_desk_price`, `express_price`, `free_shipping_minimum`, `is_active`) 
SELECT 
    s.id as wilaya_id,
    sm.id as shipping_method_id,
    CASE s.wilaya_code 
        WHEN 1 THEN 800.00  -- Algiers
        WHEN 2 THEN 600.00  -- Oran
        WHEN 3 THEN 700.00  -- Tizi Ouzou
        WHEN 16 THEN 900.00 -- Algiers (capital)
        ELSE 650.00
    END as home_delivery_price,
    CASE s.wilaya_code
        WHEN 1 THEN 400.00  -- Algiers
        WHEN 2 THEN 300.00  -- Oran
        WHEN 3 THEN 450.00  -- Tizi Ouzou
        WHEN 16 THEN 500.00 -- Algiers (capital)
        ELSE 350.00
    END as stop_desk_price,
    CASE s.wilaya_code
        WHEN 1 THEN 1200.00 -- Algiers express
        WHEN 16 THEN 1500.00 -- Algiers express
        ELSE 1000.00
    END as express_price,
    CASE s.wilaya_code
        WHEN 1 THEN 5000.00 -- Algiers free shipping minimum
        WHEN 16 THEN 5000.00 -- Algiers free shipping minimum
        ELSE 8000.00
    END as free_shipping_minimum,
    TRUE as is_active
FROM `core_shipping` s
CROSS JOIN `api_shipping_method` sm 
WHERE sm.provider = 'yalidine' 
AND s.wilaya_code IN (1, 2, 3, 16)
AND s.is_active = TRUE
LIMIT 10;

-- =====================================================
-- Views for Common Queries
-- =====================================================

-- Create view for available shipping methods per wilaya
CREATE OR REPLACE VIEW `v_wilaya_shipping_methods` AS
SELECT 
    s.wilaya_id,
    s.wilaya_code,
    s.name_ar as wilaya_name,
    sm.id as shipping_method_id,
    sm.name as shipping_method_name,
    sm.provider,
    sm.service_type,
    sm.expected_delivery_time,
    sm.logo,
    sp.home_delivery_price,
    sp.stop_desk_price,
    sp.express_price,
    sp.free_shipping_minimum,
    sp.cod_available,
    sp.insurance_available,
    sp.tracking_available
FROM `core_shipping` s
JOIN `api_shipping_price` sp ON s.id = sp.wilaya_id
JOIN `api_shipping_method` sm ON sp.shipping_method_id = sm.id
WHERE s.is_active = TRUE 
AND sp.is_active = TRUE 
AND sm.is_active = TRUE;

-- Create view for best shipping prices per service type
CREATE OR REPLACE VIEW `v_best_shipping_prices` AS
SELECT 
    s.wilaya_id,
    s.wilaya_code,
    s.name_ar as wilaya_name,
    'home' as service_type,
    MIN(sp.home_delivery_price) as best_price,
    (SELECT sm.name FROM `api_shipping_method` sm 
     JOIN `api_shipping_price` sp2 ON sm.id = sp2.shipping_method_id 
     WHERE sp2.wilaya_id = s.id AND sp2.home_delivery_price = MIN(sp.home_delivery_price)) as best_provider
FROM `core_shipping` s
JOIN `api_shipping_price` sp ON s.id = sp.wilaya_id
JOIN `api_shipping_method` sm ON sp.shipping_method_id = sm.id
WHERE s.is_active = TRUE 
AND sp.is_active = TRUE 
AND sm.is_active = TRUE
GROUP BY s.id

UNION

SELECT 
    s.wilaya_id,
    s.wilaya_code,
    s.name_ar as wilaya_name,
    'desk' as service_type,
    MIN(sp.stop_desk_price) as best_price,
    (SELECT sm.name FROM `api_shipping_method` sm 
     JOIN `api_shipping_price` sp2 ON sm.id = sp2.shipping_method_id 
     WHERE sp2.wilaya_id = s.id AND sp2.stop_desk_price = MIN(sp.stop_desk_price)) as best_provider
FROM `core_shipping` s
JOIN `api_shipping_price` sp ON s.id = sp.wilaya_id
JOIN `api_shipping_method` sm ON sp.shipping_method_id = sm.id
WHERE s.is_active = TRUE 
AND sp.is_active = TRUE 
AND sm.is_active = TRUE
GROUP BY s.id;

-- =====================================================
-- Indexes for Performance
-- =====================================================

-- Additional indexes for better query performance
CREATE INDEX IF NOT EXISTS `idx_shipping_prices_composite` ON `api_shipping_price` (`wilaya_id`, `is_active`, `home_delivery_price`);
CREATE INDEX IF NOT EXISTS `idx_shipping_methods_composite` ON `api_shipping_method` (`provider`, `service_type`, `is_active`);

-- =====================================================
-- Triggers for Data Integrity
-- =====================================================

DELIMITER //

-- Trigger to validate shipping price uniqueness
CREATE TRIGGER `validate_shipping_price_unique`
BEFORE INSERT ON `api_shipping_price`
FOR EACH ROW
BEGIN
    DECLARE duplicate_count INT;
    
    SELECT COUNT(*) INTO duplicate_count
    FROM `api_shipping_price`
    WHERE `wilaya_id` = NEW.`wilaya_id`
    AND `shipping_method_id` = NEW.`shipping_method_id`;
    
    IF duplicate_count > 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Duplicate shipping price for wilaya and method combination';
    END IF;
END//

DELIMITER ;

-- =====================================================
-- Notes and Comments
-- =====================================================

/*
This schema separates shipping methods from wilayas as requested:

1. api_shipping_method table:
   - Contains shipping providers/companies
   - Includes provider type, service type, delivery time, logo
   - Supports API integration with endpoints and keys
   - Tracks availability and service options

2. api_shipping_price table:
   - Links wilayas with shipping methods
   - Separate pricing for home, desk, and express delivery
   - Supports free shipping minimums and surcharges
   - Tracks service availability (COD, insurance, tracking)

3. Updated core_shipping table:
   - Removed direct pricing fields
   - Added organization base city reference
   - Maintains geographic data

4. Views:
   - v_wilaya_shipping_methods: Complete available options per wilaya
   - v_best_shipping_prices: Best prices per service type

5. Integration points:
   - Frontend can query by wilaya + service type
   - Admin can manage shipping providers separately
   - Pricing is flexible per provider and service type
   - Supports complex pricing rules and surcharges

Usage examples:
-- Get shipping options for wilaya 16 (Algiers)
SELECT * FROM v_wilaya_shipping_methods WHERE wilaya_id = 16;

-- Get best home delivery price for wilaya 16
SELECT * FROM v_best_shipping_prices 
WHERE wilaya_id = 16 AND service_type = 'home';

-- Calculate shipping cost with surcharges
SELECT 
    best_price + (order_weight * weight_surcharge) + (order_volume * volume_surcharge) 
FROM v_best_shipping_prices 
WHERE wilaya_id = 16 AND service_type = 'home';
*/
