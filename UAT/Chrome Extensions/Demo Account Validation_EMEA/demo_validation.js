console.log('Validate Demo Accounts EMEA')


var pwd = "ExperiencePRP!";


// if localStorage.loginIndex doesn't exist, mean's it's the first time and init the loginIndex as 0
if (!localStorage.loginIndex) {
    var demoAccounts = [
        // Account:"demo_traditional_cn_distributor@pproap.com",
        // Login:"Success",
        // Language:"Traditional Chinese",
        // LanguageDXP:"Traditional Chinese",
        // BR:"Distributor",
        // BRDXP:"Distributor",
        // Geo:"China",
        // GeoDXP:"China",
        // Attribute:"attribute1,attribute2,attribute3,attribute4,attribute5",
        // AttributeDXP:"attribute6,attribute7,attribute8,attribute9,attribute10",
        // UserRight:"userRight1,userRight2,userRight3,userRight4,userRight5",
        // UserRightDXP:"userRight6,userRight7,userRight8,userRight9,userRight10"
        {
            Account: "mapdummypartner@yopmail.com",
            Language: "English",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Formal Characteristics Agreement T2 Partner",
                "Standard Pricing Viewer Access",
                "HP Co-Marketing Zone Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "PDF Partner Catalogue Access",
                "Order Status Access",
                "Bid Guide Access",
                "GPP Global Partner Catalog Access",
                "Distribution Partner Portal Experience",
                "PC_SEEL",
                "Physical Claims Access",
                "Proposal Web Access",
                "HP Incentives and Reward Access",
                "Simplified Configuration Experience Access",
                "SPT Capability Joint Business Planning",
                "Channel Services Network (CSN) Access",
                "SPT Capability Market Development Funds",
                "myCompoptimzer Access",
                "Partner for Growth Access",
                "SPT Capability Leads & Opportunity",
                "Channel Data Collection Platform Access",
                "Stats Access",
                "AP Online Access",
                "C3T Access",
                "Care Pack Central (CPC) Access",
                "Service Partner Authorized Service Delivery Ptnr",
                "SPT Capability Deal Registration",
                "PC_AIRHEADS",
                "PC_ARUBAPEDIA",
                "iQuote Access",
                "T1 Order Status and Returns",
                "HP Insight Online Access",
                "EMEA MAP Program",
                "Special Pricing Reseller A",
                "PRP DXP Access",
                "Aruba Managed Service Provider Candidate"
            ],
            UserRight: [
                "PARTNER_EDUCATION_ACCESS_GRANTED",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "PARTNER_EDUCATION_TC_RENEWAL_REQUIRED",
                "G_SPT_Partner_Care_User",
                "G_UPP_Partner_Admin_User",
                "MANAGE_TRAINING_OF_EMPLOYEES_BACKUP",
                "LOCAL_SECURITY_PhysicalClaims",
                "G_My_Comp_Viewer_Pilot",
                "LOCAL_SECURITY_INCENTIVE_ACCESS",
                "G_HPEGO_Mobile_User_Access",
                "T1_ORDER_STATUS_AND_RETURNS_WITH_PRICING",
                "G_PRP_DXP_GO",
                "G_MDF_Champion_User"
            ],
            Geo: "Croatia",
            BR: "Master Area Partner",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=4yXD52ZkTTpDyQqq3ro2hg%3D%3D&doAsUserLanguageId=en_US&p_p_auth=KbVhya0t",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_hreng_mapt2@yopmail.com",
            Language: "English",
            Login: null,
            Attribute: [
                "AP Online Access",
                "C3T Access",
                "Care Pack Central (CPC) Access",
                "Deal registration access to Aruba Deal Reg Tool",
                "Formal Characteristics Agreement T2 Partner",
                "GPP Global Partner Catalog Access",
                "HP Co-Marketing Zone Access",
                "HP Incentives and Reward Access",
                "HPE Global Partner",
                "HPE Partner Ready for Aruba_ eCommerce",
                "iQuote Access",
                "myCompoptimzer Access",
                "OEM Partner Portal Experience",
                "Order Status Access",
                "P1 Metals Partner Portal Experience",
                "Partner for Growth Access",
                "pComm Access",
                "PDF Partner Catalogue Access",
                "Phoenix Pilot Partner",
                "Proposal Web Access",
                "PRP DXP Access",
                "PRP DXP Nancy Access",
                "PRP DXP Order Status Access",
                "PRP DXP pComm Access",
                "Simplified Configuration Experience Access",
                "Special Pricing Reseller B",
                "SPT Capability Deal Registration",
                "SPT Capability Market Development Funds",
                "SPT Capability NGQ",
                "Standard Pricing Viewer Access",
                "Stats Access",
                "T2 Order Status and Returns",
                "Unmanaged Partner Portal Experience"
            ],
            UserRight: [
                "G_GRS_USER_ACCESS",
                "G_My_Comp_Viewer_Pilot",
                "G_PC_SQ_Partner_User",
                "G_pComm_User",
                "G_PRP_DXP_GO",
                "G_SPT_HP_Deal_Registration_Partner_Company_Admin",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_SPT_HP_Deal_Registration_User_Training",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_MDF_Partner_User",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User_Training",
                "G_SPT_NGQ_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_UPP_Partner_User",
                "LOCAL_SECURITY_INCENTIVE_ACCESS",
                "LOCAL_SECURITY_INCENTIVE_COMPENSATION",
                "LOCAL_SECURITY_INCENTIVE_PARTNER_MGR",
                "LOCAL_SECURITY_INCENTIVE_PROMOTION",
                "LOCAL_SECURITY_INCENTIVE_SELL_WIN",
                "LOCAL_SECURITY_INCENTIVE_SUPPLIES",
                "LOCAL_SECURITY_INCENTIVE_SUPPLIES_PEA",
                "LOCAL_SECURITY_LitwebWithOrderCapabilities",
                "LOCAL_SECURITY_LitwebWithoutOrderCapabilities",
                "LOCAL_SECURITY_OrderStatus",
                "LOCAL_SECURITY_PhysicalClaims",
                "LOCAL_SECURITY_SBD",
                "LOCAL_SECURITY_SmartQuote",
                "PARTNER_EDUCATION_ACCESS_REQUESTED",
                "PARTNER_EDUCATION_TC_RENEWAL_REQUIRED",
                "T1_T2_OSV_Allcomm_Pilot",
                "T2_ORDER_STATUS_VISIBILITY"
            ],
            Geo: "Croatia",
            BR: "OEM Account",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=4UyXPNYQkFMdUwU2DzBTQQ%3D%3D&doAsUserLanguageId=en_US&p_p_auth=KbVhya0t",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_french_solp@yopmail.com",
            Language: "French",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Formal Characteristics Agreement T2 Partner",
                "Standard Pricing Viewer Access",
                "HP Co-Marketing Zone Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "PDF Partner Catalogue Access",
                "T2 Order Status and Returns",
                "Order Status Access",
                "Bid Guide Access",
                "GPP Global Partner Catalog Access",
                "Proposal Web Access",
                "P1 Metals Partner Portal Experience",
                "HP Incentives and Reward Access",
                "Simplified Configuration Experience Access",
                "SPT Capability Joint Business Planning",
                "SPT Capability Market Development Funds",
                "myCompoptimzer Access",
                "EG Partners Distributors MSA Content",
                "Partner for Growth Access",
                "SPT Capability Leads & Opportunity",
                "Stats Access",
                "AP Online Access",
                "C3T Access",
                "Care Pack Central (CPC) Access",
                "SPT Capability NGQ",
                "SPT Capability Deal Registration",
                "Deal registration access to Aruba Deal Reg Tool",
                "SPT Capability Deal Registration T1 Exemption",
                "Smart Quote Access",
                "iQuote Access",
                "Partner Dynamic Syndication",
                "HPE Global Partner",
                "Partner Ready Platinum Hybrid IT Specialist",
                "Special Pricing Reseller B",
                "MindTickle Learning",
                "PRP DXP pComm Access",
                "PRP DXP eClaims Return Access",
                "PRP DXP Nancy Access",
                "PRP DXP Order Status Access",
                "Special Pricing Reseller A",
                "PRP DXP Access",
                "TEST_EA3",
                "Aruba Trial Partner",
                "TEST_EA1",
                "Phoenix Pilot Partner",
                "Partner Ready Platinum Partner",
                "PR for Ntwkg Business Partner",
                "HPE Partner Ready for Aruba_eCommerce"
            ],
            UserRight: [
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "PARTNER_EDUCATION_TC_RENEWAL_REQUIRED",
                "G_SPT_Partner_Care_User",
                "G_SPT_HP_Deal_Registration_User_Training",
                "G_UPP_Partner_Admin_User",
                "LOCAL_SECURITY_OrderStatus",
                "G_SPT_Joint_Business_Planning_User",
                "PARTNER_EDUCATION_ACCESS_REQUESTED",
                "G_ARUBA_HP_Deal_Registration_Partner_User",
                "G_My_Comp_Viewer_Pilot",
                "G_GRS_USER_ACCESS",
                "G_SPT_NGQ_Partner_User",
                "T1_ORDER_STATUS_VISIBILITY",
                "T2_ORDER_STATUS_VISIBILITY",
                "G_PRP_DXP_GO",
                "T1_T2_OSV_Allcomm_Pilot",
                "G_User_SaaS_Renewals"
            ],
            Geo: "France",
            BR: "T2 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=d0rL4yXTp0IWYPQs7y5QIQ%3D%3D&doAsUserLanguageId=fr_FR&p_p_auth=KbVhya0t",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_emea_distributor@pproap.com",
            Language: "German",
            Login: null,
            Attribute: [
                "AP Online Access",
                "Aruba Distributor",
                "ARUBA Portal Experience",
                "ARUBA Trial Partner",
                "Asset Hub Access",
                "Bid Guide Access",
                "C3T Access",
                "Care Pack Central (CPC) Access",
                "Channel Data Collection Platform Access",
                "Deal registration access to Aruba Deal Reg Tool",
                "Distribution Partner Portal Experience",
                "EAF_MTP_1",
                "EG Partners Distributors MSA Content",
                "EU-CRO-1st Tier",
                "Financial Claims Access",
                "Formal Characteristics Agreement T1 Partner",
                "Global Order processing Pilot",
                "GPP Global Partner Catalog Access",
                "HP Co-Marketing Zone Access",
                "HP Incentives and Reward Access",
                "HP Insight Online Access",
                "iQuote Access",
                "MindTickle Learning",
                "myCompoptimzer Access",
                "Order Link Access",
                "Order Status Access",
                "P1 Metals Partner Portal Experience",
                "Partner Dynamic Syndication",
                "Partner for Growth Access",
                "Partner Ready Gold Partner",
                "pComm Access",
                "PDF Partner Catalogue Access",
                "Phoenix Pilot Partner",
                "Physical Claims Access",
                "PRD Select EVA Install and Startup",
                "PRD Select StoreEasy Install and Startup",
                "Proposal Web Access",
                "PRP DXP Access",
                "PRP DXP eClaims Return Access",
                "PRP DXP Nancy Access",
                "PRP DXP Order Status Access",
                "PRP DXP pComm Access",
                "PRSP P1 Business Partner EG Questionnaire",
                "Sales Builder Windows Access",
                "Sell Out Access",
                "Simplified Configuration Experience Access",
                "Smart Quote Access",
                "Special Pricing Reseller A",
                "SPT Capability Deal Registration",
                "SPT Capability Joint Business Planning",
                "SPT Capability Leads & Opportunity",
                "SPT Capability Market Development Funds",
                "SPT Capability NGQ",
                "SPT Capability Services 360",
                "Standard Pricing Viewer Access",
                "Stats Access",
                "StoreFront Migration Manager Access",
                "T1 Order Status and Returns",
                "Top Config Access",
                "Trigger contract signature form(light area) in PRP",
                "WW Global Rebates Suites Access"
            ],
            UserRight: [
                "G_MDF_Champion_User",
                "G_PRP_DXP_GO",
                "G_SPT_Partner_Care_User",
                "G_SPT_Services360_Pro_Base_Access_T1",
                "G_UPP_Partner_Admin_User",
                "G_UPP_Partner_User",
                "G_User_Trial_Create",
                "T1_ORDER_STATUS_VISIBILITY",
                "T1_T2_OSV_Allcomm_Pilot"
            ],
            Geo: "Germany",
            BR: "Distributor",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=HV9fhgSMGWKkMRYAcwtZ9A%3D%3D&doAsUserLanguageId=de_DE&p_p_auth=KbVhya0t",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_emea_platinum@pproap.com",
            Language: "German",
            Login: null,
            Attribute: [
                "Airheads Community",
                "AP Online Access",
                "Aruba Central",
                "ARUBA Portal Experience",
                "ARUBA Trial Partner",
                "Arubapedia",
                "Asset Hub Access",
                "C3T Access",
                "Care Pack Central(CPC) Access",
                "Deal registration access to Aruba Deal Reg Tool",
                "EU_EG_GOLDARU_Q319",
                "EU_EG_PLATARU_Q319",
                "EU_EG_SILVARU_Q319",
                "Financial Claims Access",
                "Formal Characteristics Agreement T1 Partner",
                "Global Order processing Pilot",
                "Gold Hybrid IT Spe Q319",
                "GPP Global Partner Catalog Access",
                "HP Co - Marketing Zone Access",
                "HP Incentives and Reward Access",
                "iQuote Access",
                "Literature Ordering Access",
                "MindTickle Learning",
                "Order Link Access",
                "P1 Deal Reg Access",
                "P1 Metals Partner Portal Experience",
                "Partner Dynamic Syndication",
                "Partner",
                "for Growth Access",
                "Partner Ready Gold Partner",
                "Partner Ready Platinum Partner",
                "Partner Ready Silver Partner",
                "pComm Access",
                "PDF Partner Catalogue Access",
                "Phoenix Pilot Partner",
                "Physical Claims Access",
                "Platinum Hybrid IT Spec Q319",
                "Proposal Web Access",
                "PRP DXP Access",
                "PRP DXP eClaims Return Access",
                "PRP DXP Nancy Access",
                "PRP DXP Order Status Access",
                "PRP DXP pComm Access",
                "SEEL(SE Enablement Lab)",
                "Silver Hybrid IT Spec Q319",
                "Simplified Configuration Experience Access",
                "SPT Capability Big Machines",
                "SPT Capability Deal Registration",
                "SPT Capability NGQ",
                "Stats Access",
                "StoreFront Migration Manager Access",
                "T2 Order Status and Returns",
                "Trigger contract signature form(light area) in PRP"
            ],
            UserRight: [
                "G_ARUBA_HP_Deal_Registration_Partner_User",
                "G_GRS_USER_ACCESS",
                "G_My_Comp_Viewer_Pilot",
                "G_PC_PHY_CLAIMS_PARTNER_USER",
                "G_PRP_DXP_GO",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_NGQ_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_UPP_Partner_User",
                "LOCAL_SECURITY_INCENTIVE_COMPENSATION",
                "PARTNER_EDUCATION_ACCESS_REQUESTED",
                "PARTNER_EDUCATION_TC_RENEWAL_REQUIRED",
                "T1_T2_OSV_Allcomm_Pilot",
                "T2_ORDER_STATUS_VISIBILIT"
            ],
            Geo: "Germany",
            BR: "T2 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=MtKIvQk92mmNK8jnezG%2Btw%3D%3D&doAsUserLanguageId=de_DE&p_p_auth=KbVhya0t",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_italian_distri@yopmail.com",
            Language: "Italian",
            Login: null,
            Attribute: [
                "Formal Characteristics Agreement T1 Partner",
                "Order Status Access",
                "Distribution Partner Portal Experience",
                "Physical Claims Access",
                "Financial Claims Access",
                "HP Incentives and Reward Access",
                "SPT Capability Joint Business Planning",
                "SPT Capability Market Development Funds",
                "Top Config Access",
                "myCompoptimzer Access",
                "Order Link Access",
                "SPT Capability NGQ",
                "SPT Capability Deal Registration",
                "T1 Order Status and Returns",
                "PRSD 3PAR Break Fix",
                "PRP DXP pComm Access",
                "PRP DXP eClaims Return Access",
                "PRP DXP Nancy Access",
                "PRP DXP Order Status Access",
                "EU-CRO-1st Tier",
                "PRP DXP Access",
                "PRSD Integrity Server Proactive Services"
            ],
            UserRight: [
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "PARTNER_EDUCATION_TC_RENEWAL_REQUIRED",
                "G_SPT_Partner_Care_User",
                "G_SPT_HP_Deal_Registration_User_Training",
                "G_UPP_Partner_Admin_User",
                "LOCAL_SECURITY_OrderStatus",
                "G_SPT_Joint_Business_Planning_User",
                "PARTNER_EDUCATION_ACCESS_REQUESTED",
                "G_ARUBA_HP_Deal_Registration_Partner_User",
                "G_GRS_USER_ACCESS",
                "T1_ORDER_STATUS_VISIBILITY"
            ],
            Geo: "Italy",
            BR: "Distributor",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=wrZwPb2adXpV7%2Fwf0VGSrQ%3D%3D&doAsUserLanguageId=it_IT&p_p_auth=KbVhya0t",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        },
        // Missing simulation link
        // {
        //     Account: "dummyt1map@yopmail.com",
        //     Language: "English",
        //     Login: null,
        //     Attribute: [
        //         "Competitor Onboarding",
        //         "EMEA MAP T1 Program"
        //     ],
        //     UserRight: [
        //         "G_SPT_HP_Deal_Registration_Partner_User",
        //         "G_UPP_Partner_User",
        //         "G_SPT_Partner_Care_User",
        //         "G_UPP_Partner_Admin_User",
        //         "MANAGE_TRAINING_OF_EMPLOYEES",
        //         "LOCAL_SECURITY_OrderStatus",
        //         "T1_ORDER_STATUS_VISIBILITY",
        //         "T1_ORDER_STATUS_AND_RETURNS_WITH_PRICING",
        //         "G_PRP_DXP_GO"
        //     ],
        //     Geo: "Lithuania",
        //     BR: "T1 Solution Provider",
        //     Simulation: "",
        //     LanguageDXP: null,
        //     BRDXP: null,
        //     GeoDXP: null,
        //     AttributeDXP: null,
        //     UserRightDXP: null
        // }, 

        {
            Account: "demo_spanisheu_distri@yopmail.com",
            Language: "Spanish",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Standard Pricing Viewer Access",
                "HP Co-Marketing Zone Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "PDF Partner Catalogue Access",
                "Order Status Access",
                "Bid Guide Access",
                "GPP Global Partner Catalog Access",
                "Distribution Partner Portal Experience",
                "Proposal Web Access",
                "P1 Metals Partner Portal Experience",
                "HP Incentives and Reward Access",
                "Simplified Configuration Experience Access",
                "SPT Capability Joint Business Planning",
                "SPT Capability Market Development Funds",
                "myCompoptimzer Access",
                "EG Partners Distributors MSA Content",
                "Partner for Growth Access",
                "SPT Capability Leads & Opportunity",
                "Stats Access",
                "AP Online Access",
                "C3T Access",
                "Care Pack Central (CPC) Access",
                "SPT Capability NGQ",
                "SPT Capability Deal Registration",
                "Deal registration access to Aruba Deal Reg Tool",
                "iQuote Access",
                "T1 Order Status and Returns",
                "Competitor Partner Intelligence",
                "Competitor SAP and BO",
                "PRP DXP pComm Access",
                "PRP DXP eClaims Return Access",
                "PRP DXP Nancy Access",
                "PRP DXP Order Status Access",
                "Special Pricing Reseller A",
                "Nutanix Authorized Distributor",
                "PRP DXP Access",
                "Aruba Trial Partner",
                "Phoenix Pilot Partner",
                "Partner Ready Gold Partner"
            ],
            UserRight: [
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "PARTNER_EDUCATION_TC_RENEWAL_REQUIRED",
                "G_SPT_Partner_Care_User",
                "G_SPT_HP_Deal_Registration_User_Training",
                "G_UPP_Partner_Admin_User",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User_Training",
                "PARTNER_EDUCATION_ACCESS_REQUESTED",
                "G_ARUBA_HP_Deal_Registration_Partner_User",
                "G_PRP_DXP_GO",
                "T1_T2_OSV_Allcomm_Pilot",
                "G_User_SaaS_Renewals_Company_Admin"
            ],
            Geo: "Spain",
            BR: "Distributor",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=DiZl5pD%2BpGWerfu%2FWOjwlw%3D%3D&doAsUserLanguageId=es_ES&p_p_auth=KbVhya0t",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        },

        // Missing simulation link
        // {
        //     Account: "demo_turkish_distri@yopmail.com",
        //     Language: "Turkish",
        //     Login: null,
        //     Attribute: [
        //         "Aruba Portal Experience",
        //         "Formal Characteristics Agreement T2 Partner",
        //         "Standard Pricing Viewer Access",
        //         "HP Co-Marketing Zone Access",
        //         "pComm Access",
        //         "Formal Characteristics Agreement T1 Partner",
        //         "PDF Partner Catalogue Access",
        //         "Order Status Access",
        //         "Bid Guide Access",
        //         "GPP Global Partner Catalog Access",
        //         "Distribution Partner Portal Experience",
        //         "Proposal Web Access",
        //         "P1 Metals Partner Portal Experience",
        //         "HP Incentives and Reward Access",
        //         "Simplified Configuration Experience Access",
        //         "SPT Capability Joint Business Planning",
        //         "SPT Capability Market Development Funds",
        //         "myCompoptimzer Access",
        //         "EG Partners Distributors MSA Content",
        //         "Partner for Growth Access",
        //         "SPT Capability Leads & Opportunity",
        //         "Stats Access",
        //         "AP Online Access",
        //         "C3T Access",
        //         "Care Pack Central (CPC) Access",
        //         "SPT Capability NGQ",
        //         "SPT Capability Deal Registration",
        //         "iQuote Access",
        //         "T1 Order Status and Returns",
        //         "PRP DXP pComm Access",
        //         "PRP DXP eClaims Return Access",
        //         "PRP DXP Nancy Access",
        //         "PRP DXP Order Status Access",
        //         "PRP DXP Access",
        //         "NA 100000 - Please DO NOT ALTER or Use"
        //     ],
        //     UserRight: [
        //         "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
        //         "G_SPT_HP_Deal_Registration_Partner_User",
        //         "G_UPP_Partner_User",
        //         "PARTNER_EDUCATION_TC_RENEWAL_REQUIRED",
        //         "G_SPT_Partner_Care_User",
        //         "G_SPT_HP_Deal_Registration_User_Training",
        //         "G_UPP_Partner_Admin_User",
        //         "MANAGE_TRAINING_OF_EMPLOYEES",
        //         "LOCAL_SECURITY_OrderStatus",
        //         "G_SPT_My_HP_Leads_and_Opportunities_Tool_User_Training",
        //         "PARTNER_EDUCATION_ACCESS_REQUESTED",
        //         "T1_ORDER_STATUS_VISIBILITY",
        //         "G_PRP_DXP_GO",
        //         "T1_T2_OSV_Allcomm_Pilot"
        //     ],
        //     Geo: "Turkey",
        //     BR: "Distributor",
        //     Simulation: "",
        //     LanguageDXP: null,
        //     BRDXP: null,
        //     GeoDXP: null,
        //     AttributeDXP: null,
        //     UserRightDXP: null
        // }, 

        {
            Account: "demo_turkish_solp@yopmail.com",
            Language: "Turkish",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Formal Characteristics Agreement T2 Partner",
                "Standard Pricing Viewer Access",
                "HP Co - Marketing Zone Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "PDF Partner Catalogue Access",
                "Order Status Access",
                "Bid Guide Access",
                "GPP Global Partner Catalog Access",
                "Proposal Web Access",
                "P1 Metals Partner Portal Experience",
                "HP Incentives and Reward Access",
                "Simplified Configuration Experience Access",
                "SPT Capability Joint Business Planning",
                "SPT Capability Market Development Funds",
                "myCompoptimzer Access",
                "EG Partners Distributors MSA Content",
                "Partner for Growth Access",
                "SPT Capability Leads & Opportunity",
                "Stats Access",
                "AP Online Access",
                "C3T Access",
                "Care Pack Central(CPC) Access",
                "SPT Capability NGQ",
                "SPT Capability Deal Registration",
                "Smart Quote Access",
                "iQuote Access",
                "T1 Order Status and Returns",
                "PRP DXP pComm Access",
                "PRP DXP eClaims Return Access",
                "PRP DXP Nancy Access",
                "PRP DXP Order Status Access",
                "PRP DXP Access",
                "TEST_EA3",
                "EAF_MTP_1"
            ],
            UserRight: [
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "PARTNER_EDUCATION_TC_RENEWAL_REQUIRED",
                "G_SPT_Partner_Care_User",
                "G_UPP_Partner_Admin_User",
                "LOCAL_SECURITY_OrderStatus",
                "PARTNER_EDUCATION_ACCESS_REQUESTED",
                "T1_ORDER_STATUS_VISIBILITY",
                "T1_ORDER_STATUS_AND_RETURNS_WITH_PRICING",
                "G_PRP_DXP_GO",
                "T1_T2_OSV_Allcomm_Pilot"
            ],
            Geo: "Turkey",
            BR: "T2 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=iFwQv22xYg0oYIw2Y4bf8w%3D%3D&doAsUserLanguageId=tr_TR&p_p_auth=KbVhya0t",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_ukeng_distri@yopmail.com",
            Language: "English",
            Login: null,
            Attribute: [
                "Unmanaged Partner Portal Experience",
                "Aruba Portal Experience",
                "Standard Pricing Viewer Access",
                "HP Co-Marketing Zone Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "PDF Partner Catalogue Access",
                "Bid Guide Access",
                "GPP Global Partner Catalog Access",
                "Distribution Partner Portal Experience",
                "Proposal Web Access",
                "HP Incentives and Reward Access",
                "Simplified Configuration Experience Access",
                "SPT Capability Joint Business Planning",
                "SPT Capability Market Development Funds",
                "myCompoptimzer Access",
                "EG Partners Distributors MSA Content",
                "Partner for Growth Access",
                "SPT Capability Leads & Opportunity",
                "Stats Access",
                "AP Online Access",
                "C3T Access",
                "Care Pack Central (CPC) Access",
                "SPT Capability NGQ",
                "SPT Capability Deal Registration",
                "SPT Capability Deal Registration T1 Exemption",
                "Smart Quote Access",
                "T1 Order Status and Returns",
                "Competitor Partner Intelligence",
                "PRP DXP pComm Access",
                "PRP DXP eClaims Return Access",
                "PRP DXP Nancy Access",
                "PRP DXP Order Status Access",
                "Special Pricing Reseller A",
                "PRP DXP Access"
            ],
            UserRight: [
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "PARTNER_EDUCATION_TC_RENEWAL_REQUIRED",
                "G_SPT_Partner_Care_User",
                "G_UPP_Partner_Admin_User",
                "LOCAL_SECURITY_INCENTIVE_PARTNER_MGR",
                "G_SPT_MDF_Partner_User",
                "PARTNER_EDUCATION_ACCESS_REQUESTED",
                "G_SPT_NGQ_Partner_User",
                "T1_ORDER_STATUS_AND_RETURNS_WITH_PRICING",
                "G_PRP_DXP_GO",
                "T1_T2_OSV_Allcomm_Pilot"
            ],
            Geo: "Denmark",
            BR: "Distributor",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=zQ7iMRkf0ouPogNbOSRr%2Fw%3D%3D&doAsUserLanguageId=en_US&p_p_auth=KbVhya0t",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_ukeng_proximity@yopmail.com",
            Language: "English",
            Login: null,
            Attribute: [
                "AP Online Access",
                "C3T Access",
                "Care Pack Central (CPC) Access",
                "Deal registration access to Aruba Deal Reg Tool",
                "EG Partners Distributors MSA Content",
                "Formal Characteristics Agreement T1 Partner",
                "Global Order processing Pilot",
                "GPP Global Partner Catalog Access",
                "HP Co-Marketing Zone Access",
                "HP Incentives and Reward Access",
                "HPE Global Partner",
                "iQuote Access",
                "myCompoptimzer Access",
                "P1 Metals Partner Portal Experience",
                "Partner for Growth Access",
                "pComm Access",
                "PDF Partner Catalogue Access",
                "Phoenix Pilot Partner",
                "Proposal Web Access",
                "PRP DXP Access",
                "PRP DXP eClaims Return Access",
                "PRP DXP Nancy Access",
                "PRP DXP Order Status Access",
                "PRP DXP pComm Access",
                "Simplified Configuration Experience Access",
                "Special Pricing Reseller A",
                "Special Pricing Reseller B",
                "SPT Capability Deal Registration T1 Exemption",
                "SPT Capability Joint Business Planning",
                "SPT Capability Leads & Opportunity",
                "SPT Capability Market Development Funds",
                "SPT Capability NGQ",
                "Standard Pricing Viewer Access",
                "Stats Access",
                "T1 Order Status and Returns",
                "T2 Order Status and Returns",
                "Unmanaged Partner Portal Experience"
            ],
            UserRight: [
                "G_PRP_DXP_GO",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_SPT_HP_Deal_Registration_User_Training",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_NGQ_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_UPP_Partner_User",
                "PARTNER_EDUCATION_ACCESS_REQUESTED",
                "PARTNER_EDUCATION_TC_RENEWAL_REQUIRED",
                "T1_ORDER_STATUS_AND_RETURNS_WITH_PRICING",
                "T1_ORDER_STATUS_VISIBILITY",
                "T1_T2_OSV_Allcomm_Pilot",
                "T2_ORDER_STATUS_VISIBILITY"
            ],
            Geo: "United Kingdom",
            BR: "T1 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=SMUNlHUZj5xS5acz3UdgKg%3D%3D&doAsUserLanguageId=en_US&p_p_auth=KbVhya0t",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_ukeng_solp@yopmail.com",
            Language: "English",
            Login: null,
            Attribute: [
                "Unmanaged Partner Portal Experience",
                "Formal Characteristics Agreement T2 Partner",
                "Standard Pricing Viewer Access",
                "HP Co - Marketing Zone Access",
                "pComm Access",
                "PDF Partner Catalogue Access",
                "T2 Order Status and Returns",
                "GPP Global Partner Catalog Access",
                "Proposal Web Access",
                "P1 Metals Partner Portal Experience",
                "HP Incentives and Reward Access",
                "Simplified Configuration Experience Access",
                "SPT Capability Market Development Funds",
                "myCompoptimzer Access",
                "Partner for Growth Access",
                "Stats Access",
                "AP Online Access",
                "C3T Access",
                "Care Pack Central(CPC) Access",
                "SPT Capability NGQ",
                "SPT Capability Deal Registration",
                "Deal registration access to Aruba Deal Reg Tool",
                "SPT Capability Deal Registration T1 Exemption",
                "iQuote Access",
                "T1 Order Status and Returns",
                "HPE Global Partner",
                "Special Pricing Reseller B",
                "PRP DXP pComm Access",
                "PRP DXP eClaims Return Access",
                "PRP DXP Nancy Access",
                "PRP DXP Order Status Access",
                "PRP DXP Access",
                "Aruba Trial Partner",
                "Phoenix Pilot Partner"
            ],
            UserRight: [
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "PARTNER_EDUCATION_TC_RENEWAL_REQUIRED",
                "G_SPT_Partner_Care_User",
                "PARTNER_EDUCATION_ACCESS_REQUESTED",
                "G_ARUBA_HP_Deal_Registration_Partner_User",
                "G_SPT_NGQ_Partner_User",
                "G_PRP_DXP_GO",
                "T1_T2_OSV_Allcomm_Pilot"
            ],
            Geo: "United Kingdom",
            BR: "T2 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=4W0rVo6f1nWUT8OHqsNZmg%3D%3D&doAsUserLanguageId=en_US&p_p_auth=KbVhya0t",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }
    ]
    localStorage.loginIndex = 0; // Index for login validate
    localStorage.profileIndex = 0; // Index for profile compare
    localStorage.demoAccounts = JSON.stringify(demoAccounts); // init demoAccounts as string
    localStorage.fail = 0; // Index for account sign in fail but with no error message appear
}

