console.log('Validate Demo Accounts AMS')


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
            Account: "demo_la_distributor@pproap.com",
            Language: "LAR Spanish",
            Login: null,
            Attribute: [
                "Formal Characteristics Agreement T1 Partner",
                "Channel Data Collection Platform Access",
                "Deal registration access to Aruba Deal Reg Tool",
                "myCompoptimzer Access",
                "Order Status Tool Access",
                "Partner Dynamic Syndication",
                "pComm Access",
                "Physical Claims Access",
                "Sales Builder Windows Access",
                "Simplified Configuration Experience Access",
                "SPT Capability Deal Registration",
                "SPT Capability Joint Business Planning",
                "SPT Capability Leads & Opportunity",
                "SPT Capability Market Development Funds",
                "SPT Capability NGQ",
                "T1 Order Status and Returns",
                "Standard Pricing Viewer Access"
            ],
            UserRight: [
                "Channel_Data_Collection_Platform_Access",
                "G_ARUBA_Deal_Registration_Partner_Company_Admin",
                "G_ARUBA_HP_Deal_Registration_Partner_Admin",
                "G_ARUBA_HP_Deal_Registration_Partner_User",
                "G_My_Comp_Viewer_Pilot",
                "G_PARTNER_DYNAMIC_SYND",
                "G_PC_PHY_CLAIMS_PARTNER_USER",
                "G_SPT_Services360_Pro_Base_Access_T1",
                "G_PRP_DXP_GO",
                "G_SPT_HP_Deal_Registration_Partner_Admin",
                "G_SPT_HP_Deal_Registration_Partner_Company_Admin",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_MDF_Partner_User",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Admin",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Company_Admin",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_NGQ_Partner_User",
                "G_UPP_Partner_Admin_User",
                "G_UPP_Partner_User",
                "MANAGE_TRAINING_OF_EMPLOYEES",
                "MANAGE_TRAINING_OF_EMPLOYEES_BACKUP",
                "Order Status",
                "Order Status with Net Pricing",
                "Order Status with Pricing",
                "T1_ORDER_STATUS_AND_RETURNS_WITH_PRICING",
                "T1_ORDER_STATUS_VISIBILITY",
            ],
            Geo: "Mexico",
            BR: "Distributor",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=J82wzbjGMiEEgYicvScyiw%3D%3D&doAsUserLanguageId=es_ES&p_p_auth=4VjnPuuP",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_distributor_lar@pproap.com",
            Language: "Portuguese (Brazilian)",
            Login: null,
            Attribute: [
                "Formal Characteristics Agreement T1 Partner",
                "Channel Data Collection Platform Access",
                "Deal registration access to Aruba Deal Reg Tool",
                "myCompoptimzer Access",
                "Order Status Tool Access",
                "Partner Dynamic Syndication",
                "pComm Access",
                "Physical Claims Access",
                "Sales Builder Windows Access",
                "Simplified Configuration Experience Access",
                "SPT Capability Deal Registration",
                "SPT Capability Joint Business Planning",
                "SPT Capability Leads & Opportunity",
                "SPT Capability Market Development Funds",
                "SPT Capability NGQ",
                "T1 Order Status and Returns",
                "Standard Pricing Viewer Access",
            ],
            UserRight: [
                "Channel_Data_Collection_Platform_Access",
                "G_ARUBA_Deal_Registration_Partner_Company_Admin",
                "G_ARUBA_HP_Deal_Registration_Partner_Admin",
                "G_ARUBA_HP_Deal_Registration_Partner_User",
                "G_My_Comp_Viewer_Pilot",
                "G_PARTNER_DYNAMIC_SYND",
                "G_PC_PHY_CLAIMS_PARTNER_USER",
                "G_SPT_Services360_Pro_Base_Access_T1",
                "G_PRP_DXP_GO",
                "G_SPT_HP_Deal_Registration_Partner_Admin",
                "G_SPT_HP_Deal_Registration_Partner_Company_Admin",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_MDF_Partner_User",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Admin",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Company_Admin",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_NGQ_Partner_User",
                "G_UPP_Partner_Admin_User",
                "G_UPP_Partner_User",
                "MANAGE_TRAINING_OF_EMPLOYEES",
                "MANAGE_TRAINING_OF_EMPLOYEES_BACKUP",
                "Order Status",
                "Order Status with Net Pricing",
                "Order Status with Pricing",
                "T1_ORDER_STATUS_AND_RETURNS_WITH_PRICING",
                "T1_ORDER_STATUS_VISIBILITY",
            ],
            Geo: "Brazil",
            BR: "Distributor",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=6%2BcwfmRE5ALp1r8XjeZrwQ%3D%3D&doAsUserLanguageId=pt_BR&p_p_auth=4VjnPuuP",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_la_platinum@pproap.com",
            Language: "LAR Spanish",
            Login: null,
            Attribute: [
                "Partner Ready Platinum Partner",
                "PR for Ntwkg Platinum Partner",
                "Formal Characteristics Agreement T2 Partner",
                "Channel Data Collection Platform Access",
                "myCompoptimzer Access",
                "Order Status Tool Access",
                "Partner Dynamic Syndication",
                "pComm Access",
                "Physical Claims Access",
                "Sales Builder Windows Access",
                "Simplified Configuration Experience Access",
                "SPT Capability Deal Registration",
                "SPT Capability Joint Business Planning",
                "SPT Capability Leads & Opportunity",
                "SPT Capability Market Development Funds",
                "SPT Capability NGQ",
                "Standard Pricing Viewer Access",
                "T2 Order Status and Returns"
            ],
            UserRight: [
                "Channel_Data_Collection_Platform_Access",
                "G_PARTNER_DYNAMIC_SYND",
                "G_PC_PHY_CLAIMS_PARTNER_USER",
                "G_PRP_DXP_GO",
                "G_SPT_HP_Deal_Registration_Partner_Admin",
                "G_SPT_HP_Deal_Registration_Partner_Company_Admin",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_MDF_Partner_User",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Admin",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Company_Admin",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_NGQ_Partner_User",
                "G_UPP_Partner_Admin_User",
                "G_UPP_Partner_User",
                "MANAGE_TRAINING_OF_EMPLOYEES",
                "MANAGE_TRAINING_OF_EMPLOYEES_BACKUP",
                "Order Status",
                "Order Status with Net Pricing",
                "Order Status with Pricing",
                "T2_ORDER_STATUS_VISIBILITY",
            ],
            Geo: "Mexico",
            BR: "T2 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=NOkDHAg4U3fomPmUxzvtbQ%3D%3D&doAsUserLanguageId=es_ES&p_p_auth=4VjnPuuP",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_hpelarptbr_01@pproap.com",
            Language: "Portuguese (Brazilian)",
            Login: null,
            Attribute: [
                "Partner Ready Platinum Partner",
                "PR for Ntwkg Platinum Partner",
                "Formal Characteristics Agreement T2 Partner",
                "Channel Data Collection Platform Access",
                "myCompoptimzer Access",
                "Order Status Tool Access",
                "Partner Dynamic Syndication",
                "pComm Access",
                "Physical Claims Access",
                "Sales Builder Windows Access",
                "Simplified Configuration Experience Access",
                "SPT Capability Deal Registration",
                "SPT Capability Joint Business Planning",
                "SPT Capability Leads & Opportunity",
                "SPT Capability Market Development Funds",
                "SPT Capability NGQ",
                "Standard Pricing Viewer Access",
                "T2 Order Status and Returns"
            ],
            UserRight: [
                "Channel_Data_Collection_Platform_Access",
                "G_PARTNER_DYNAMIC_SYND",
                "G_PC_PHY_CLAIMS_PARTNER_USER",
                "G_PRP_DXP_GO",
                "G_SPT_HP_Deal_Registration_Partner_Admin",
                "G_SPT_HP_Deal_Registration_Partner_Company_Admin",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_MDF_Partner_User",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Admin",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Company_Admin",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_NGQ_Partner_User",
                "G_UPP_Partner_User",
                "MANAGE_TRAINING_OF_EMPLOYEES",
                "MANAGE_TRAINING_OF_EMPLOYEES_BACKUP",
                "Order Status",
                "Order Status with Net Pricing",
                "Order Status with Pricing",
                "T2_ORDER_STATUS_VISIBILITY"
            ],
            Geo: "Brazil",
            BR: "T2 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=ycWVuGi58auOfEiiqj5KSQ%3D%3D&doAsUserLanguageId=pt_BR&p_p_auth=4VjnPuuP",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_na_distributor@pproap.com",
            Language: "English",
            Login: null,
            Attribute: [
                "Formal Characteristics Agreement T1 Partner",
                "Channel Data Collection Platform Access",
                "Deal registration access to Aruba Deal Reg Tool",
                "myCompoptimzer Access",
                "Order Status Tool Access",
                "Partner Dynamic Syndication",
                "pComm Access",
                "Physical Claims Access",
                "Sales Builder Windows Access",
                "Simplified Configuration Experience Access",
                "SPT Capability Deal Registration",
                "SPT Capability Joint Business Planning",
                "SPT Capability Leads & Opportunity",
                "SPT Capability Market Development Funds",
                "SPT Capability NGQ",
                "T1 Order Status and Returns",
                "Standard Pricing Viewer Access",
                "Aruba Distributor",
                "Aruba Portal Experience",
                "Distribution Partner Portal Experience"
            ],
            UserRight: [
                "Channel_Data_Collection_Platform_Access",
                "G_ARUBA_Deal_Registration_Partner_Company_Admin",
                "G_ARUBA_HP_Deal_Registration_Partner_Admin",
                "G_ARUBA_HP_Deal_Registration_Partner_User",
                "G_My_Comp_Viewer_Pilot",
                "G_PARTNER_DYNAMIC_SYND",
                "G_PC_PHY_CLAIMS_PARTNER_USER",
                "G_SPT_Services360_Pro_Base_Access_T1",
                "G_PRP_DXP_GO",
                "G_SPT_HP_Deal_Registration_Partner_Admin",
                "G_SPT_HP_Deal_Registration_Partner_Company_Admin",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_MDF_Partner_User",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Admin",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Company_Admin",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_NGQ_Partner_User",
                "G_UPP_Partner_Admin_User",
                "G_UPP_Partner_User",
                "MANAGE_TRAINING_OF_EMPLOYEES",
                "MANAGE_TRAINING_OF_EMPLOYEES_BACKUP",
                "Order Status",
                "Order Status with Net Pricing",
                "Order Status with Pricing",
                "T1_ORDER_STATUS_AND_RETURNS_WITH_PRICING",
                "T1_ORDER_STATUS_VISIBILITY"
            ],
            Geo: "United States",
            BR: "Distributor",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=KdHUigiz4YwD30izfyMySg%3D%3D&doAsUserLanguageId=en_US&p_p_auth=4VjnPuuP",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "test_ntwkg_gold@pproap.com",
            Language: "English",
            Login: null,
            Attribute: [
                "Unmanaged Partner Portal Experience",
                "Aruba Portal Experience",
                "Standard Pricing Viewer Access",
                "HP Co-Marketing Zone Access",
                "pComm Access",
                "GPP Global Partner Catalog Access",
                "PC_SEEL",
                "Proposal Web Access",
                "myCompoptimzer Access",
                "C3T Access",
                "PC_AIRHEADS",
                "PC_ARUBA_CENTRAL",
                "PC_ARUBAPEDIA",
                "PR for Ntwkg Gold Wireless LAN Specialist",
                "Benefits Statement Access",
                "myCompoptimzer2 Access",
                "CompOptimizer2 Pilot",
                "NA 100000 - Please DO NOT ALTER or Use",
                "Aruba Customer Success COE Candidate",
                "Aruba Managed Services COE CAN",
                "Aruba Professional Services COE Candidate"
            ],
            UserRight: [
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_PRP_DXP_GO"
            ],
            Geo: "Canada",
            BR: "Commercial Traditional Dealer",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=wGzPvzDPu%2BfSl57%2F8nm%2FVw%3D%3D&doAsUserLanguageId=en_US&p_p_auth=4VjnPuuP",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_unmanaged@pproap.com",
            Language: "English",
            Login: null,
            Attribute: [
                "Unmanaged Partner Portal Experience",
                "SPT Capability Market Development Funds",
                "NA 100000 - Please DO NOT ALTER or Use"
            ],
            UserRight: [
                "G_UPP_Partner_User",
                "G_SPT_Partner_Care_User",
                "Benefit Statement - US",
                "G_My_Comp_Viewer_Pilot",
                "G_PRP_DXP_GO"
            ],
            Geo: "United States",
            BR: "Commercial Traditional Dealer",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=gjAykRa9VfYzCSEShQjIfw%3D%3D&doAsUserLanguageId=en_US&p_p_auth=4VjnPuuP",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_na_platinum@pproap.com",
            Language: "English",
            Login: null,
            Attribute: [
                "Partner Ready Platinum Partner",
                "PR for Ntwkg Platinum Partner",
                "Formal Characteristics Agreement T2 Partner",
                "Channel Data Collection Platform Access",
                "myCompoptimzer Access",
                "Order Status Tool Access",
                "Partner Dynamic Syndication",
                "pComm Access",
                "Physical Claims Access",
                "Sales Builder Windows Access",
                "Simplified Configuration Experience Access",
                "SPT Capability Deal Registration",
                "SPT Capability Joint Business Planning",
                "SPT Capability Leads & Opportunity",
                "SPT Capability Market Development Funds",
                "SPT Capability NGQ",
                "Standard Pricing Viewer Access",
                "T2 Order Status and Returns"
            ],
            UserRight: [
                "Channel_Data_Collection_Platform_Access",
                "G_PARTNER_DYNAMIC_SYND",
                "G_PC_PHY_CLAIMS_PARTNER_USER",
                "G_PRP_DXP_GO",
                "G_SPT_HP_Deal_Registration_Partner_Admin",
                "G_SPT_HP_Deal_Registration_Partner_Company_Admin",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_MDF_Partner_User",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Admin",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Company_Admin",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_NGQ_Partner_User",
                "G_UPP_Partner_Admin_User",
                "G_UPP_Partner_User",
                "MANAGE_TRAINING_OF_EMPLOYEES",
                "MANAGE_TRAINING_OF_EMPLOYEES_BACKUP",
                "Order Status",
                "Order Status with Net Pricing",
                "Order Status with Pricing",
                "T2_ORDER_STATUS_VISIBILITY"
            ],
            Geo: "United States",
            BR: "T2 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=N7zmbB5RZCzlJ69%2FcZ%2FLuQ%3D%3D&doAsUserLanguageId=en_US&p_p_auth=4VjnPuuP",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_competitor@pproap.com",
            Language: "English",
            Login: null,
            Attribute: [
                "Unmanaged Partner Portal Experience",
                "pComm Access",
                "SPT Capability Joint Business Planning",
                "SPT Capability Market Development Funds",
                "myCompoptimzer Access",
                "SPT Capability Leads & Opportunity",
                "Channel Data Collection Platform Access",
                "SPT Capability NGQ",
                "SPT Capability Deal Registration",
                "Deal registration access to Aruba Deal Reg Tool",
                "T1 Order Status and Returns",
                "Competitor Onboarding",
                "Order Status Tool Access",
                "AMS Global Rebates Suite Access",
                "Competitor Alcatel"
            ],
            UserRight: [
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "Order Status",
                "Order Status with Pricing",
                "Order Status with Net Pricing",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_MDF_Partner_User",
                "Benefit Statement - US",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Admin",
                "G_ARUBA_HP_Deal_Registration_Partner_User",
                "G_My_Comp_Viewer_Pilot",
                "Channel_Data_Collection_Platform_Access",
                "G_SPT_NGQ_Partner_User",
                "T1_ORDER_STATUS_VISIBILITY",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Admin_Training",
                "G_ARUBA_HP_Deal_Registration_Partner_Admin",
                "T1_ORDER_STATUS_AND_RETURNS_WITH_PRICING",
                "G_PRP_DXP_GO"
            ],
            Geo: "United States",
            BR: "Commercial Traditional Dealer",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=fYhYVk%2B8xH5ZkVdkrBMmwA%3D%3D&doAsUserLanguageId=en_US&p_p_auth=4VjnPuuP",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_aruba@pproap.com",
            Language: "English",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Channel Data Collection Platform Access",
                "Deal registration access to Aruba Deal Reg Tool",
                "Formal Characteristics Agreement T2 Partner",
                "My HP Leads and Opportunities Access",
                "myCompoptimzer Access",
                "P1 Metals Partner Portal Experience",
                "Partner Dynamic Syndication",
                "Partner Ready Platinum Partner",
                "pComm Access",
                "PR for Ntwkg Platinum Partner",
                "Sales Builder Windows Access",
                "Simplified Configuration Experience Access",
                "SPT Capability Deal Registration",
                "SPT Capability Joint Business Planning",
                "SPT Capability Leads & Opportunity",
                "SPT Capability Market Development Funds",
                "SPT Capability NGQ",
                "Standard Pricing Viewer Access",
                "T2 Order Status and Returns",
                "Aruba Distributor",
                "Aruba Customer Success COE Candidate",
                "Aruba Managed Services COE CAN",
                "Aruba Professional Services COE Candidate"
            ],
            UserRight: [
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_UPP_Partner_Admin_User",
                "MANAGE_TRAINING_OF_EMPLOYEES",
                "MANAGE_TRAINING_OF_EMPLOYEES_BACKUP",
                "Order Status",
                "Order Status with Pricing",
                "Order Status with Net Pricing",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_MDF_Partner_User",
                "Benefit Statement - US",
                "G_SPT_BMI_Partner_User",
                "G_ARUBA_HP_Deal_Registration_Partner_User",
                "G_My_Comp_Viewer_Pilot",
                "G_PARTNER_DYNAMIC_SYND",
                "Channel_Data_Collection_Platform_Access",
                "G_UPP_Pilot_User",
                "G_SPT_NGQ_Partner_User",
                "G_ARUBA_Deal_Registration_Partner_Company_Admin",
                "G_PRfN_Pilot_User",
                "G_ARUBA_HP_Deal_Registration_Partner_Admin",
                "T2_ORDER_STATUS_VISIBILITY",
                "G_PRP_DXP_GO"
            ],
            Geo: "United States",
            BR: "T2 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=GqByQT%2FMUtTebEnitSq3GQ%3D%3D&doAsUserLanguageId=en_US&p_p_auth=4VjnPuuP",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_oem@pproap.com",
            Language: "English",
            Login: null,
            Attribute: [
                "OEM Distribution Partner",
                "OEM Integrator Partner",
                "OEM Partner Portal Experience",
                "Order Status Tool Access",
                "Partner Dynamic Syndication",
                "SPT Capability Market Development Funds",
                "SPT Capability NGQ",
                "Sales Builder Windows Access",
                "Simplified Configuration Experience Access",
                "Standard Pricing Viewer Access",
                "Channel Data Collection Platform Access",
                "Formal Characteristics Agreement T1 Partner",
                "pComm Access",
                "T1 Order Status and Returns"
            ],
            UserRight: [
                "Channel_Data_Collection_Platform_Access",
                "G_PARTNER_DYNAMIC_SYND",
                "G_SPT_MDF_Partner_User",
                "G_SPT_NGQ_Partner_User",
                "G_UPP_Partner_User",
                "Order Status",
                "Order Status with Net Pricing",
                "Order Status with Pricing",
                "G_PRP_DXP_GO",
                "T1_ORDER_STATUS_AND_RETURNS_WITH_PRICING",
                "T1_ORDER_STATUS_VISIBILITY"
            ],
            Geo: "United States",
            BR: "OEM Distributor",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=kDbzzzY2cTuZEkhXBjf9Pw%3D%3D&doAsUserLanguageId=en_US&p_p_auth=4VjnPuuP",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_msa@pproap.com",
            Language: "English",
            Login: null,
            Attribute: [
                "Unmanaged Partner Portal Experience",
                "SPT Capability Market Development Funds",
                "SPT Capability Deal Registration",
                "Partner Dynamic Syndication",
                "MSA Vendor Portal Experience",
                "MDF Business Planning Access",
                "MDF Access",
                "MindTickle Learning",
                "EXCLUDE_DUMMY_PARTNER"
            ],
            UserRight: [
                "G_UPP_Partner_User",
                "G_UPP_Partner_Admin_User",
                "G_SPT_MDF_Partner_User",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_PARTNER_DYNAMIC_SYND",
                "G_PRP_DXP_GO"
            ],
            Geo: "United States",
            BR: "MDF Agency",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=s3nnosE%2B9vhI8l%2B%2BEBOYrA%3D%3D&doAsUserLanguageId=en_US&p_p_auth=4VjnPuuP",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_na_proximity@pproap.com",
            Language: "English",
            Login: null,
            Attribute: [
                "Unmanaged Partner Portal Experience",
                "SPT Capability Market Development Funds",
                "NA 100000 - Please DO NOT ALTER or Use"
            ],
            UserRight: [
                "G_UPP_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_PRP_DXP_GO"
            ],
            Geo: "United States",
            BR: "Commercial Traditional Dealer",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=6%2BA8zsD7aT9stwfA6aLjlA%3D%3D&doAsUserLanguageId=en_US&p_p_auth=4VjnPuuP",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_technology@yopmail.com",
            Language: "English",
            Login: null,
            Attribute: [
                "Alliance Portal experience",
                "PRfTP Server Integrity NonStop",
                "PRfTP Storage BU",
                "PRfTP IS Composable Infrastructure",
                "PRfTP Server Rack Tower Blade DO",
                "PRfTP IS OpenNFV",
                "PRfTP IS ConvergedSystem",
                "PRfTP Server for IoT",
                "PRfTP Server Integrity Servers HP-UX",
                "PRfTP IS Helion OpenStack",
                "PRfTP IS IoT",
                "PRfTP Server Integrity Superdome X",
                "PRfTP IS Digital Services Aggregation",
                "PRfTP Networking BU",
                "PRfTP Platinum Level"
            ],
            UserRight: [
                "G_UPP_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_UPP_Partner_Admin_User",
                "G_PRP_DXP_GO",
                "G_SPT_MDF_Partner_User",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_PARTNER_DYNAMIC_SYND"
            ],
            Geo: "United States",
            BR: "Technology Partner",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=oDnHh7H8qC0XqVw3CMJEqA%3D%3D&doAsUserLanguageId=en_US&p_p_auth=fObZxLIQ",
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
            //ToList: "kalaivanan.a@hpe.com;mohammed.imran4@hpe.com",
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
            if (lang == 'es-ES') {
                lang = 'LAR Spanish';
            } else if (lang == 'pt-BR') {
                lang = 'Portuguese (Brazilian)';
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
                    if (lang == 'es-ES') {
                        lang = 'LAR Spanish';
                    } else if (lang == 'pt-BR') {
                        lang = 'Portuguese (Brazilian)';
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