-- 01_create_trusted_benefit_programs.sql
-- Run in Databricks SQL against your NEW hackathon workspace.
-- Primary trusted reference table for the app.

CREATE CATALOG IF NOT EXISTS benefits_navigator;
CREATE SCHEMA IF NOT EXISTS benefits_navigator.trusted;

CREATE OR REPLACE TABLE benefits_navigator.trusted.benefit_programs (
  program_id STRING,
  program_name STRING,
  category STRING,
  description STRING,
  eligibility_summary STRING,
  apply_url STRING,
  apply_phone STRING,
  source_name STRING,
  source_url STRING,
  source_type STRING,
  state STRING,
  active_flag BOOLEAN,
  last_verified_date DATE,
  rule_key STRING,
  income_limit_pct_fpl DOUBLE,
  accepts_undocumented BOOLEAN,
  min_child_age INT,
  max_child_age INT,
  requires_work_or_school BOOLEAN
)
USING DELTA;

DELETE FROM benefits_navigator.trusted.benefit_programs;

INSERT INTO benefits_navigator.trusted.benefit_programs VALUES
('snap', 'NJ SNAP (Supplemental Nutrition Assistance Program)', 'food', 'Monthly food benefits loaded onto an EBT card to buy groceries.', 'Based on household size and gross income (typically up to 130% of federal poverty level).', 'https://www.njhelps.org', NULL, 'NJ SNAP (Supplemental Nutrition Assistance Program)', 'https://www.njhelps.org', 'official_or_reference', 'NJ', true, current_date(), 'snap', 130, false, NULL, NULL, false),
('wic', 'WIC (Women, Infants & Children)', 'food', 'Nutrition program providing food, health referrals, and breastfeeding support for pregnant women, new mothers, and children under 5.', 'Income up to 185% FPL. Must have a child under 5, be pregnant, or recently gave birth.', 'https://www.nj.gov/health/fhs/wic/', NULL, 'WIC (Women, Infants & Children)', 'https://www.nj.gov/health/fhs/wic/', 'official_or_reference', 'NJ', true, current_date(), 'wic', 185, true, 0, 4, false),
('nj_familycare', 'NJ FamilyCare (Medicaid)', 'healthcare', 'Free or low-cost health insurance for eligible NJ residents including children, pregnant women, and families.', 'Children up to 350% FPL. Adults up to 138% FPL. Covers doctor visits, prescriptions, dental, and vision.', 'https://www.state.nj.us/humanservices/dmahs/clients/medicaid/', NULL, 'NJ FamilyCare (Medicaid)', 'https://www.state.nj.us/humanservices/dmahs/clients/medicaid/', 'official_or_reference', 'NJ', true, current_date(), 'nj_familycare', 350, false, NULL, NULL, false),
('chip', 'NJ FamilyCare - CHIP (Children''s Health Insurance)', 'healthcare', 'Low-cost health coverage specifically for children in families who earn too much for Medicaid but can''t afford private insurance.', 'Children up to age 19. Household income up to 350% FPL.', 'https://getcovered.nj.gov', NULL, 'NJ FamilyCare - CHIP (Children''s Health Insurance)', 'https://getcovered.nj.gov', 'official_or_reference', 'NJ', true, current_date(), 'chip', 350, false, 0, 18, false),
('ccdf', 'NJ Child Care Assistance (CCDF / Child Care Subsidy)', 'childcare', 'Subsidizes childcare costs so parents can work or attend school. Covers licensed childcare centers and home daycares.', 'Working families with children under 13. Income up to 200% FPL.', 'https://www.childcarenj.gov', NULL, 'NJ Child Care Assistance (CCDF / Child Care Subsidy)', 'https://www.childcarenj.gov', 'official_or_reference', 'NJ', true, current_date(), 'ccdf', 200, false, 0, 12, true),
('preschool', 'NJ Preschool Education Aid (PEA)', 'childcare', 'Free, high-quality preschool for 3- and 4-year-olds in eligible districts across New Jersey.', 'Must reside in an Abbott or expanded preschool district. No income requirement.', 'https://www.nj.gov/education/ece/', NULL, 'NJ Preschool Education Aid (PEA)', 'https://www.nj.gov/education/ece/', 'official_or_reference', 'NJ', true, current_date(), 'preschool', 999, true, 3, 4, false),
('ga', 'NJ General Assistance (GA)', 'cash', 'Monthly cash assistance for single adults and childless couples who are not eligible for TANF.', 'NJ resident, not receiving other cash assistance. Very limited income/assets.', 'https://www.nj.gov/humanservices/dfd/programs/tanf/', NULL, 'NJ General Assistance (GA)', 'https://www.nj.gov/humanservices/dfd/programs/tanf/', 'official_or_reference', 'NJ', true, current_date(), 'ga', 30, false, NULL, NULL, false),
('tanf', 'NJ WorkFirst (TANF)', 'cash', 'Cash assistance and employment support for families with children. Includes job training and work supports.', 'Families with children under 18. Very low income. Time-limited program.', 'https://www.nj.gov/humanservices/dfd/programs/tanf/', NULL, 'NJ WorkFirst (TANF)', 'https://www.nj.gov/humanservices/dfd/programs/tanf/', 'official_or_reference', 'NJ', true, current_date(), 'tanf', 50, false, NULL, NULL, false),
('liheap', 'Low Income Home Energy Assistance (LIHEAP)', 'cash', 'Helps eligible NJ households pay heating and cooling bills and may cover emergency energy needs.', 'Income up to 60% of state median income. Apply during open enrollment periods.', 'https://www.njhelps.org', NULL, 'Low Income Home Energy Assistance (LIHEAP)', 'https://www.njhelps.org', 'official_or_reference', 'NJ', true, current_date(), 'liheap', 150, false, NULL, NULL, false),
('211nj', 'NJ 2-1-1 Helpline', 'family', 'Free, 24/7 information and referral service connecting NJ residents to local health and human services.', 'Available to all NJ residents regardless of income or status.', 'https://www.nj211.org', NULL, 'NJ 2-1-1 Helpline', 'https://www.nj211.org', 'official_or_reference', 'NJ', true, current_date(), '211nj', 999, true, NULL, NULL, false),
('ece_home_visit', 'Nurse-Family Partnership / Home Visiting Programs', 'family', 'Free home visits by trained nurses and social workers for first-time, low-income mothers from pregnancy through age 2.', 'First-time mothers, low income, enrolled before 28 weeks of pregnancy.', 'https://www.nj.gov/humanservices/dfd/programs/familysupport/', NULL, 'Nurse-Family Partnership / Home Visiting Programs', 'https://www.nj.gov/humanservices/dfd/programs/familysupport/', 'official_or_reference', 'NJ', true, current_date(), 'ece_home_visit', 185, true, NULL, NULL, false),
('dv_services', 'NJ Domestic Violence Services', 'family', 'Emergency shelter, legal assistance, counseling, and safety planning for survivors of domestic violence.', 'Available to all survivors regardless of income, status, or gender.', 'https://www.nj.gov/dcf/women/domestic/', NULL, 'NJ Domestic Violence Services', 'https://www.nj.gov/dcf/women/domestic/', 'official_or_reference', 'NJ', true, current_date(), 'dv_services', 999, true, NULL, NULL, false);

SELECT COUNT(*) AS total_programs
FROM benefits_navigator.trusted.benefit_programs;

SELECT category, COUNT(*) AS program_count
FROM benefits_navigator.trusted.benefit_programs
GROUP BY category
ORDER BY category;