// **************************************************************
// **************************************************************
// ******************   PUBLIC FUNCTION    **********************
// **************************************************************
// **************************************************************

function login(username, pwd) {
    window.onload = function() {
        var No = parseInt(localStorage.fail);
        No++;
        localStorage.fail = No;
        jQuery('#USER').val(username);
        jQuery('#PASSWORD').val(pwd);
        jQuery('#_com_liferay_login_web_portlet_LoginPortlet_sign-in-btn').click();
    }
}

function logout() {
    location.href = "https://partner.hpe.com/c/portal/logout";
}

function destroy() {
    console.log('destroy')
    localStorage.removeItem('loginIndex');
    localStorage.removeItem('profileIndex');
    localStorage.removeItem('demoAccounts');
    localStorage.removeItem('fail');
}


function email() {
    console.log('email function')

    console.log("demoAccounts:")
    console.log(JSON.parse(localStorage.demoAccounts));

    var tempArray = JSON.parse(localStorage.demoAccounts);
    for (var o = 0; o < tempArray.length; o++) {
        tempArray[o].Attribute = tempArray[o].Attribute.toString();
        tempArray[o].UserRight = tempArray[o].UserRight.toString();
    }
    localStorage.demoAccounts = JSON.stringify(tempArray);

    $.post("https://digital-planning-hub.its.hpecorp.net/Ashx/SendEmailHandler.ashx", {
            Subject: "Demo account validation result " + new Date().toString().substring(4, 15),
            MainText: "Dear Team, <br><br> Please check the validation result as attached <br> <br>Regards",
            //ToList: "somaiah.kodimaniyanda-lava@hpe.com;ragul.subramani@hpe.com;mrunal-v.choure@hpe.com",
            ToList: "pranav-m.bhat@hpe.com;weiwei.shao@hpe.com;ang.gao@hpe.com;kalaivanan.a@hpe.com;ragul.subramani@hpe.com;marina.melcioiu@hpe.com;srividya-d@hpe.com;somaiah.kodimaniyanda-lava@hpe.com;probles@hpe.com;jiaojiao.ding@hpe.com;jingz@hpe.com",
            ExcelText: localStorage.demoAccounts
        },
        function(res) {
            console.log("Request sent for DPH: " + res);
            if (res == 'Success') {
                destroy();
                window.alert('Validation is finished, email sent');
            } else {
                window.alert("Email trigger error, please reach out to gechen.wang@hpe.com. Error: " + res)
            }
        }, 'text');
}

