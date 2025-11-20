console.log('Validate Demo Accounts')


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
            Account: "demo_h3c@pproap.com",
            Language: "Simplified Chinese",
            Login: null,
            Attribute: [
                "Standard Pricing Viewer Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "Distribution Partner Portal Experience",
                "Sales Builder Windows Access",
                "SPT Capability NGQ",
                "Partner Dynamic Syndication",
                "Order Status Tool Access",
                "Partner Ready Distributor",
                "PRP DXP Access",
                "H3C Company Identifier",
                "T1 Order Status and Return"
            ],
            UserRight: [
                "CBizInfo - Channel Program Reports",
                "Claims and Rebates",
                "EOP Admin",
                "G_GRS_USER_ACCESS",
                "G_My_Comp_Viewer_Pilot",
                "G_PRP_DXP_GO",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_MDF_Partner_User",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_Partner_Care_User",
                "G_UPP_Partner_Admin_User",
                "G_UPP_Partner_User",
                "G_pComm_User",
                "MANAGE_TRAINING_OF_EMPLOYEES",
                "MANAGE_TRAINING_OF_EMPLOYEES_BACKUP",
                "Order Status",
                "Order Status with Net Pricing",
                "Order Status with Pricing",
                "e-Order processing",
                "T1_ORDER_STATUS_AND_RETURNS_WITH_PRICING",
                "T1_ORDER_STATUS_VISIBILITY"

            ],
            Geo: "China",
            BR: "Distributor",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=%2Fzna6646%2BXETkRkxahgAiQ%3D%3D&doAsUserLanguageId=zh_CN&p_p_auth=QTyiGyE2",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_traditional_cn_distributor@pproap.com",
            Language: "Traditional Chinese",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Standard Pricing Viewer Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "Distribution Partner Portal Experience",
                "SPT Capability Market Development Funds",
                "myCompoptimzer Access",
                "Sales Builder Windows Access",
                "C3T Access",
                "SPT Capability NGQ",
                "SPT Capability Deal Registration",
                "T1 Order Status and Returns",
                "Order Status Tool Access",
                "e-Order Processing Access",
                "HP Insight Online Access"
            ],
            UserRight: [

                "Channel_Data_Collection_Platform_Access",
                "Contract AP Price Book with Net Buy Price",
                "EOP Admin",
                "G_My_Comp_Viewer_Pilot",
                "G_SPT_HP_Deal_Registration_Partner_Admin",
                "G_SPT_HP_Deal_Registration_Partner_Company_Admin",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_NGQ_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_UPP_Partner_User",
                "G_pComm_User",
                "MANAGE_TRAINING_OF_EMPLOYEES",
                "MANAGE_TRAINING_OF_EMPLOYEES_BACKUP",
                "Net Buy Price",
                "Order Status",
                "Order Status with Net Pricing",
                "Order Status with Pricing"
            ],
            Geo: "Taiwan",
            BR: "Distributor",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=hGc67YnpQPhX8VAlA5EI3Q%3D%3D&doAsUserLanguageId=zh_TW&p_p_auth=QTyiGyE2",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_indonesian_distributor@pproap.com",
            Language: "Indonesian",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Standard Pricing Viewer Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "Distribution Partner Portal Experience",
                "SPT Capability Joint Business Planning",
                "SPT Capability Market Development Funds",
                "myCompoptimzer Access",
                "Sales Builder Windows Access",
                "SPT Capability Leads & Opportunity",
                "Channel Data Collection Platform Access",
                "C3T Access",
                "SPT Capability NGQ",
                "WW Global Rebates Suites Access",
                "SPT Capability Deal Registration",
                "Deal registration access to Aruba Deal Reg Tool",
                "T1 Order Status and Returns",
                "Partner Dynamic Syndication",
                "Order Status Tool Access",
                "e-Order Processing Access",
                "PR for Ntwkg Branded Support",
                "Partner Ready Distributor Ntwkg",
                "Partner Ready Distributor",
                "Aruba Distributor Accredited"
            ],
            UserRight: [
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_UPP_Partner_Admin_User",
                "G_pComm_User",
                "e-Order processing",
                "Order Status",
                "Order Status with Pricing",
                "Order Status with Net Pricing",
                "T1_ORDER_STATUS_AND_RETURNS_WITH_PRICING",
                "G_PRP_DXP_GO",
                "G_SPT_NGQ_Partner_User",
                "G_ARUBA_HP_Deal_Registration_Partner_User",
                "T1_ORDER_STATUS_VISIBILITY"
            ],
            Geo: "Indonesia",
            BR: "Distributor",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=bQn3GgxZdGg09z42RITv3A%3D%3D&doAsUserLanguageId=en_US&p_p_auth=cVUtClf0",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_japanese_distributor@pproap.com",
            Language: "Japanese",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Standard Pricing Viewer Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "Distribution Partner Portal Experience",
                "SPT Capability Market Development Funds",
                "Sales Builder Windows Access",
                "SPT Capability Leads & Opportunity",
                "Channel Data Collection Platform Access",
                "C3T Access",
                "SPT Capability NGQ",
                "SPT Capability Deal Registration",
                "T1 Order Status and Returns",
                "EG ServiceOne General Info Content",
                "Partner Dynamic Syndication",
                "PRSD Simplivity HW Install and Startup",
                "PRSD Simplivity SW Install and Startup",
                "SIMPLIVITY Company Identifier",
                "PRSD Simplivity HW IS Trainee",
                "ResellerPlus JP Access",
                "Product Availabilty Content",
                "Distributor Partner Content",
                "JP - Partner - DIS Content",
                "JP - Partner - DIS Parent Content",
                "PR for Ntwkg Business Partner",
                "Partner Ready Distributor Ntwkg",
                "Partner Ready Distributor",
                "PRD Select 3PAR HW IS Trainee"
            ],
            UserRight: [
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_UPP_Partner_Admin_User",
                "G_SPT_NGQ_Partner_User",
                "T1_ORDER_STATUS_AND_RETURNS_WITH_PRICING",
                "G_PRP_DXP_GO"
            ],
            Geo: "Japan",
            BR: "Distributor",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=qjVeEG52sRAGnokwi%2FmSKA%3D%3D&doAsUserLanguageId=ja_JP&p_p_auth=0bfLhc21",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_korean_distributor@pproap.com",
            Language: "Korean",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Standard Pricing Viewer Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "Distribution Partner Portal Experience",
                "SPT Capability Joint Business Planning",
                "SPT Capability Market Development Funds",
                "Sales Builder Windows Access",
                "SPT Capability Leads & Opportunity",
                "Channel Data Collection Platform Access",
                "C3T Access",
                "SPT Capability NGQ",
                "WW Global Rebates Suites Access",
                "SPT Capability Deal Registration",
                "PRSD StoreEver Install and Startup",
                "PRSD StoreOnce Break Fix",
                "PRSD StoreVirtual Break Fix",
                "Partner Dynamic Syndication",
                "PRSD Simplivity HW Install and Startup",
                "PRSD Simplivity SW Install and Startup",
                "PRSD Standard Server Break Fix",
                "PRSD StoreEver Break Fix",
                "PRSD StoreVirtual Install and Startup",
                "PRSD Standard Server Install and Startup",
                "PRSD StoreEasy Break Fix",
                "PRSD 3PAR Break Fix",
                "PRSD 3PAR Install and Startup",
                "PRSD EVA Break Fix",
                "PRSD StoreEasy Install and Startup",
                "PRSD Simplivity HW Break Fix",
                "PRSD Nimble Install and Startup",
                "PRSD StoreOnce Install and Startup",
                "PRSD Primera HW IS Trainee",
                "PRSD Apollo Air Cooled BF Trainee",
                "PRSD Edgeline Break Fix",
                "PRSD Primera HW BF Trainee",
                "PRSD Hyper Converged Install and Startup",
                "Order Status Tool Access",
                "e-Order Processing Access",
                "PRSD Moonshot Break Fix",
                "PRSD Moonshot Install and Startup",
                "PRSD Synergy IS Trainee",
                "PRSD Integrity Server Break Fix",
                "PRSD Synergy BF Trainee",
                "PRSD Hyper Converged Break Fix",
                "PRSD Apollo Air Cooled IS Trainee",
                "Partner Ready Distributor",
                "PRSD Integrity Server Install and Startup",
                "PRSD Edgeline Install and Startup",
                "Partner Ready Distributor Ntwkg",
                "PM S1 Service Contract Specialist Partner Distrib",
                "Aruba DCN Distributor",
                "PRD Select EVA BF Trainee"
            ],
            UserRight: [
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_UPP_Partner_Admin_User",
                "Order Status",
                "CBizInfo - Channel Program Reports",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Admin",
                "G_My_Comp_Viewer_Pilot",
                "G_SPT_NGQ_Partner_User",
                "G_PRP_DXP_GO"
            ],
            Geo: "Korea (Rep.)",
            BR: "Distributor",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=l9ealA%2FZrNieSOAKuqTaKA%3D%3D&doAsUserLanguageId=ko_KR&p_p_auth=Ztbnh2yz",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_apj_distributor@pproap.com",
            Language: "English",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Standard Pricing Viewer Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "Order Status Access",
                "Distribution Partner Portal Experience",
                "SPT Capability Joint Business Planning",
                "SPT Capability Market Development Funds",
                "Sales Builder Windows Access",
                "SPT Capability Leads & Opportunity",
                "Channel Data Collection Platform Access",
                "C3T Access",
                "SPT Capability NGQ",
                "WW Global Rebates Suites Access",
                "SPT Capability Deal Registration",
                "T1 Order Status and Returns",
                "Partner Dynamic Syndication",
                "Order Status Tool Access",
                "e-Order Processing Access",
                "APJ Physical Claims Access",
                "Partner Ready Distributor Ntwkg",
                "Partner Ready Distributor",
                "PRP DXP Access"
            ],
            UserRight: [
                "G_UPP_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_SPT_Services360_Pro_Base_Access_T1",
                "G_UPP_Partner_Admin_User",
                "Claims and Rebates",
                "EOP Admin",
                "e-Order processing",
                "Order Status",
                "Order Status with Pricing",
                "Order Status with Net Pricing",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_MDF_Partner_User",
                "G_My_Comp_Viewer_Pilot",
                "G_PARTNER_DYNAMIC_SYND",
                "Channel_Data_Collection_Platform_Access",
                "G_SPT_NGQ_Partner_User",
                "T1_ORDER_STATUS_VISIBILITY",
                "T1_ORDER_STATUS_AND_RETURNS_WITH_PRICING",
                "G_PRP_DXP_GO",
                "G_ARUBA_HP_Deal_Registration_Partner_User",
                "G_GRS_USER_ACCESS",
                "G_User_SaaS_Renewals",
                "G_User_Trial_Create"
            ],
            Geo: "Singapore",
            BR: "Distributor",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=1gDmP8FtU6N3VqX6cxqmXg%3D%3D&doAsUserLanguageId=en_US&p_p_auth=QTyiGyE2",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_simplified_cn_t2solutionprovider@pproap.com",
            Language: "Simplified Chinese",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Formal Characteristics Agreement T2 Partner",
                "pComm Access",
                "T2 Order Status and Returns",
                "C3T Access",
                "Distributor Partner Content",
                "PR for Ntwkg Business Partner",
                "Partner Ready Business Partner"
            ],
            UserRight: [
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_UPP_Partner_Admin_User",
                "Order Status",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_MDF_Partner_User",
                "CBizInfo - Channel Program Reports",
                "G_My_Comp_Viewer_Pilot",
                "T2_ORDER_STATUS_VISIBILITY",
                "G_PRP_DXP_GO"
            ],
            Geo: "China",
            BR: "T2 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=dWb0TmJ0FPhDaI9SNGvPBA%3D%3D&doAsUserLanguageId=zh_CN&p_p_auth=QTyiGyE2",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_traditional_cn_t2solutionprovider@pproap.com",
            Language: "Traditional Chinese",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Formal Characteristics Agreement T2 Partner",
                "Standard Pricing Viewer Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "SPT Capability Joint Business Planning",
                "SPT Capability Market Development Funds",
                "Sales Builder Windows Access",
                "C3T Access",
                "SPT Capability NGQ",
                "SPT Capability Deal Registration",
                "Deal registration access to Aruba Deal Reg Tool",
                "T1 Order Status and Returns",
                "EG ServiceOne General Info Content",
                "PRSD StoreEver Install and Startup",
                "Partner Dynamic Syndication",
                "PRSD Simplivity HW Install and Startup",
                "PRSD Simplivity SW Install and Startup",
                "PRSD Standard Server Break Fix",
                "PRSD StoreEver Break Fix",
                "PRSD Standard Server Install and Startup",
                "PRSD StoreEasy Break Fix",
                "PRSD 3PAR Break Fix",
                "PRSD StoreEasy Install and Startup",
                "PRSD Apollo Air Cooled Break Fix",
                "PRSD StoreOnce Install and Startup",
                "PRSD Apollo Air Cooled Install and Startup",
                "PRSD EVA Install and Startup",
                "PRSD Infra Mgmt SW Install and Startup",
                "Order Status Tool Access",
                "e-Order Processing Access",
                "PBS StoreVirtual Break Fix",
                "PBS StoreOnce Break Fix",
                "Partner Ready Platinum Partner",
                "Partner Ready Gold Services Specialist",
                "Containers on HPE Competency",
                "VMware and HyperV Virtualization on HPE Competency",
                "Containers on HPE Competency",
                "VMware and HyperV Virtualization on HPE Competency",
                "PR for Ntwkg Plat Wireless LAN Specialist"
            ],
            UserRight: [
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "G_UPP_Partner_Admin_User",
                "Order Status",
                "G_PRP_DXP_GO"
            ],
            Geo: "Taiwan",
            BR: "T2 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=91FWtL4bZyyrEB2s2lZn%2Fg%3D%3D&doAsUserLanguageId=zh_TW&p_p_auth=Ztbnh2yz",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_indonesian_id_t2solutionprovider@pproap.com",
            Language: "Indonesian",
            Login: null,
            Attribute: [
                "Standard Pricing Viewer Access",
                "Formal Characteristics Agreement T1 Partner",
                "T2 Order Status and Returns",
                "SPT Capability Joint Business Planning",
                "SPT Capability Market Development Funds",
                "myCompoptimzer Access",
                "Sales Builder Windows Access",
                "SPT Capability Leads & Opportunity",
                "SPT Capability NGQ",
                "WW Global Rebates Suites Access",
                "SPT Capability Deal Registration",
                "Deal registration access to Aruba Deal Reg Tool",
                "EG ServiceOne General Info Content",
                "PRSD StoreEver Install and Startup",
                "Partner Dynamic Syndication",
                "PRSD Simplivity HW Install and Startup",
                "PRSD Simplivity SW Install and Startup",
                "PRSD StoreVirtual Install and Startup",
                "PRSD Standard Server Install and Startup",
                "PRSD StoreEasy Install and Startup",
                "PRSD Synergy Install and Startup",
                "Partner Ready Gold Services Specialist",
                "PRSD Nimble Install and Startup",
                "PRSD Primera HW Install and Startup",
                "PRSD StoreOnce Install and Startup",
                "PRSD EVA Install and Startup",
                "Order Status Tool Access",
                "e-Order Processing Access",
                "PRSD Synergy IS Trainee",
                "APJ Physical Claims Access",
                "PRSD StoreOnce IS Trainee",
                "PR for Ntwkg Plat Wireless LAN Specialist",
                "HP Achieve Plus Access",
                "PRSD Edgeline Install and Startup",
                "PR for Ntwkg Platinum Partner",
                "Partner Ready Platinum Partner"
            ],
            UserRight: [
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "G_UPP_Partner_Admin_User",
                "G_My_Comp_Viewer_Pilot",
                "T2_ORDER_STATUS_VISIBILITY",
                "G_PRP_DXP_GO"
            ],
            Geo: "Indonesia",
            BR: "T2 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=icuHPaOpk6oA%2FzgHo7oCfQ%3D%3D&doAsUserLanguageId=en_US&p_p_auth=HUmz7BVv",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_japanese_jp_t2solutionprovider@pproap.com",
            Language: "Japanese",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Standard Pricing Viewer Access",
                "Formal Characteristics Agreement T1 Partner"
            ],
            UserRight: [
                "G_UPP_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_PRP_DXP_GO"
            ],
            Geo: "Japan",
            BR: "T2 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=cPBQOjDdPSaHKaDgjcsZQQ%3D%3D&doAsUserLanguageId=ja_JP&p_p_auth=QTyiGyE2",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_korean_kr_t2solutionprovider@pproap.com",
            Language: "Korean",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Formal Characteristics Agreement T2 Partner",
                "Standard Pricing Viewer Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "SPT Capability Joint Business Planning",
                "SPT Capability Market Development Funds",
                "myCompoptimzer Access",
                "Sales Builder Windows Access",
                "SPT Capability Leads & Opportunity",
                "C3T Access",
                "SPT Capability NGQ",
                "SPT Capability Deal Registration",
                "Deal registration access to Aruba Deal Reg Tool",
                "EG ServiceOne General Info Content",
                "PRSD StoreEver Install and Startup",
                "PRSD StoreOnce Break Fix",
                "PRSD StoreVirtual Break Fix",
                "Partner Dynamic Syndication",
                "PRSD 3PAR SW Install and Startup",
                "PRSD Simplivity HW Install and Startup",
                "PRSD Simplivity SW Install and Startup",
                "PRSD Standard Server Break Fix",
                "PRSD StoreEver Break Fix",
                "Partner Ready Silver Services Specialist",
                "PRSD StoreVirtual Install and Startup",
                "PRSD Standard Server Install and Startup",
                "PRSD StoreEasy Break Fix",
                "PRSD 3PAR Break Fix",
                "PRSD 3PAR Install and Startup",
                "PRSD EVA Break Fix",
                "PRSD StoreEasy Install and Startup",
                "PRSD Primera HW Break Fix",
                "PRSD Primera SW Install and Startup",
                "PRSD Simplivity HW Break Fix",
                "PRSD Synergy Install and Startup",
                "PRSD Nimble Install and Startup",
                "PRSD Primera HW Install and Startup",
                "PRSD Synergy Break Fix",
                "PRSD Apollo Air Cooled Break Fix",
                "PRSD StoreOnce Install and Startup",
                "PRSD Primera HW IS Trainee",
                "PRSD Apollo Air Cooled Install and Startup",
                "PRSD EVA Install and Startup",
                "PRSD Primera HW BF Trainee",
                "PRSD Infra Mgmt SW Install and Startup",
                "PRSD Converged System Install and Startup",
                "PRSD Moonshot Break Fix",
                "PRSD Moonshot Install and Startup",
                "PRSD Integrity Server Break Fix",
                "PR for Ntwkg Gold Wireless LAN Specialist",
                "PRSD Edgeline BF Trainee",
                "PRSD Integrity Server Install and Startup",
                "PRSD Edgeline IS Trainee",
                "OEM Integrator Partner",
                "PR for Ntwkg Business Partner",
                "PR for Ntwkg Gold Partner",
                "Partner Ready Platinum Partner"
            ],
            UserRight: [
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_UPP_Partner_User",
                "G_SPT_Partner_Care_User",
                "G_UPP_Partner_Admin_User",
                "MANAGE_TRAINING_OF_EMPLOYEES_BACKUP",
                "e-Order processing",
                "Order Status",
                "Order Status with Pricing",
                "Order Status with Net Pricing",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_MDF_Partner_User",
                "G_SPT_HP_Deal_Registration_Partner_Company_Admin",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Company_Admin",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Admin",
                "G_ARUBA_HP_Deal_Registration_Partner_User",
                "G_My_Comp_Viewer_Pilot",
                "G_SPT_HP_Deal_Registration_Partner_Admin",
                "G_ARUBA_Deal_Registration_Partner_Company_Admin",
                "G_ARUBA_HP_Deal_Registration_Partner_Admin",
                "G_PRP_DXP_GO"
            ],
            Geo: "Korea (Rep.)",
            BR: "T2 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=68QfVGOI8KsSp3c0Dbi3KQ%3D%3D&doAsUserLanguageId=ko_KR&p_p_auth=Ztbnh2yz",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demoapjplat@pproap.com",
            Language: "English",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Aruba Professional Services COE Candidate",
                "Standard Pricing Viewer Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "T2 Order Status and Returns",
                "Order Status Access",
                "SPT Capability Joint Business Planning",
                "SPT Capability Market Development Funds",
                "myCompoptimzer Access",
                "Sales Builder Windows Access",
                "SPT Capability Leads & Opportunity",
                "Channel Data Collection Platform Access",
                "C3T Access",
                "SPT Capability NGQ",
                "WW Global Rebates Suites Access",
                "SPT Capability Deal Registration",
                "Deal registration access to Aruba Deal Reg Tool",
                "T1 Order Status and Returns",
                "EG ServiceOne General Info Content",
                "Partner Dynamic Syndication",
                "Partner Ready Gold Partner",
                "Partner Ready Platinum Partner",
                "PR for Ntwkg Platinum Partner",
                "PR Data & Analytics Infrastructure Competency",
                "PR Business Continuity & Data Protection Compt",
                "Order Status Tool Access",
                "e-Order Processing Access",
                "APJ Physical Claims Access",
                "ResellerPlus JP Access",
                "T2 Contracted Partner Content",
                "System Integrator Partner Content",
                "Enterprise Partner Content",
                "Distributor Partner Content",
                "Value Partner Content",
                "PRP DXP Access"
            ],
            UserRight: [
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_UPP_Partner_User",
                "G_SPT_Services360_Pro_Base_Access_T1",
                "G_UPP_Partner_Admin_User",
                "Claims and Rebates",
                "MANAGE_TRAINING_OF_EMPLOYEES_BACKUP",
                "G_PC_PHY_CLAIMS_PARTNER_USER",
                "EOP Admin",
                "e-Order processing",
                "Order Status",
                "Order Status with Pricing",
                "G_SPT_Joint_Business_Planning_User",
                "G_SPT_HP_Deal_Registration_Partner_Company_Admin",
                "G_SPT_HP_Deal_Registration_Partner_User",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Company_Admin",
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_Admin",
                "G_My_Comp_Viewer_Pilot",
                "G_PARTNER_DYNAMIC_SYND",
                "Channel_Data_Collection_Platform_Access",
                "G_SPT_HP_Deal_Registration_Partner_Admin",
                "G_GRS_USER_ACCESS",
                "G_SPT_NGQ_Partner_User",
                "G_ARUBA_Deal_Registration_Partner_Company_Admin",
                "T1_ORDER_STATUS_VISIBILITY",
                "T2_ORDER_STATUS_VISIBILITY",
                "T1_ORDER_STATUS_AND_RETURNS_WITH_PRICING",
                "G_PRP_DXP_GO"
            ],
            Geo: "Singapore",
            BR: "T2 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=OktAeSAdzAqGrx%2FQ8PAhvQ%3D%3D&doAsUserLanguageId=en_US&p_p_auth=HUmz7BVv",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_traditional_cn_competitor@pproap.com",
            Language: "Traditional Chinese",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Formal Characteristics Agreement T2 Partner",
                "pComm Access",
                "SPT Capability Joint Business Planning",
                "SPT Capability Market Development Funds",
                "Sales Builder Windows Access",
                "SPT Capability Leads & Opportunity",
                "C3T Access",
                "SPT Capability Deal Registration",
                "EG ServiceOne General Info Content",
                "Competitor Onboarding",
                "Partner Ready Business Partner EG",
                "HP Achieve Plus Access",
                "Partner Ready Gold Partner",
                "PR for Ntwkg Gold Partner"
            ],
            UserRight: [
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_UPP_Partner_User",
                "G_UPP_Partner_Admin_User",
                "G_PRP_DXP_GO"
            ],
            Geo: "Taiwan",
            BR: "Commercial Traditional Dealer",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=AwP53eAzWWx7eowI3CUjdA%3D%3D&doAsUserLanguageId=zh_TW&p_p_auth=QTyiGyE2",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_japanese_jp_competitor@pproap.com",
            Language: "Japanese",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Formal Characteristics Agreement T2 Partner",
                "Standard Pricing Viewer Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "SPT Capability Market Development Funds",
                "C3T Access",
                "PBS Aruba Break Fix",
                "SPT Capability Deal Registration",
                "Deal registration access to Aruba Deal Reg Tool",
                "T1 Order Status and Returns",
                "SPT Capability Deal Registration T1 Exemption",
                "Competitor Partner",
                "Partner Ready Business Partner EG",
                "ResellerPlus JP Access",
                "System Integrator Partner Content",
                "PBS Partner for Networking",
                "Competitor Partner - EG",
                "Hardware And Services Partner Content",
                "PR for Ntwkg Business Partner",
                "PR for Ntwkg Branded Support",
                "HP Co-Marketing Zone Access",
                "Proposal Web Access",
                "Pay For Performance Access",
                "T2 Contracted Partner Content",
                "PRP DXP pComm Access",
                "PRP DXP eClaims Return Access",
                "PRP DXP Nancy Access",
                "PRP DXP Order Status Access",
                "Literature Ordering Access",
                "Product information for Aruba only partner",
                "Business Partner Candidate for APJ Check Engine",
                "EG Business Partner Candidate",
                "PBS Aruba",
                "EG Business Partner Candidate"

            ],
            UserRight: [
                "G_SPT_S360_Etools_Invoices_Tab",
                "G_SPT_Services360_Pro_Base_Access",
                "G_SPT_Services360_Pro_Base_Access_T1",
                "G_SPT_Services360_Pro_Contact_Management",
                "G_SPT_Services360_Pro_Purchasing",
                "G_SPT_Services360_Pro_Quote_Contract_View",
                "G_SPT_Services360_Pro_Quoting",
                "JP - Contract Net Pricing",
                "G_UPP_Partner_User"
            ],
            Geo: "Japan",
            BR: "T1 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=JDcZcCtnwWpQL8wLgpjEfA%3D%3D&doAsUserLanguageId=ja_JP&p_p_auth=QTyiGyE2",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_simplified_cn_aruba@yopmail.com",
            Language: "Simplified Chinese",
            Login: null,
            Attribute: [
                "Aruba Portal Experience",
                "Formal Characteristics Agreement T2 Partner",
                "Standard Pricing Viewer Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "T2 Order Status and Returns",
                "SPT Capability Market Development Funds",
                "myCompoptimzer Access",
                "C3T Access",
                "WW Global Rebates Suites Access",
                "Deal registration access to Aruba Deal Reg Tool",
                "China Aruba Partners",
                "PR for Ntwkg Platinum Partner",
                "PR for Ntwkg Branded Support"
            ],
            UserRight: [
                "G_UPP_Partner_User",
                "G_UPP_Partner_Admin_User",
                "T2_ORDER_STATUS_VISIBILITY",
                "G_PRP_DXP_GO"
            ],
            Geo: "China",
            BR: "T2 Solution Provider",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=A%2F2%2BE6U1lXe%2BkWMzH3L2%2FQ%3D%3D&doAsUserLanguageId=zh_CN&p_p_auth=DqmWlZNI",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_english_sg_oem@pproap.com",
            Language: "English",
            Login: null,
            Attribute: [
                "Standard Pricing Viewer Access",
                "pComm Access",
                "Formal Characteristics Agreement T1 Partner",
                "SPT Capability Market Development Funds",
                "myCompoptimzer Access",
                "Sales Builder Windows Access",
                "Channel Data Collection Platform Access",
                "C3T Access",
                "OEM Partner Portal Experience",
                "T1 Order Status and Returns",
                "EG ServiceOne General Info Content",
                "Partner Ready Gold Partner",
                "Order Status Tool Access",
                "e-Order Processing Access",
                "OEM T1 Partner"
            ],
            UserRight: [
                "G_UPP_Partner_User",
                "G_UPP_Partner_Admin_User",
                "G_SPT_MDF_Partner_User",
                "G_PRP_DXP_GO"
            ],
            Geo: "Singapore",
            BR: "OEM Account",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=y3X0LOcWvpuoRViUrAvrFA%3D%3D&doAsUserLanguageId=en_US&p_p_auth=na1Iv7Kd",
            LanguageDXP: null,
            BRDXP: null,
            GeoDXP: null,
            AttributeDXP: null,
            UserRightDXP: null
        }, {
            Account: "demo_english_sg_proximity@pproap.com",
            Language: "English",
            Login: null,
            Attribute: [
                "PBS Networking Break Fix"
            ],
            UserRight: [
                "G_SPT_My_HP_Leads_and_Opportunities_Tool_User",
                "G_UPP_Partner_User",
                "G_UPP_Partner_Admin_User",
                "G_PRP_DXP_GO"
            ],
            Geo: "Singapore",
            BR: "Commercial Traditional Dealer",
            Simulation: "https://partner.hpe.com/group/control_panel/manage?p_p_id=com_liferay_my_account_web_portlet_MyAccountPortlet&p_p_lifecycle=0&p_p_state=maximized&doAsUserId=dzxhqhylFoTH6OVtQLMduw%3D%3D&doAsUserLanguageId=en_US&p_p_auth=na1Iv7Kd",
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
            // ToList: "peng.wang3@hpe.com;jingz@hpe.com;jiaojiao.ding@hpe.com;xiaojie.feng@hpe.com;weiwei.shao@hpe.com;ang.gao@hpe.com;taoy@hpe.com",
            //ToList: "pranav-m.bhat@hpe.com"
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
            if (lang == 'zh-CN') {
                lang = 'Simplified Chinese';
            } else if (lang == 'zh-TW') {
                lang = 'Traditional Chinese';
            } else if (lang == 'ja-JP') {
                lang = 'Japanese';
            } else if (lang == 'ko-KR') {
                lang = 'Korean';
            } else if (lang == 'in-ID') {
                lang = 'Indonesian';
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
                    if (lang == 'zh-CN') {
                        lang = 'Simplified Chinese';
                    } else if (lang == 'zh-TW') {
                        lang = 'Traditional Chinese';
                    } else if (lang == 'ja-JP') {
                        lang = 'Japanese';
                    } else if (lang == 'ko-KR') {
                        lang = 'Korean';
                    } else if (lang == 'in-ID') {
                        lang = 'Indonesian';
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

        // if ($('.aui-field-label').length == 7) {
        //     $tempBR = $('.aui-helper-clearfix:eq(0)')
        //     $tempAttrArray = $('.aui-helper-clearfix:eq(4)');
        //     $tempURArray = $('.aui-helper-clearfix:eq(3)');
        //     $tempGeo = $('.aui-helper-clearfix:eq(6)');
        // } else if ($('.aui-field-label').length == 6) {
        //     $tempBR = $('.aui-helper-clearfix:eq(2)')
        //     $tempAttrArray = $('.aui-helper-clearfix:eq(3)');
        //     $tempURArray = $('.aui-helper-clearfix:eq(4)');
        //     $tempGeo = $('.aui-helper-clearfix:eq(5)');
        // } else if ($('.aui-field-label').length == 5) {
        //     $tempBR = $('.aui-helper-clearfix:eq(1)')
        //     $tempAttrArray = $('.aui-helper-clearfix:eq(2)');
        //     $tempURArray = $('.aui-helper-clearfix:eq(3)');
        //     $tempGeo = $('.aui-helper-clearfix:eq(4)');
        // } else if ($('.aui-field-label').length == 4) {
        //     $tempBR = $('.aui-helper-clearfix:eq(0)')
        //     $tempAttrArray = $('.aui-helper-clearfix:eq(1)');
        //     $tempURArray = $('.aui-helper-clearfix:eq(2)');
        //     $tempGeo = $('.aui-helper-clearfix:eq(3)');
        // } else {
        //     window.alert('Account setting section having list not amoung 4-6, please reach out to gechen.wang@hpe.com')
        // }

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