// arr1: demoAccounts default array
// arr2: DXP list array
function codeCompare(arr1, arr2) {
    // var str1 = arr1.toString();
    var str2 = arr2.toString();
    var missingValue = '';
    for (var l = 0; l < arr1.length; l++) {
        if (str2.indexOf(arr1[l]) == -1) {
            // arr1[l] exist in default but missing in DXP, return;
            console.log("exist in default but missing in DXP: " + arr1[l]);
            missingValue += arr1[l] + ',';
        }
    }
    // console.log('missingValue')
    // console.log(missingValue)
    return missingValue.substring(0, missingValue.length - 1);


    // console.log('arr2[m] exist in DXP but missing in default')
    // for(var m =0;m<arr2.length;m++){
    //     if(str1.indexOf(arr2[m]) == -1){
    //         // arr2[m] exist in DXP but missing in default
    //         console.log("exist in DXP but missing in default: " + arr2[m]);
    //     }
    // }
}

function setDemoValue(index, Login, LanguageDXP, BRDXP, GeoDXP, AttributeDXP, UserRightDXP) {
    var tempDemoAccounts = JSON.parse(localStorage.demoAccounts);
    if (Login) {
        tempDemoAccounts[index].Login = Login;
    }
    if (LanguageDXP) {
        tempDemoAccounts[index].LanguageDXP = LanguageDXP;
    }
    if (BRDXP) {
        tempDemoAccounts[index].BRDXP = BRDXP;
    }
    if (GeoDXP) {
        tempDemoAccounts[index].GeoDXP = GeoDXP;
    }
    if (AttributeDXP) {
        tempDemoAccounts[index].AttributeDXP = AttributeDXP;
    }
    if (UserRightDXP) {
        tempDemoAccounts[index].UserRightDXP = UserRightDXP;
    }
    localStorage.demoAccounts = JSON.stringify(tempDemoAccounts);
}



// **************************************************************
// **************************************************************
// *********   DEMO ACCOUNT LOGIN + LANG VALIDATION    **********
// **************************************************************
// **************************************************************

// 5min for 17 accounts

// DEMO LOGIN PAGE not internal login page
if (location.href.indexOf("https://partner.hpe.com/login") > -1 && location.href.indexOf('internal') == -1) {

    // Error appear or Fail 3 times for a account
    if ($('.alert-danger').length || parseInt(localStorage.fail) == 3) {
        // Red alert appear, like pwd not correct. Means the account validation if fail, jump to next one
        // localStorage.fail == 3 means the account login for 3 time, but still couldn't login and no error response, jump to next one
        setDemoValue(parseInt(localStorage.loginIndex), 'False', 'Not applicable', null, null, null, null);
        var No = parseInt(localStorage.loginIndex);
        No++;
        localStorage.loginIndex = No;
        localStorage.fail = 0;
        window.location.href = "https://partner.hpe.com/login";
    }

    // continue to login or jump to internal page
    if (parseInt(localStorage.loginIndex) != JSON.parse(localStorage.demoAccounts).length) {
        login(JSON.parse(localStorage.demoAccounts)[parseInt(localStorage.loginIndex)].Account, pwd);
    } else {
        // email();
        // Demo account login validation is done, jump to internal page
        location.href = "https://partner.hpe.com/group/internal"
    }
}
// DXP HOMEPAGE
if (location.href == "https://partner.hpe.com/group/prp") {
    if (jQuery('#content').length) {
        console.log('Homepage loaded, login success')
        console.log(JSON.parse(localStorage.demoAccounts)[parseInt(localStorage.loginIndex)].Account)
        window.setTimeout(function() {
            var lang = $('html')[0].getAttribute('lang');
            if (lang == 'fr-FR') {
                lang = 'French';
            } else if (lang == 'de-DE') {
                lang = 'German';
            } else if (lang == 'it-IT') {
                lang = 'Italian';
            } else if (lang == 'tr-TR') {
                lang = 'Turkish';
            } else if (lang == 'ru-RU') {
                lang = 'Russian';
            } else if (lang == 'en-US') {
                lang = 'English';
            } else {
                lang = 'Not captured'
            }

            var result = JSON.parse(localStorage.demoAccounts)[parseInt(localStorage.loginIndex)];
            if (lang == result.Language) {
                setDemoValue(parseInt(localStorage.loginIndex), 'Success', ' ', null, null, null, null);
                var No = parseInt(localStorage.loginIndex);
                No++;
                localStorage.loginIndex = No;
                localStorage.fail = 0;
                window.setTimeout(function() {
                    logout();
                }, 5000)
            } else {
                console.log('lang not aligned, check after 5 second')
                    // lang is not the same as default, setup a timeout to wait for the page to fully loaded and capture lang again.
                window.setTimeout(function() {
                    lang = $('html')[0].getAttribute('lang');
                    console.log('lang: ' + lang)
                    if (lang == 'fr-FR') {
                        lang = 'French';
                    } else if (lang == 'de-DE') {
                        lang = 'German';
                    } else if (lang == 'it-IT') {
                        lang = 'Italian';
                    } else if (lang == 'tr-TR') {
                        lang = 'Turkish';
                    } else if (lang == 'ru-RU') {
                        lang = 'Russian';
                    } else if (lang == 'es-ES') {
                        lang = 'Spanish';
                    } else if (lang == 'en-US') {
                        lang = 'English';
                    } else {
                        lang = 'Not captured'
                    }

                    if (lang == result.Language) {
                        lang = ' ';
                    }
                    setDemoValue(parseInt(localStorage.loginIndex), 'Success', lang, null, null, null, null);
                    var No = parseInt(localStorage.loginIndex);
                    No++;
                    localStorage.loginIndex = No;
                    localStorage.fail = 0;
                    window.setTimeout(function() {
                        logout();
                    }, 5000)
                }, 5000)
            }
        }, 5000)
    }
}


// **************************************************************
// **************************************************************
// ******   DEMO ACCOUNT ATTR + UR + GEO + BR VALIDATION    *****
// **************************************************************
// **************************************************************

// 1min for 15 accounts

// INTERNAL LOGIN
// The && in the condition is beacuse the when locaiton.href internal page, the internal login page will auto redirect another link.
if (location.href.indexOf("https://partner.hpe.com/login") > -1 && location.href.indexOf('internal') > -1) {
    window.alert('Please click login and manually input the PIN code')
}

// INTERNAL PAGE
if (location.href == "https://partner.hpe.com/group/internal") {
    window.location.href = JSON.parse(localStorage.demoAccounts)[0].Simulation
}

// Exception that apj Dist demo account logout will jump to belo link
if (location.href == "https://partner.hpe.com/web/internal/login") {
    window.location.href = "https://partner.hpe.com/login"
}

// Account setting page
if (location.href.indexOf("https://partner.hpe.com/group/control_panel") > -1) {
    window.onload = function() {
        var $tempBR; // BR ul element
        var $tempAttrArray; // ATTRIBUTE ul element
        var $tempURArray; // USER RIGHT ul element
        var $tempGeo; // GEO ul element
        for (var l = 0; l < $('.aui-field-label').length; l++) {

            if ($('.aui-field-label:eq(' + l + ')').html() == "BR") {
                $tempBR = $('.aui-helper-clearfix:eq(' + l + ')')
            } else if ($('.aui-field-label:eq(' + l + ')').html() == "User EPI") {
                $tempURArray = $('.aui-helper-clearfix:eq(' + l + ')')
            } else if ($('.aui-field-label:eq(' + l + ')').html() == "Extended Attributes") {
                $tempAttrArray = $('.aui-helper-clearfix:eq(' + l + ')')
            } else if ($('.aui-field-label:eq(' + l + ')').html() == "Geography") {
                $tempGeo = $('.aui-helper-clearfix:eq(' + l + ')')
            }
        }

        var DXPAttrArray = []; // Attr in DXP
        if ($tempAttrArray) {
            for (var j = 0; j < $tempAttrArray.find('li').length; j++) {
                DXPAttrArray.push($tempAttrArray.find('li').find('.aui-textboxlistentry-text')[j].innerText)
            }
            var tempDXPAttrArray = codeCompare(JSON.parse(localStorage.demoAccounts)[parseInt(localStorage.profileIndex)].Attribute, DXPAttrArray)
        }


        var DXPURArray = []; // UR in DXP
        if ($tempURArray) {
            for (var k = 0; k < $tempURArray.find('li').length; k++) {
                DXPURArray.push($tempURArray.find('li').find('.aui-textboxlistentry-text')[k].innerText)
            }
            var tempDXPURArray = codeCompare(JSON.parse(localStorage.demoAccounts)[parseInt(localStorage.profileIndex)].UserRight, DXPURArray)
        }




        if ($tempBR) {
            var tempBRDXP = $tempBR.find('li').find('.aui-textboxlistentry-text')[0].innerText;
            if (tempBRDXP == JSON.parse(localStorage.demoAccounts)[parseInt(localStorage.profileIndex)].BR) {
                tempBRDXP = ' '
            }
        }

        if ($tempGeo) {
            var tempGeoDXP = $tempGeo.find('li').find('.aui-textboxlistentry-text')[0].innerText;
            if (tempGeoDXP == JSON.parse(localStorage.demoAccounts)[parseInt(localStorage.profileIndex)].Geo) {
                tempGeoDXP = ' '
            }
        }


        setDemoValue(parseInt(localStorage.profileIndex), null, null, tempBRDXP, tempGeoDXP, tempDXPAttrArray, tempDXPURArray);

        var No = parseInt(localStorage.profileIndex);
        No++;
        localStorage.profileIndex = No;
        if (parseInt(localStorage.profileIndex) != JSON.parse(localStorage.demoAccounts).length) {
            window.location.href = JSON.parse(localStorage.demoAccounts)[parseInt(localStorage.profileIndex)].Simulation
        } else {
            email();
        }
    }
}